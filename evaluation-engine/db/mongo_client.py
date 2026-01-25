from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()


class MongoDBClient:
    """
    Handles MongoDB connection and exposes detectionlog collection.
    No metrics, no business logic.
    """

    def __init__(
    self,
    uri: str = None,
    db_name: str = "test",              # ✅ FIXED
    collection_name: str = "detectionlogs",
    ):

        self.uri = uri or os.getenv("MONGO_URI")
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None

        if not self.uri:
            raise RuntimeError("❌ MONGO_URI not found. Check your .env file.")

    def connect(self):
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000
            )

            # Force connection test
            self.client.admin.command("ping")

            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]

            print("✅ MongoDB connection successful")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise RuntimeError(f"❌ MongoDB connection failed: {e}")

    def get_collection(self):
        if self.collection is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.collection

    def close(self):
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")
