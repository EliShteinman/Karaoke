import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import NotFoundError
from elasticsearch.helpers import async_bulk, async_scan

logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self, es: AsyncElasticsearch, index_name: str):
        self.es = es
        self.index_name = index_name

    async def initialize_index(
        self, index_name: str = None, mapping: dict = None
    ) -> None:
        """Initialize the Elasticsearch index with proper mapping"""
        index_name = index_name or self.index_name
        try:
            await self.es.indices.delete(index=index_name, ignore_unavailable=True)
            index_exists = await self.es.indices.exists(index=index_name)
            if not index_exists:
                logger.info(f"Creating index {index_name}")
                if mapping:
                    await self.es.indices.create(
                        index=self.index_name, mappings=mapping
                    )
                    logger.info(f"Index {index_name} created successfully")
                    logger.debug(f"Mapping: {mapping}")
                else:
                    await self.es.indices.create(index=self.index_name)
                    logger.info(
                        f"Index {index_name} created successfully with default mapping"
                    )
            else:
                logger.info(f"Index {index_name} already exists")
        except Exception as e:
            logger.error(f"Failed to initialize index: {e}")
            raise

    async def create_document(self, document, id=None):
        """Create a new document"""
        doc_id = id or document["file_hash"]
        now = datetime.now(timezone.utc)

        doc_data = document
        doc_data.update({"created_at": now, "updated_at": now})
        logger.info(f"Creating document {doc_id}")
        logger.info(f"Document data: {doc_data}")
        try:
            await self.es.index(index=self.index_name, id=doc_id, body=doc_data)
            await self.es.indices.refresh(index=self.index_name)

            return await self.get_document(doc_id)
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    async def get_document(self, doc_id: str):
        """Get a document by ID"""
        try:
            result = await self.es.get(index=self.index_name, id=doc_id)
            source = result["_source"]
            source["video_id"] = result["_id"]
            return source
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")
            raise

    async def update_document(self, doc_id: str, update_data):
        """Update a document"""
        try:
            # Prepare update data
            update_dict = {k: v for k, v in update_data.items() if v is not None}
            update_dict["updated_at"] = datetime.now(timezone.utc)

            await self.es.update(
                index=self.index_name,
                id=doc_id,
                body={"doc": update_dict, "doc_as_upsert": True},
            )
            await self.es.indices.refresh(index=self.index_name)

            return await self.get_document(doc_id)
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            raise

    @staticmethod
    def _build_query(
        query_text: Optional[str] = None,
        search_terms: Optional[List[str]] = None,
        # Generic filters
        term_filters: Optional[Dict[str, Any]] = None,
        exists_filters: Optional[List[str]] = None,
        not_exists_filters: Optional[List[str]] = None,
        terms_filters: Optional[Dict[str, List[str]]] = None,
        range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
        script_filters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generic query builder that supports various filter types.

        Args:
            query_text: Full text search
            search_terms: Terms to search in text field
            term_filters: {field: value} for exact matches
            exists_filters: [field1, field2] for fields that must exist
            not_exists_filters: [field1, field2] for fields that must NOT exist
            terms_filters: {field: [value1, value2]} for multiple values
            range_filters: {field: {"gte": 5, "lt": 10}} for range queries
            script_filters: ["doc['field'].size() >= 2"] for script queries
        """
        must_clauses: List[Dict[str, Any]] = []
        filter_clauses: List[Dict[str, Any]] = []
        must_not_clauses: List[Dict[str, Any]] = []

        # Text search
        if query_text:
            must_clauses.append({"match": {"text": query_text}})
        elif search_terms:
            must_clauses.append({"terms": {"text": search_terms}})
        else:
            must_clauses.append({"match_all": {}})

        # Term filters (exact matches)
        if term_filters:
            for field, value in term_filters.items():
                filter_clauses.append({"term": {field: value}})

        # Exists filters
        if exists_filters:
            for field in exists_filters:
                filter_clauses.append({"exists": {"field": field}})

        # Not exists filters
        if not_exists_filters:
            for field in not_exists_filters:
                must_not_clauses.append({"exists": {"field": field}})

        # Terms filters (multiple values)
        if terms_filters:
            for field, values in terms_filters.items():
                filter_clauses.append({"terms": {field: values}})

        # Range filters
        if range_filters:
            for field, range_config in range_filters.items():
                filter_clauses.append({"range": {field: range_config}})

        # Script filters
        if script_filters:
            for script_source in script_filters:
                filter_clauses.append({"script": {"script": {"source": script_source}}})

        return {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
                "must_not": must_not_clauses,
            }
        }

    async def stream_all_documents(
        self, fields_to_include: Optional[List[str]] = None, **kwargs: Any
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streams all documents matching a query, yielding them one by one.
        Efficient for processing large result sets.
        """
        query = self._build_query(**kwargs)
        search_body = {"query": query}
        try:
            async for hit in async_scan(
                client=self.es,
                index=self.index_name,
                query=search_body,
                _source=fields_to_include,
                size=200,
            ):
                yield hit
        except Exception as e:
            logger.error(f"Streaming documents failed: {e}", exc_info=True)
            raise

    async def bulk_update(
        self, actions: AsyncGenerator[Dict[str, Any], None]
    ) -> Dict[str, Any]:
        """
        Performs bulk updates using a provided iterable of actions.
        Ideal for enriching documents.
        """
        try:
            success, failed = await async_bulk(self.es, actions, stats_only=True)
            await self.es.indices.refresh(index=self.index_name)
            return {"success_count": success, "error_count": failed}
        except Exception as e:
            logger.error(f"Bulk update failed: {e}")
            raise

    async def count(self, **kwargs: Any) -> int:
        """Counts documents matching a query."""
        try:
            query = self._build_query(**kwargs)
            response = await self.es.count(index=self.index_name, query=query)
            return response.get("count", 0)
        except Exception as e:
            logger.error(f"Count query failed: {e}", exc_info=True)
            return 0

    async def refresh(self):
        return await self.es.indices.refresh(index=self.index_name)

    async def is_connected(self) -> bool:
        try:
            return await self.es.ping()
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            return False

    async def is_index_exists(self) -> bool:
        try:
            return await self.es.indices.exists(index=self.index_name)
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            return False
