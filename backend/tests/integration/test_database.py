import uuid
from src.database import mongo_client

TEST_DB_NAME = f"test_db_{uuid.uuid4().hex[:8]}"


def test_add_data():
    test_database = mongo_client[TEST_DB_NAME]
    test_database["test_collection"].insert_one({"test": True})
    data = test_database["test_collection"].find_one({"test": True})
    assert TEST_DB_NAME in mongo_client.list_database_names()
    assert "test_collection" in test_database.list_collection_names()
    assert data.get("test") == True


def test_delete_collection():
    test_database = mongo_client[TEST_DB_NAME]
    test_database["test_collection"].drop()
    assert "test_collection" not in test_database.list_collection_names()


def test_delete_database():
    mongo_client.drop_database(TEST_DB_NAME)
    assert TEST_DB_NAME not in mongo_client.list_database_names()