from datetime import datetime
from typing import TypedDict, NotRequired

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database


class HistoryItem(TypedDict):
    _id: NotRequired[ObjectId]
    content: str
    user_id: int
    chat_id: int
    message_id: int
    created_at: datetime


class HistoryStore:
    _collection: Collection[HistoryItem] = None

    def __init__(self, db: Database):
        self._collection = db['message_history']

    def create(self, item: HistoryItem):
        self._collection.insert_one(item)

    def get_by_message_id(self, message_id: int) -> HistoryItem:
        return self._collection.find_one({"message_id": message_id})
