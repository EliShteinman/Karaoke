import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from .elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)


class GenericElasticsearchRepository:
    def __init__(self, es: ElasticsearchService):
        self.es_repository = es

    async def generic_enrich_documents(
        self,
        analyzer_func: Callable[[str], Any],
        search_params: Dict[str, Any],
        process_name: str,
        fields_to_include: Optional[List[str]] = None,
        field_to_process: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Generic method for enriching documents with analyzed data.

        Args:
            analyzer_func: Function that analyzes text and returns result
            search_params: Parameters for filtering documents to process
            process_name: Name for logging purposes
            fields_to_include: Fields to include in the update operation
            field_to_process: Field to read text from
        """
        docs_to_process = await self.es_repository.count(**search_params)
        logger.info(f"Found {docs_to_process} documents for {process_name}")
        if docs_to_process == 0:
            logger.info(f"No documents to process for {process_name}")
            return None

        logger.info(f"Processing {docs_to_process} documents for {process_name}")

        fields_to_include = fields_to_include
        field_to_process = field_to_process

        async def generate_update_actions() -> AsyncGenerator[Dict[str, Any], None]:
            stream = self.es_repository.stream_all_documents(
                fields_to_include=fields_to_include, **search_params
            )

            processed_count = 0
            async for doc in stream:
                text_to_analyze = doc["_source"].get(field_to_process)
                logger.debug(f"Processing document: {doc['_id']}")
                logger.debug(f"Text to analyze: {text_to_analyze}")
                if not text_to_analyze:
                    continue

                analyzed_result: dict = analyzer_func(text_to_analyze)
                logger.debug(f"Analyzed result: {analyzed_result}")
                if analyzed_result:
                    data = {
                        "_op_type": "update",
                        "_index": self.es_repository.index_name,
                        "_id": doc["_id"],
                        "doc": {
                            **analyzed_result,
                            "updated_at": datetime.now(timezone.utc),
                        },
                    }
                    logger.debug(f"Generated update action: {data}")
                    yield data
                    processed_count += 1

                    if processed_count % 100 == 0:  # Log progress
                        logger.info(
                            f"Processed {processed_count} documents for {process_name}"
                        )

        result = await self.es_repository.bulk_update(generate_update_actions())
        logger.info(f"Completed {process_name}: {result}")
        return result
