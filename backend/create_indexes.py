"""
MongoDB Index Creation Script for PensionFund Officer Dashboard

This script creates all recommended B-tree indexes for optimal query performance.
These are SEPARATE from Atlas Search indexes which are created through the Atlas UI.

Usage:
    python create_indexes.py

Requirements:
    - MONGODB_URL environment variable set (or update connection string below)
    - pymongo installed (pip install pymongo)
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, OperationFailure


async def create_indexes():
    """Create all recommended indexes for PensionFund Officer Dashboard."""

    # Get MongoDB connection string from environment
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db>")
    db_name = os.getenv("MONGODB_DB_NAME", "PensionFund_db")

    print("=" * 60)
    print("Creating MongoDB Indexes for PensionFund Officer Dashboard")
    print("=" * 60)
    print(f"\nConnecting to MongoDB: {mongodb_url}")
    print(f"Database: {db_name}\n")

    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]

    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ Connected to MongoDB successfully\n")

        # ============================================
        # MEMBERS COLLECTION INDEXES
        # ============================================

        print("Creating indexes for 'members' collection...")

        # Primary identifier - memberId (UNIQUE)
        try:
            await db.members.create_index(
                [("memberId", 1)],
                unique=True,
                name="idx_member_id_unique",
                background=True
            )
            print("✓ Created unique index on memberId")
        except DuplicateKeyError:
            print("⚠ Index on memberId already exists (or duplicate data found)")
        except OperationFailure as e:
            print(f"⚠ Failed to create memberId index: {e}")

        # IC Number (UNIQUE)
        try:
            await db.members.create_index(
                [("icNumber", 1)],
                unique=True,
                name="idx_ic_number_unique",
                background=True
            )
            print("✓ Created unique index on icNumber")
        except DuplicateKeyError:
            print("⚠ Index on icNumber already exists (or duplicate data found)")
        except OperationFailure as e:
            print(f"⚠ Failed to create icNumber index: {e}")

        print()

        # ============================================
        # EMPLOYERS COLLECTION INDEXES
        # ============================================

        print("Creating indexes for 'employers' collection...")

        # Primary identifier - employerId (UNIQUE)
        try:
            await db.employers.create_index(
                [("employerId", 1)],
                unique=True,
                name="idx_employer_id_unique",
                background=True
            )
            print("✓ Created unique index on employerId")
        except DuplicateKeyError:
            print("⚠ Index on employerId already exists (or duplicate data found)")
        except OperationFailure as e:
            print(f"⚠ Failed to create employerId index: {e}")

        # Employer Code (UNIQUE)
        try:
            await db.employers.create_index(
                [("employerCode", 1)],
                unique=True,
                name="idx_employer_code_unique",
                background=True
            )
            print("✓ Created unique index on employerCode")
        except DuplicateKeyError:
            print("⚠ Index on employerCode already exists (or duplicate data found)")
        except OperationFailure as e:
            print(f"⚠ Failed to create employerCode index: {e}")

        print()

        # ============================================
        # MATERIALIZED VIEW INDEXES
        # ============================================

        print("Creating indexes for materialized view collections...")

        # Member contribution trends - sorted by month descending
        await db.mv_member_contribution_trends.create_index(
            [("month", -1)],
            name="idx_month_desc",
            background=True
        )
        print("✓ Created descending index on mv_member_contribution_trends.month")

        # Employer submissions - sorted by month descending
        await db.mv_employer_submissions.create_index(
            [("month", -1)],
            name="idx_month_desc",
            background=True
        )
        print("✓ Created descending index on mv_employer_submissions.month")

        print()

        # ============================================
        # VERIFY INDEXES
        # ============================================

        print("=" * 60)
        print("Index Creation Complete!")
        print("=" * 60)
        print("\nVerifying indexes...\n")

        # List all indexes
        print("Members collection indexes:")
        async for index in db.members.list_indexes():
            print(f"  - {index['name']}: {index['key']}")

        print("\nEmployers collection indexes:")
        async for index in db.employers.list_indexes():
            print(f"  - {index['name']}: {index['key']}")

        print("\nMaterialized view indexes:")
        print("  mv_member_contribution_trends:")
        async for index in db.mv_member_contribution_trends.list_indexes():
            print(f"    - {index['name']}: {index['key']}")

        print("  mv_employer_submissions:")
        async for index in db.mv_employer_submissions.list_indexes():
            print(f"    - {index['name']}: {index['key']}")

        print("\n" + "=" * 60)
        print("Index creation successful!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

    finally:
        # Close connection
        client.close()
        print("\n✓ MongoDB connection closed")


async def drop_all_indexes():
    """
    Drop all custom indexes (useful for testing).
    WARNING: This will NOT drop the _id index (which is required).
    """
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db>")
    db_name = os.getenv("MONGODB_DB_NAME", "PensionFund_db")

    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]

    try:
        print("Dropping all custom indexes...")

        # Drop indexes (except _id)
        await db.members.drop_index("idx_member_id_unique")
        await db.members.drop_index("idx_ic_number_unique")
        print("✓ Dropped members indexes")

        await db.employers.drop_index("idx_employer_id_unique")
        await db.employers.drop_index("idx_employer_code_unique")
        print("✓ Dropped employers indexes")

        await db.mv_member_contribution_trends.drop_index("idx_month_desc")
        await db.mv_employer_submissions.drop_index("idx_month_desc")
        print("✓ Dropped materialized view indexes")

        print("\n✓ All custom indexes dropped successfully")

    except Exception as e:
        print(f"Error dropping indexes: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        print("⚠️  WARNING: This will drop all custom indexes!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(drop_all_indexes())
        else:
            print("Aborted.")
    else:
        asyncio.run(create_indexes())


"""
NOTES:

1. background=True - Allows index creation without blocking reads/writes
   (Important for production environments with existing data)

2. unique=True - Enforces uniqueness constraint on the field
   (Prevents duplicate memberId, icNumber, employerId, employerCode)

3. These indexes are SEPARATE from Atlas Search indexes:
   - Atlas Search indexes: For full-text search, faceting, vector search
   - B-tree indexes (this file): For exact match queries, sorts, uniqueness

4. The _id field is automatically indexed by MongoDB, so we don't create
   additional indexes for materialized view _id fields

5. Query patterns optimized:
   - members.find_one({"memberId": member_id})
     → member_service.py:115, 136, 163, 184, 204
   - employers.find_one({"employerId": employer_id})
     → employer_service.py:115, 136, 170, 197, 223
   - mv_member_contribution_trends.find({}).sort("month", -1)
     → dashboard_service.py:70
   - mv_employer_submissions.find({}).sort("month", -1)
     → dashboard_service.py:123

6. Index sizes (estimated for 100K members, 20K employers):
   - memberId index: ~2-3 MB
   - icNumber index: ~2-3 MB
   - employerId index: ~500 KB
   - employerCode index: ~500 KB
   - month indexes: < 100 KB each
   Total: ~8-10 MB (negligible overhead)

7. To run:
   python create_indexes.py

8. To drop all custom indexes (for testing):
   python create_indexes.py --drop
"""
