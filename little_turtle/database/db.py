from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase

from little_turtle.services import AppConfig


class Database:
    _client: MongoClient
    _db: PyMongoDatabase

    def __init__(self, config: AppConfig):
        self._client = MongoClient(
            config.MONGODB_URI,
            username=config.MONGODB_USERNAME,
            password=config.MONGODB_PASSWORD,
        )
        self._db = self._client.get_database(config.MONGODB_DB_NAME)

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self) -> PyMongoDatabase:
        return self._db
