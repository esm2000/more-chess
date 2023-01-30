import os
import sys

from src.database import mongo_client


def test_add_data():
    test_database = mongo_client["test_database"]
    test_database["test_collection"].insert_one({"test": True})
    data = test_database["test_collection"].find_one({"test": True})
    assert "test_database" in mongo_client.list_database_names()
    assert "test_collection" in test_database.list_collection_names()
    assert data.get("test") == True


def test_delete_collection():
    test_database = mongo_client["test_database"]
    test_database["test_collection"].drop()
    assert "test_collection" not in test_database.list_collection_names()


def test_delete_database():
    mongo_client.drop_database("test_database")
    assert "test_database" not in mongo_client.list_database_names()
