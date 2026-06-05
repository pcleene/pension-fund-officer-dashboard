# Atlas Triggers Setup Guide

This guide explains how to set up MongoDB Atlas Triggers to automatically refresh materialized views on a schedule.

## Overview

Atlas Triggers allow you to run serverless functions on a schedule (similar to cron jobs). We use them to refresh the 8 materialized views that power the dashboard statistics.

## Prerequisites

- MongoDB Atlas cluster (M10 or higher recommended)
- Atlas App Services enabled for your project
- `PensionFund_db` database with all collections created

## Step 1: Enable Atlas App Services

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Select your project
3. Click "App Services" in the left sidebar
4. Click "Create a New App" (if you haven't already)
5. Name it "PensionFund-Dashboard-Services"
6. Link it to your MongoDB cluster
7. Click "Create"

## Step 2: Create Scheduled Triggers

For each materialized view, create a separate scheduled trigger:

### 1. Member Demographics Trigger

**Schedule:** Every 15 minutes (`*/15 * * * *`)

1. Go to App Services → Triggers
2. Click "Add a Trigger"
3. Configure:
   - **Trigger Type:** Scheduled
   - **Name:** `refresh_member_demographics`
   - **Schedule Type:** Advanced (cron expression)
   - **Cron Schedule:** `*/15 * * * *`
   - **Select An Event Type:** Function

4. **Function Code:**

```javascript
exports = async function() {
  const mongodb = context.services.get("mongodb-atlas");
  const db = mongodb.db("PensionFund_db");

  console.log("Refreshing member demographics...");

  try {
    await db.collection("members").aggregate([
      {
        $facet: {
          totalMembers: [
            { $count: "count" }
          ],
          byGender: [
            { $group: { _id: "$personalInfo.gender", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ],
          byRegion: [
            { $group: { _id: "$personalInfo.region", count: { $sum: 1 } } },
            { $sort: { count: -1 } },
            { $limit: 15 }
          ],
          byGenerationGroup: [
            { $group: { _id: "$personalInfo.generationGroup", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ],
          byJobCategory: [
            { $group: { _id: "$employmentProfile.jobCategory", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ],
          byAccountStatus: [
            { $group: { _id: "$accountInfo.accountStatus", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ],
          byRiskScore: [
            { $group: { _id: "$complianceFlags.riskScore", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ],
          byEmploymentStatus: [
            { $group: { _id: "$employmentProfile.employmentStatus", count: { $sum: 1 } } },
            { $sort: { count: -1 } }
          ]
        }
      },
      {
        $addFields: {
          _id: "demographics_summary",
          viewType: "demographics",
          refreshedAt: "$$NOW",
          dataSource: "members",
          recordCount: { $arrayElemAt: ["$totalMembers.count", 0] }
        }
      },
      {
        $merge: {
          into: "mv_member_demographics",
          on: "_id",
          whenMatched: "replace",
          whenNotMatched: "insert"
        }
      }
    ]).toArray();

    console.log("✅ Member demographics refreshed successfully at", new Date());
  } catch (error) {
    console.error("❌ Error refreshing member demographics:", error);
  }
};
```

5. Click "Save"

### 2. Member Balances Trigger

**Schedule:** Hourly (`0 * * * *`)

Follow the same steps as above, but use:
- **Name:** `refresh_member_balances`
- **Cron Schedule:** `0 * * * *`
- **Function Code:** Use the pipeline from `get_member_balances_pipeline()` in `backend/app/aggregations/materialized_views.py`

### 3. Member Contribution Trends Trigger

**Schedule:** Daily at 2 AM (`0 2 * * *`)

- **Name:** `refresh_member_contribution_trends`
- **Cron Schedule:** `0 2 * * *`
- **Function Code:** Use the pipeline from `get_member_contribution_trends_pipeline()`

### 4. Member Compliance Trigger

**Schedule:** Every 30 minutes (`*/30 * * * *`)

- **Name:** `refresh_member_compliance`
- **Cron Schedule:** `*/30 * * * *`
- **Function Code:** Use the pipeline from `get_member_compliance_pipeline()`

### 5. Employer Profiles Trigger

**Schedule:** Every 6 hours (`0 */6 * * *`)

- **Name:** `refresh_employer_profiles`
- **Cron Schedule:** `0 */6 * * *`
- **Function Code:** Use the pipeline from `get_employer_profiles_pipeline()`

### 6. Employer Compliance Trigger

**Schedule:** Every 3 hours (`0 */3 * * *`)

- **Name:** `refresh_employer_compliance`
- **Cron Schedule:** `0 */3 * * *`
- **Function Code:** Use the pipeline from `get_employer_compliance_pipeline()`

### 7. Employer Workforce Trigger

**Schedule:** Daily at 3 AM (`0 3 * * *`)

- **Name:** `refresh_employer_workforce`
- **Cron Schedule:** `0 3 * * *`
- **Function Code:** Use the pipeline from `get_employer_workforce_pipeline()`

### 8. Employer Submissions Trigger

**Schedule:** Daily at 4 AM (`0 4 * * *`)

- **Name:** `refresh_employer_submissions`
- **Cron Schedule:** `0 4 * * *`
- **Function Code:** Use the pipeline from `get_employer_submissions_pipeline()`

## Step 3: Test Triggers

To test a trigger manually before the scheduled time:

1. Go to App Services → Triggers
2. Find your trigger in the list
3. Click "Run" on the right side
4. View the execution logs to verify success

## Step 4: Monitor Trigger Execution

1. Go to App Services → Logs
2. Filter by "Triggers"
3. Monitor for successful executions and errors
4. Set up alerts for failed triggers (optional)

## Refresh Frequency Summary

| View | Refresh Frequency | Cron Expression | Reason |
|------|------------------|-----------------|--------|
| Member Demographics | Every 15-30 min | `*/15 * * * *` | Lightweight, no $unwind |
| Member Balances | Hourly | `0 * * * *` | Medium weight, financial data |
| Member Contribution Trends | Daily at 2 AM | `0 2 * * *` | Heavy, has $unwind |
| Member Compliance | Every 30 min | `*/30 * * * *` | Boolean flags, fast |
| Employer Profiles | Every 6 hours | `0 */6 * * *` | Lightweight segmentation |
| Employer Compliance | Every 3 hours | `0 */3 * * *` | Compliance-critical |
| Employer Workforce | Daily at 3 AM | `0 3 * * *` | Light $unwind |
| Employer Submissions | Daily at 4 AM | `0 4 * * *` | Heavy, has $unwind |

## Alternative: Manual Refresh via API

If you prefer not to use Atlas Triggers, you can refresh views manually via the API:

```bash
# Refresh all views
curl -X POST http://localhost:8000/api/v1/dashboard/refresh \
  -H "Content-Type: application/json" \
  -d '{"views": ["all"]}'

# Refresh specific views
curl -X POST http://localhost:8000/api/v1/dashboard/refresh \
  -H "Content-Type: application/json" \
  -d '{"views": ["member_demographics", "member_balances"]}'
```

You could then set up a cron job or scheduled task on your server to call these endpoints.

## Best Practices

1. **Stagger daily refreshes:** Notice we schedule heavy views at different times (2 AM, 3 AM, 4 AM) to avoid database load spikes

2. **Monitor execution time:** If a trigger takes too long, consider:
   - Adding indexes to the source collections
   - Splitting the view into smaller pieces
   - Reducing the refresh frequency

3. **Set up alerts:** Configure Atlas to alert you when triggers fail

4. **Test with sample data first:** Before running on production data, test all triggers with a small dataset

## Troubleshooting

### Trigger Fails with Timeout

- Reduce the amount of data being processed
- Add indexes to improve aggregation performance
- Consider splitting the view into multiple smaller views

### Trigger Runs But View is Empty

- Check that the source collection has data
- Verify the `$merge` target collection name matches your database
- Check the trigger logs for errors

### Dashboard Shows Stale Data

- Verify triggers are enabled and running on schedule
- Check trigger execution logs
- Manually trigger a refresh to test
- Verify the materialized view collections exist

## Resources

- [MongoDB Atlas Triggers Documentation](https://www.mongodb.com/docs/atlas/app-services/triggers/)
- [Cron Expression Generator](https://crontab.guru/)
- [Aggregation Pipeline Operators](https://www.mongodb.com/docs/manual/reference/operator/aggregation/)
