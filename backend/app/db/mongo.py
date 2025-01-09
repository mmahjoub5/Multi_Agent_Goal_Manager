from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from  backend.app.configs.config import MONGO_URI




class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(MONGO_URI)
            except ConnectionFailure as e:
                print(f"Couldn't connect to the database: {e!s}")

                raise

        print(f"Connection to MongoDB with URI successful: {MONGO_URI}")

        return cls._instance


connection = MongoDatabaseConnector()