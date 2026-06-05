"""
MongoDB database connection and management.
Uses Motor for async MongoDB operations.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB Atlas connection lifecycle."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Establish connection to MongoDB Atlas."""
        try:
            logger.info(f"Connecting to MongoDB: {settings.mongodb_db_name}")

            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=settings.mongodb_max_pool_size,
                minPoolSize=settings.mongodb_min_pool_size,
            )

            self.database = self.client[settings.mongodb_db_name]

            # Verify connection
            await self.client.admin.command('ping')

            logger.info("Successfully connected to MongoDB Atlas")

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            logger.info("Disconnecting from MongoDB")
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if self.database is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return self.database

    def get_collection(self, collection_name: str):
        """Get a specific collection."""
        db = self.get_database()
        return db[collection_name]


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get database instance.
    Use this in FastAPI route dependencies.
    """
    return db_manager.get_database()


async def get_members_collection():
    """Get members collection."""
    return db_manager.get_collection("members")


async def get_employers_collection():
    """Get employers collection."""
    return db_manager.get_collection("employers")


# Materialized view collections
async def get_mv_member_demographics():
    """Get member demographics materialized view."""
    return db_manager.get_collection("mv_member_demographics")


async def get_mv_member_balances():
    """Get member balances materialized view."""
    return db_manager.get_collection("mv_member_balances")


async def get_mv_member_contribution_trends():
    """Get member contribution trends materialized view."""
    return db_manager.get_collection("mv_member_contribution_trends")


async def get_mv_member_compliance():
    """Get member compliance materialized view."""
    return db_manager.get_collection("mv_member_compliance")


async def get_mv_employer_profiles():
    """Get employer profiles materialized view."""
    return db_manager.get_collection("mv_employer_profiles")


async def get_mv_employer_compliance():
    """Get employer compliance materialized view."""
    return db_manager.get_collection("mv_employer_compliance")


async def get_mv_employer_workforce():
    """Get employer workforce materialized view."""
    return db_manager.get_collection("mv_employer_workforce")


async def get_mv_employer_submissions():
    """Get employer submissions materialized view."""
    return db_manager.get_collection("mv_employer_submissions")
