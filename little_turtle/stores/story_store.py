from typing import TypedDict, NotRequired, List, Optional

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database


class Story(TypedDict):
    _id: NotRequired[ObjectId]
    content: str
    image_prompt: str


class StoryStore:
    _collection: Collection[Story] = None

    def __init__(self, db: Database):
        self._collection = db['stories']

    def create(self, story: Story):
        self._collection.insert_one(story)

    def get_all(self, query: Optional[dict]) -> List[Story]:
        return list(self._collection.find(query))
