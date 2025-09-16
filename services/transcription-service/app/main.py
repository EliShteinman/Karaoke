from app.consumers.transcription_consumer import TranscriptionConsumer

if __name__ == "__main__":
    consumer = TranscriptionConsumer()
    consumer.start()
