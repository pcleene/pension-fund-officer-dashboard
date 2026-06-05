# MongoDB Indexing Strategy for Pension Fund Officer Dashboard

This document outlines the complete indexing strategy for the PensionFund Officer Dashboard, including both Atlas Search indexes and regular B-tree indexes.

---

## Table of Contents

1. [Overview](#overview)
2. [Atlas Search Indexes](#atlas-search-indexes)
3. [B-tree Indexes](#b-tree-indexes)
4. [Index Creation](#index-creation)
5. [Performance Impact](#performance-impact)
6. [Maintenance](#maintenance)

---

## Overview

The PensionFund Officer Dashboard uses **two types of indexes**:

1. **Atlas Search Indexes** - For full-text search, faceted search, and vector search
2. **B-tree Indexes** - For exact match queries, sorts, and uniqueness constraints

### Why Two Types?

- **Atlas Search indexes** are specialized for search operations:
  - Full-text search with relevance scoring
  - Faceted filtering (multi-select dropdowns)
  - Semantic vector search (natural language queries)

- **B-tree indexes** are for traditional database operations:
  - Exact match lookups (e.g., `find_one({"memberId": "M123456"})`)
  - Sorting (e.g., `sort("month", -1)`)
  - Uniqueness constraints (preventing duplicates)

---

## Atlas Search Indexes

These are created through the **MongoDB Atlas UI** or **Atlas CLI**, not through standard MongoDB commands.

### 1. Members Search Index

**Index Name:** `members_search_index`
**Collection:** `members`
**File:** `backend/atlas_search_indexes/members_search_index.json`

**Features:**
- Full-text search on: `fullName`, `memberId`, `icNumber`
- Faceted filtering on: `accountStatus`, `region`, `generationGroup`, `jobCategory`, `riskScore`
- All faceted fields use `"type": "token"` for exact value matching

### 2. Employers Search Index

**Index Name:** `employers_search_index`
**Collection:** `employers`
**File:** `backend/atlas_search_indexes/employers_search_index.json`

**Features:**
- Full-text search on: `companyName`, `employerId`, `employerCode`, `registrationNumber`
- Faceted filtering on: `sector`, `companySize`, `state`, `riskRating`
- All faceted fields use `"type": "token"` for exact value matching

### 3. Members Vector Index

**Index Name:** `members_vector_index`
**Collection:** `members`
**File:** `backend/atlas_search_indexes/members_vector_index.json`

**Features:**
- 512-dimensional vector search using Voyage Large 2 embeddings
- Enables semantic search like "members with contribution gaps in KL"
- **Note:** `semanticEmbedding` field not yet populated in sample data

### 4. Employers Vector Index

**Index Name:** `employers_vector_index`
**Collection:** `employers`
**File:** `backend/atlas_search_indexes/employers_vector_index.json`

**Features:**
- 512-dimensional vector search using Voyage Large 2 embeddings
- Enables semantic search like "tech companies with late payments"
- **Note:** `semanticEmbedding` field not yet populated in sample data

---

## B-tree Indexes

These are **regular MongoDB indexes** created using standard MongoDB commands.

### Why These Indexes?

Based on code analysis, these indexes optimize the following query patterns:

| Query Pattern | File Location | Frequency |
|--------------|---------------|-----------|
| `members.find_one({"memberId": member_id})` | `member_service.py:115, 136, 163, 184, 204` | Every member detail page load |
| `employers.find_one({"employerId": employer_id})` | `employer_service.py:115, 136, 170, 197, 223` | Every employer detail page load |
| `mv_member_contribution_trends.find({}).sort("month", -1)` | `dashboard_service.py:70` | Dashboard loads |
| `mv_employer_submissions.find({}).sort("month", -1)` | `dashboard_service.py:123` | Dashboard loads |

---

### 1. Members Collection Indexes

#### Primary Identifier (UNIQUE)
```javascript
db.members.createIndex(
  { "memberId": 1 },
  { unique: true, name: "idx_member_id_unique" }
)
```

**Purpose:**
- Optimizes all member lookup queries
- Enforces uniqueness (prevents duplicate member IDs)
- **Query pattern:** `find_one({"memberId": "M123456"})`

**Impact:**
- Without index: O(n) collection scan - up to 100,000 documents scanned
- With index: O(log n) - typically 10-15 comparisons for 100K documents
- **Speed improvement:** ~10,000x faster for large collections

---

#### IC Number (UNIQUE)
```javascript
db.members.createIndex(
  { "icNumber": 1 },
  { unique: true, name: "idx_ic_number_unique" }
)
```

**Purpose:**
- Natural lookup key for Malaysian PensionFund members
- Enforces data integrity (no duplicate IC numbers)
- Future-proofs for IC-based search features

**Impact:**
- Currently not queried, but essential for data quality
- Prevents accidental duplicate member records

---

### 2. Employers Collection Indexes

#### Primary Identifier (UNIQUE)
```javascript
db.employers.createIndex(
  { "employerId": 1 },
  { unique: true, name: "idx_employer_id_unique" }
)
```

**Purpose:**
- Optimizes all employer lookup queries
- Enforces uniqueness
- **Query pattern:** `find_one({"employerId": "E12345"})`

**Impact:**
- Same as memberId index - ~10,000x faster for lookups

---

#### Employer Code (UNIQUE)
```javascript
db.employers.createIndex(
  { "employerCode": 1 },
  { unique: true, name: "idx_employer_code_unique" }
)
```

**Purpose:**
- Natural lookup key for Malaysian PensionFund employers
- Enforces data integrity

---

### 3. Materialized View Indexes

#### Member Contribution Trends - Month Sort
```javascript
db.mv_member_contribution_trends.createIndex(
  { "month": -1 },
  { name: "idx_month_desc" }
)
```

**Purpose:**
- Optimizes dashboard queries that fetch last N months of contribution trends
- **Query pattern:** `find({}).sort("month", -1).limit(12)`

**Impact:**
- Without index: Fetches all documents, sorts in memory, then limits
- With index: Uses index to return first 12 documents (already sorted)
- **Speed improvement:** ~100x faster when collection grows large

---

#### Employer Submissions - Month Sort
```javascript
db.mv_employer_submissions.createIndex(
  { "month": -1 },
  { name: "idx_month_desc" }
)
```

**Purpose:**
- Same as above, for employer submission trends

---

### 4. Auto-Created Indexes

MongoDB automatically creates an index on `_id` for every collection. We use this for materialized views:

- `mv_member_demographics._id = "demographics_summary"` ✅ Already indexed
- `mv_member_balances._id = "balance_summary"` ✅ Already indexed
- `mv_member_compliance._id = "compliance_summary"` ✅ Already indexed
- `mv_employer_profiles._id = "employer_profiles"` ✅ Already indexed
- `mv_employer_compliance._id = "employer_compliance"` ✅ Already indexed
- `mv_employer_workforce._id = "workforce_summary"` ✅ Already indexed

**No additional indexing needed** for these collections.

---

## Index Creation

### Option 1: MongoDB Shell (mongosh)

```bash
mongosh "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db>" --file create_indexes.js
```

Or run commands manually in mongosh or MongoDB Compass.

### Option 2: Python Script

```bash
# Set environment variables first
export MONGODB_URL="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db>"
export MONGODB_DB_NAME="PensionFund_db"

# Run the script
python create_indexes.py
```

### Option 3: MongoDB Compass

1. Connect to your cluster
2. Select `PensionFund_db` database
3. For each collection, go to "Indexes" tab
4. Click "Create Index"
5. Paste the index definition (without the `createIndex` wrapper)

### Option 4: Atlas UI

1. Go to MongoDB Atlas dashboard
2. Navigate to your cluster → Collections
3. Select collection → Indexes
4. Click "Create Index"
5. Use the JSON editor to paste index definitions

---

## Performance Impact

### Index Sizes (Estimated)

For 100,000 members and 20,000 employers:

| Index | Estimated Size |
|-------|----------------|
| `members.memberId` | 2-3 MB |
| `members.icNumber` | 2-3 MB |
| `employers.employerId` | 500 KB |
| `employers.employerCode` | 500 KB |
| `mv_member_contribution_trends.month` | < 100 KB |
| `mv_employer_submissions.month` | < 100 KB |
| **Total** | **~8-10 MB** |

**Impact:** Negligible storage overhead (<1% of total data size)

---

### Query Performance Improvements

| Query Type | Without Index | With Index | Improvement |
|------------|---------------|------------|-------------|
| Member lookup by ID | 100-200ms | 1-2ms | **100x faster** |
| Employer lookup by ID | 50-100ms | 1-2ms | **50x faster** |
| Dashboard trend queries | 50-100ms | 5-10ms | **10x faster** |

---

### Write Performance Impact

Indexes add a small overhead to write operations:

- **Inserts:** ~5-10% slower (must update 2 indexes per document)
- **Updates:** Minimal impact (only if indexed fields change)
- **Deletes:** ~5-10% slower (must update indexes)

**For this application:** Write performance impact is negligible because:
1. Data is mostly read-heavy (searches and dashboard views)
2. Writes are batch operations (sample data generation, materialized view refreshes)
3. Real-time writes are minimal (no user-generated data)

---

## Maintenance

### Monitoring Index Usage

Check if indexes are being used:

```javascript
// Check query explain plan
db.members.find({"memberId": "M123456"}).explain("executionStats")

// List all indexes
db.members.getIndexes()

// Get index stats
db.members.aggregate([{ $indexStats: {} }])
```

### Rebuilding Indexes

If indexes become fragmented:

```javascript
// Rebuild all indexes (blocking operation)
db.members.reIndex()

// Or drop and recreate specific index
db.members.dropIndex("idx_member_id_unique")
db.members.createIndex({ "memberId": 1 }, { unique: true, name: "idx_member_id_unique" })
```

### Background Index Creation

All indexes in our scripts use `background: true`:

```javascript
db.members.createIndex(
  { "memberId": 1 },
  { unique: true, background: true }  // ← Non-blocking
)
```

**Benefits:**
- Doesn't block reads/writes during creation
- Safe for production environments
- Takes longer but doesn't impact app availability

---

## Summary

### Atlas Search Indexes (4 total)
✅ `members_search_index` - Full-text + faceted search
✅ `employers_search_index` - Full-text + faceted search
✅ `members_vector_index` - Semantic vector search
✅ `employers_vector_index` - Semantic vector search

### B-tree Indexes (6 total)
✅ `members.memberId` (unique)
✅ `members.icNumber` (unique)
✅ `employers.employerId` (unique)
✅ `employers.employerCode` (unique)
✅ `mv_member_contribution_trends.month` (descending)
✅ `mv_employer_submissions.month` (descending)

### Auto-Created Indexes
✅ All `_id` fields (automatically indexed by MongoDB)

---

## Next Steps

1. **Create Atlas Search indexes** using the JSON files in `backend/atlas_search_indexes/`
2. **Create B-tree indexes** using either:
   - `create_indexes.js` (MongoDB Shell)
   - `create_indexes.py` (Python script)
   - Manual creation via Atlas UI or Compass
3. **Verify indexes** are created correctly
4. **Monitor performance** using Atlas Performance Advisor

---

## References

- [MongoDB Index Documentation](https://www.mongodb.com/docs/manual/indexes/)
- [Atlas Search Documentation](https://www.mongodb.com/docs/atlas/atlas-search/)
- [Index Performance Best Practices](https://www.mongodb.com/docs/manual/indexes/#index-performance)
