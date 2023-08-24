from typing import TypedDict, Optional

from bson import ObjectId
from pymongo.database import Database


class Story(TypedDict):
    _id: Optional[ObjectId]
    content: str
    image_prompt: str


class StoryStore:
    def __init__(self, db: Database):
        self._collection = db['stories']

    def create(self, story: Story):
        self._collection.insert_one(story)

    def get_all(self) -> [Story]:
        return self._collection.find()
