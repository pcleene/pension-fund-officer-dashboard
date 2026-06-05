/**
 * MongoDB Index Creation Script for PensionFund Officer Dashboard
 *
 * This script creates all recommended B-tree indexes for optimal query performance.
 * These are SEPARATE from Atlas Search indexes which are created through the Atlas UI.
 *
 * Run this script in MongoDB Shell (mongosh) or MongoDB Compass:
 * mongosh mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db> --file create_indexes.js
 *
 * Or execute the commands manually in MongoDB Compass or Atlas UI.
 */

// Switch to PensionFund_db database
use PensionFund_db;

print("========================================");
print("Creating MongoDB Indexes for PensionFund Officer Dashboard");
print("========================================\n");

// ============================================
// MEMBERS COLLECTION INDEXES
// ============================================

print("Creating indexes for 'members' collection...");

// Primary identifier - memberId (UNIQUE)
db.members.createIndex(
  { "memberId": 1 },
  {
    unique: true,
    name: "idx_member_id_unique",
    background: true
  }
);
print("✓ Created unique index on memberId");

// IC Number (UNIQUE) - Natural lookup key for Malaysian PensionFund members
db.members.createIndex(
  { "icNumber": 1 },
  {
    unique: true,
    name: "idx_ic_number_unique",
    background: true
  }
);
print("✓ Created unique index on icNumber\n");

// ============================================
// EMPLOYERS COLLECTION INDEXES
// ============================================

print("Creating indexes for 'employers' collection...");

// Primary identifier - employerId (UNIQUE)
db.employers.createIndex(
  { "employerId": 1 },
  {
    unique: true,
    name: "idx_employer_id_unique",
    background: true
  }
);
print("✓ Created unique index on employerId");

// Employer Code (UNIQUE) - Natural lookup key for Malaysian PensionFund employers
db.employers.createIndex(
  { "employerCode": 1 },
  {
    unique: true,
    name: "idx_employer_code_unique",
    background: true
  }
);
print("✓ Created unique index on employerCode\n");

// ============================================
// MATERIALIZED VIEW INDEXES
// ============================================

print("Creating indexes for materialized view collections...");

// Member contribution trends - sorted by month descending
db.mv_member_contribution_trends.createIndex(
  { "month": -1 },
  {
    name: "idx_month_desc",
    background: true
  }
);
print("✓ Created descending index on mv_member_contribution_trends.month");

// Employer submissions - sorted by month descending
db.mv_employer_submissions.createIndex(
  { "month": -1 },
  {
    name: "idx_month_desc",
    background: true
  }
);
print("✓ Created descending index on mv_employer_submissions.month\n");

// ============================================
// VERIFY INDEXES
// ============================================

print("========================================");
print("Index Creation Complete!");
print("========================================\n");

print("Verifying indexes...\n");

print("Members collection indexes:");
printjson(db.members.getIndexes());

print("\nEmployers collection indexes:");
printjson(db.employers.getIndexes());

print("\nMaterialized view indexes:");
printjson(db.mv_member_contribution_trends.getIndexes());
printjson(db.mv_employer_submissions.getIndexes());

print("\n========================================");
print("Index creation successful!");
print("========================================");

/**
 * NOTES:
 *
 * 1. background: true - Allows index creation without blocking reads/writes
 *    (Important for production environments with existing data)
 *
 * 2. unique: true - Enforces uniqueness constraint on the field
 *    (Prevents duplicate memberId, icNumber, employerId, employerCode)
 *
 * 3. These indexes are SEPARATE from Atlas Search indexes:
 *    - Atlas Search indexes: For full-text search, faceting, vector search
 *    - B-tree indexes (this file): For exact match queries, sorts, uniqueness
 *
 * 4. The _id field is automatically indexed by MongoDB, so we don't create
 *    additional indexes for materialized view _id fields
 *
 * 5. Query patterns optimized:
 *    - members.find_one({"memberId": member_id}) - Lines 115, 136, 163, 184, 204
 *    - employers.find_one({"employerId": employer_id}) - Lines 115, 136, 170, 197, 223
 *    - mv_member_contribution_trends.find({}).sort("month", -1) - Line 70
 *    - mv_employer_submissions.find({}).sort("month", -1) - Line 123
 *
 * 6. Index sizes (estimated for 100K members, 20K employers):
 *    - memberId index: ~2-3 MB
 *    - icNumber index: ~2-3 MB
 *    - employerId index: ~500 KB
 *    - employerCode index: ~500 KB
 *    - month indexes: < 100 KB each
 *    Total: ~8-10 MB (negligible overhead)
 */
