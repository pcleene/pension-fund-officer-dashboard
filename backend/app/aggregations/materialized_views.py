"""
Materialized view aggregation pipelines for fast dashboard loading.

This module contains all 8 materialized view pipelines that pre-aggregate
data for dashboard statistics. These should be executed on a schedule using
Atlas Triggers or APScheduler.
"""
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# =======================
# MEMBER MATERIALIZED VIEWS
# =======================

def get_member_demographics_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_member_demographics materialized view.

    Refresh frequency: Every 15-30 minutes
    Size: Very small (~1 document)
    No $unwind: ✅ Extremely fast

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                "totalMembers": [
                    {"$count": "count"}
                ],
                "byGender": [
                    {"$group": {"_id": "$personalInfo.gender", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byRegion": [
                    {"$group": {"_id": "$personalInfo.region", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 15}
                ],
                "byGenerationGroup": [
                    {"$group": {"_id": "$personalInfo.generationGroup", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byJobCategory": [
                    {"$group": {"_id": "$employmentProfile.jobCategory", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byAccountStatus": [
                    {"$group": {"_id": "$accountInfo.accountStatus", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byRiskScore": [
                    {"$group": {"_id": "$complianceFlags.riskScore", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byEmploymentStatus": [
                    {"$group": {"_id": "$employmentProfile.employmentStatus", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]
            }
        },
        {
            "$addFields": {
                "_id": "demographics_summary",
                "viewType": "demographics",
                "refreshedAt": "$$NOW",
                "dataSource": "members",
                "recordCount": {"$arrayElemAt": ["$totalMembers.count", 0]}
            }
        },
        {
            "$merge": {
                "into": "mv_member_demographics",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_member_balances_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_member_balances materialized view.

    Refresh frequency: Hourly or every 6 hours
    Size: Very small (~1 document)
    No $unwind: ✅ Fast aggregations only

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                "totalBalances": [
                    {
                        "$group": {
                            "_id": None,
                            "totalAkaun1": {"$sum": "$accountInfo.akaun1Balance"},
                            "totalAkaun2": {"$sum": "$accountInfo.akaun2Balance"},
                            "totalBalance": {"$sum": "$accountInfo.totalBalance"},
                            "avgBalance": {"$avg": "$accountInfo.totalBalance"},
                            "maxBalance": {"$max": "$accountInfo.totalBalance"},
                            "minBalance": {"$min": "$accountInfo.totalBalance"}
                        }
                    }
                ],
                "balanceDistribution": [
                    {
                        "$bucket": {
                            "groupBy": "$accountInfo.totalBalance",
                            "boundaries": [0, 10000, 25000, 50000, 100000, 200000, 500000, 1000000],
                            "default": "1000000+",
                            "output": {
                                "count": {"$sum": 1},
                                "avgBalance": {"$avg": "$accountInfo.totalBalance"}
                            }
                        }
                    }
                ],
                "akaun1Distribution": [
                    {
                        "$bucket": {
                            "groupBy": "$accountInfo.akaun1Balance",
                            "boundaries": [0, 10000, 25000, 50000, 100000, 200000],
                            "default": "200000+",
                            "output": {
                                "count": {"$sum": 1}
                            }
                        }
                    }
                ],
                "akaun2Distribution": [
                    {
                        "$bucket": {
                            "groupBy": "$accountInfo.akaun2Balance",
                            "boundaries": [0, 5000, 15000, 30000, 60000, 100000],
                            "default": "100000+",
                            "output": {
                                "count": {"$sum": 1}
                            }
                        }
                    }
                ]
            }
        },
        {
            "$addFields": {
                "_id": "balance_summary",
                "viewType": "balances",
                "refreshedAt": "$$NOW",
                "dataSource": "members"
            }
        },
        {
            "$merge": {
                "into": "mv_member_balances",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_member_contribution_trends_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_member_contribution_trends materialized view.

    Refresh frequency: Daily (has $unwind - slower)
    Size: Small (~12-24 documents, one per month)
    Has $unwind: ⚠️ Slower, refresh less frequently

    Returns:
        Aggregation pipeline
    """
    return [
        # Unwind recent contributions
        {"$unwind": "$recentContributions"},

        # Group by month
        {
            "$group": {
                "_id": "$recentContributions.contributionMonth",
                "totalContribution": {"$sum": "$recentContributions.totalContribution"},
                "totalWages": {"$sum": "$recentContributions.wageReported"},
                "employerContribution": {"$sum": "$recentContributions.employerContribution"},
                "employeeContribution": {"$sum": "$recentContributions.employeeContribution"},
                "uniqueMembers": {"$addToSet": "$memberId"},
                "avgWage": {"$avg": "$recentContributions.wageReported"},
                "avgContribution": {"$avg": "$recentContributions.totalContribution"},
                "acceptedCount": {
                    "$sum": {"$cond": [{"$eq": ["$recentContributions.submissionStatus", "Accepted"]}, 1, 0]}
                },
                "pendingCount": {
                    "$sum": {"$cond": [{"$eq": ["$recentContributions.submissionStatus", "Pending"]}, 1, 0]}
                },
                "latePaymentCount": {
                    "$sum": {"$cond": ["$recentContributions.isLatePayment", 1, 0]}
                }
            }
        },

        # Calculate member count
        {
            "$addFields": {
                "memberCount": {"$size": "$uniqueMembers"}
            }
        },

        # Project final shape
        {
            "$project": {
                "_id": 0,
                "month": "$_id",
                "totalContribution": 1,
                "totalWages": 1,
                "employerContribution": 1,
                "employeeContribution": 1,
                "memberCount": 1,
                "avgWage": {"$round": ["$avgWage", 2]},
                "avgContribution": {"$round": ["$avgContribution", 2]},
                "acceptedCount": 1,
                "pendingCount": 1,
                "latePaymentCount": 1,
                "onTimeRate": {
                    "$round": [
                        {
                            "$divide": [
                                "$acceptedCount",
                                {"$add": ["$acceptedCount", "$pendingCount", "$latePaymentCount"]}
                            ]
                        },
                        4
                    ]
                }
            }
        },

        # Sort by month descending
        {"$sort": {"month": -1}},

        # Limit to last 24 months
        {"$limit": 24},

        # Add metadata
        {
            "$addFields": {
                "viewType": "contribution_trends",
                "refreshedAt": "$$NOW",
                "dataSource": "members"
            }
        },

        # Merge into collection
        {
            "$merge": {
                "into": "mv_member_contribution_trends",
                "on": "month",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_member_compliance_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_member_compliance materialized view.

    Refresh frequency: Every 30 minutes
    Size: Very small (~1 document)
    No $unwind: ✅ Boolean flags only, instant

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                # Eligibility metrics
                "eligibilitySummary": [
                    {
                        "$group": {
                            "_id": None,
                            "housingEligible": {
                                "$sum": {"$cond": ["$eligibilityFlags.housingWithdrawal", 1, 0]}
                            },
                            "educationEligible": {
                                "$sum": {"$cond": ["$eligibilityFlags.educationWithdrawal", 1, 0]}
                            },
                            "medicalEligible": {
                                "$sum": {"$cond": ["$eligibilityFlags.medicalWithdrawal", 1, 0]}
                            },
                            "retirementEligible": {
                                "$sum": {"$cond": ["$eligibilityFlags.retirementAge", 1, 0]}
                            },
                            "minimumBalanceReached": {
                                "$sum": {"$cond": ["$eligibilityFlags.minimumBalanceReached", 1, 0]}
                            }
                        }
                    }
                ],

                # Compliance metrics
                "complianceSummary": [
                    {
                        "$group": {
                            "_id": None,
                            "withIrregularities": {
                                "$sum": {"$cond": ["$complianceFlags.hasIrregularities", 1, 0]}
                            },
                            "withMissingContributions": {
                                "$sum": {"$cond": ["$complianceFlags.hasMissingContributions", 1, 0]}
                            },
                            "withWageDiscrepancies": {
                                "$sum": {"$cond": ["$complianceFlags.hasWageDiscrepancies", 1, 0]}
                            },
                            "withActiveComplaints": {
                                "$sum": {"$cond": ["$complianceFlags.hasActiveComplaints", 1, 0]}
                            },
                            "cleanRecord": {
                                "$sum": {
                                    "$cond": [
                                        {
                                            "$and": [
                                                {"$not": "$complianceFlags.hasIrregularities"},
                                                {"$not": "$complianceFlags.hasMissingContributions"},
                                                {"$not": "$complianceFlags.hasWageDiscrepancies"},
                                                {"$not": "$complianceFlags.hasActiveComplaints"}
                                            ]
                                        },
                                        1,
                                        0
                                    ]
                                }
                            }
                        }
                    }
                ],

                # Risk distribution
                "riskDistribution": [
                    {"$group": {"_id": "$complianceFlags.riskScore", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ],

                # Gap analysis
                "gapAnalysis": [
                    {
                        "$match": {"contributionStats.hasGaps": True}
                    },
                    {
                        "$group": {
                            "_id": None,
                            "membersWithGaps": {"$sum": 1},
                            "totalGapMonths": {"$sum": {"$size": "$contributionStats.gapMonths"}},
                            "avgGapsPerMember": {"$avg": {"$size": "$contributionStats.gapMonths"}}
                        }
                    }
                ]
            }
        },
        {
            "$addFields": {
                "_id": "compliance_summary",
                "viewType": "compliance",
                "refreshedAt": "$$NOW",
                "dataSource": "members"
            }
        },
        {
            "$merge": {
                "into": "mv_member_compliance",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


# ===========================
# EMPLOYER MATERIALIZED VIEWS
# ===========================

def get_employer_profiles_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_employer_profiles materialized view.

    Refresh frequency: Every 6 hours
    Size: Very small (~1 document)
    No heavy operations: ✅ Fast grouping only

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                "totalEmployers": [
                    {"$count": "count"}
                ],
                "byAccountStatus": [
                    {"$group": {"_id": "$accountStatus.status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byAccountType": [
                    {"$group": {"_id": "$accountStatus.accountType", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "bySector": [
                    {"$group": {"_id": "$companyProfile.industryClassification.sector", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 20}
                ],
                "byCompanySize": [
                    {"$group": {"_id": "$companyProfile.companySize", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ],
                "byState": [
                    {"$group": {"_id": "$companyProfile.businessAddress.state", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 15}
                ],
                "byRiskRating": [
                    {"$group": {"_id": "$complianceStatus.riskRating", "count": {"$sum": 1}}},
                    {"$sort": {"_id": 1}}
                ],
                "trendAnalysis": [
                    {"$group": {"_id": "$contributionStats.trend", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "byProductTags": [
                    {"$unwind": "$productTags"},
                    {"$group": {"_id": "$productTags", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]
            }
        },
        {
            "$addFields": {
                "_id": "employer_profiles",
                "viewType": "profiles",
                "refreshedAt": "$$NOW",
                "dataSource": "employers",
                "totalCount": {"$arrayElemAt": ["$totalEmployers.count", 0]}
            }
        },
        {
            "$merge": {
                "into": "mv_employer_profiles",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_employer_compliance_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_employer_compliance materialized view.

    Refresh frequency: Every 3-6 hours
    Size: Very small (~1 document)
    No $unwind: ✅ Compliance metrics only

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                "complianceMetrics": [
                    {
                        "$group": {
                            "_id": None,
                            "withArrears": {"$sum": {"$cond": ["$complianceStatus.hasArrears", 1, 0]}},
                            "totalArrearsAmount": {
                                "$sum": {"$cond": ["$complianceStatus.hasArrears", "$complianceStatus.arrearsAmount", 0]}
                            },
                            "avgArrearsAmount": {
                                "$avg": {"$cond": ["$complianceStatus.hasArrears", "$complianceStatus.arrearsAmount", None]}
                            },
                            "withLegalCases": {"$sum": {"$cond": ["$complianceStatus.hasLegalCases", 1, 0]}},
                            "totalLatePayments": {"$sum": "$contributionStats.totalLatePayments"},
                            "totalLateCharges": {"$sum": "$contributionStats.totalLateCharges"},
                            "avgOnTimeRate": {"$avg": "$contributionStats.onTimeRate"}
                        }
                    }
                ],
                "arrearsByRiskRating": [
                    {
                        "$match": {"complianceStatus.hasArrears": True}
                    },
                    {
                        "$group": {
                            "_id": "$complianceStatus.riskRating",
                            "count": {"$sum": 1},
                            "totalArrears": {"$sum": "$complianceStatus.arrearsAmount"}
                        }
                    },
                    {"$sort": {"totalArrears": -1}}
                ],
                "legalCasesByType": [
                    {
                        "$match": {"complianceStatus.hasLegalCases": True}
                    },
                    {"$unwind": "$complianceStatus.legalCaseTypes"},
                    {
                        "$group": {
                            "_id": "$complianceStatus.legalCaseTypes",
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"count": -1}}
                ],
                "auditCompliance": [
                    {
                        "$group": {
                            "_id": "$complianceStatus.auditResult",
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"count": -1}}
                ],
                "onTimePaymentDistribution": [
                    {
                        "$bucket": {
                            "groupBy": "$contributionStats.onTimeRate",
                            "boundaries": [0, 0.5, 0.7, 0.85, 0.95, 1.0],
                            "default": "other",
                            "output": {
                                "count": {"$sum": 1}
                            }
                        }
                    }
                ]
            }
        },
        {
            "$addFields": {
                "_id": "employer_compliance",
                "viewType": "compliance",
                "refreshedAt": "$$NOW",
                "dataSource": "employers"
            }
        },
        {
            "$merge": {
                "into": "mv_employer_compliance",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_employer_workforce_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_employer_workforce materialized view.

    Refresh frequency: Daily
    Size: Very small (~1 document)
    Light $unwind: ⚠️ Only for nested objects, still fast

    Returns:
        Aggregation pipeline
    """
    return [
        {
            "$facet": {
                "workforceMetrics": [
                    {
                        "$group": {
                            "_id": None,
                            "totalMembers": {"$sum": "$memberSummary.totalMembers"},
                            "totalActiveMembers": {"$sum": "$memberSummary.activeMembers"},
                            "totalInactiveMembers": {"$sum": "$memberSummary.inactiveMembers"},
                            "avgMembersPerEmployer": {"$avg": "$memberSummary.totalMembers"},
                            "maxMembers": {"$max": "$memberSummary.totalMembers"},
                            "minMembers": {"$min": "$memberSummary.totalMembers"}
                        }
                    }
                ],
                "employersByMemberCount": [
                    {
                        "$bucket": {
                            "groupBy": "$memberSummary.totalMembers",
                            "boundaries": [0, 10, 50, 100, 250, 500, 1000, 5000],
                            "default": "5000+",
                            "output": {
                                "employerCount": {"$sum": 1},
                                "totalMembers": {"$sum": "$memberSummary.totalMembers"}
                            }
                        }
                    }
                ],
                "genderDistribution": [
                    {
                        "$group": {
                            "_id": None,
                            "totalMale": {"$sum": "$memberSummary.membersByGender.Male"},
                            "totalFemale": {"$sum": "$memberSummary.membersByGender.Female"}
                        }
                    }
                ],
                "jobCategoryDistribution": [
                    {
                        "$project": {
                            "categories": {"$objectToArray": "$memberSummary.membersByJobCategory"}
                        }
                    },
                    {"$unwind": "$categories"},
                    {
                        "$group": {
                            "_id": "$categories.k",
                            "totalMembers": {"$sum": "$categories.v"}
                        }
                    },
                    {"$sort": {"totalMembers": -1}}
                ],
                "ageGroupDistribution": [
                    {
                        "$project": {
                            "ageGroups": {"$objectToArray": "$memberSummary.membersByAgeGroup"}
                        }
                    },
                    {"$unwind": "$ageGroups"},
                    {
                        "$group": {
                            "_id": "$ageGroups.k",
                            "totalMembers": {"$sum": "$ageGroups.v"}
                        }
                    },
                    {"$sort": {"_id": 1}}
                ]
            }
        },
        {
            "$addFields": {
                "_id": "workforce_summary",
                "viewType": "workforce",
                "refreshedAt": "$$NOW",
                "dataSource": "employers"
            }
        },
        {
            "$merge": {
                "into": "mv_employer_workforce",
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


def get_employer_submissions_pipeline() -> List[Dict[str, Any]]:
    """
    Pipeline for mv_employer_submissions materialized view.

    Refresh frequency: Daily (has $unwind - slower)
    Size: Small (~12-24 documents, one per month)
    Has $unwind: ⚠️ Slower, refresh less frequently

    Returns:
        Aggregation pipeline
    """
    return [
        # Unwind recent submissions
        {"$unwind": "$recentSubmissions"},

        # Group by month
        {
            "$group": {
                "_id": "$recentSubmissions.contributionMonth",
                "totalContribution": {"$sum": "$recentSubmissions.totalContribution"},
                "totalEmployerContribution": {"$sum": "$recentSubmissions.totalEmployerContribution"},
                "totalEmployeeContribution": {"$sum": "$recentSubmissions.totalEmployeeContribution"},
                "totalWages": {"$sum": "$recentSubmissions.totalWages"},
                "totalMembers": {"$sum": "$recentSubmissions.totalMembers"},
                "uniqueEmployers": {"$addToSet": "$employerId"},
                "avgContribution": {"$avg": "$recentSubmissions.totalContribution"},
                "avgWage": {
                    "$avg": {
                        "$divide": ["$recentSubmissions.totalWages", "$recentSubmissions.totalMembers"]
                    }
                },
                "onTimeSubmissions": {
                    "$sum": {"$cond": ["$recentSubmissions.isLateSubmission", 0, 1]}
                },
                "lateSubmissions": {
                    "$sum": {"$cond": ["$recentSubmissions.isLateSubmission", 1, 0]}
                },
                "acceptedSubmissions": {
                    "$sum": {"$cond": [{"$eq": ["$recentSubmissions.submissionStatus", "Accepted"]}, 1, 0]}
                },
                "pendingSubmissions": {
                    "$sum": {"$cond": [{"$eq": ["$recentSubmissions.submissionStatus", "Pending"]}, 1, 0]}
                },
                "rejectedSubmissions": {
                    "$sum": {"$cond": [{"$eq": ["$recentSubmissions.submissionStatus", "Rejected"]}, 1, 0]}
                },
                "totalLateCharges": {"$sum": "$recentSubmissions.latePaymentCharges"},
                "iAkaunSubmissions": {
                    "$sum": {"$cond": [{"$eq": ["$recentSubmissions.submissionMethod", "i-Akaun Online"]}, 1, 0]}
                },
                "counterSubmissions": {
                    "$sum": {"$cond": [{"$eq": ["$recentSubmissions.submissionMethod", "Counter"]}, 1, 0]}
                }
            }
        },

        # Calculate derived metrics
        {
            "$addFields": {
                "employerCount": {"$size": "$uniqueEmployers"},
                "onTimeRate": {
                    "$divide": [
                        "$onTimeSubmissions",
                        {"$add": ["$onTimeSubmissions", "$lateSubmissions"]}
                    ]
                },
                "acceptanceRate": {
                    "$divide": [
                        "$acceptedSubmissions",
                        {"$add": ["$acceptedSubmissions", "$pendingSubmissions", "$rejectedSubmissions"]}
                    ]
                },
                "digitalAdoptionRate": {
                    "$divide": [
                        "$iAkaunSubmissions",
                        {"$add": ["$iAkaunSubmissions", "$counterSubmissions"]}
                    ]
                },
                "avgMembersPerEmployer": {
                    "$divide": ["$totalMembers", {"$size": "$uniqueEmployers"}]
                }
            }
        },

        # Project final shape
        {
            "$project": {
                "_id": 0,
                "month": "$_id",
                "totalContribution": {"$round": ["$totalContribution", 2]},
                "totalEmployerContribution": {"$round": ["$totalEmployerContribution", 2]},
                "totalEmployeeContribution": {"$round": ["$totalEmployeeContribution", 2]},
                "totalWages": {"$round": ["$totalWages", 2]},
                "totalMembers": 1,
                "employerCount": 1,
                "avgContribution": {"$round": ["$avgContribution", 2]},
                "avgWage": {"$round": ["$avgWage", 2]},
                "avgMembersPerEmployer": {"$round": ["$avgMembersPerEmployer", 2]},
                "onTimeSubmissions": 1,
                "lateSubmissions": 1,
                "onTimeRate": {"$round": ["$onTimeRate", 4]},
                "acceptedSubmissions": 1,
                "pendingSubmissions": 1,
                "rejectedSubmissions": 1,
                "acceptanceRate": {"$round": ["$acceptanceRate", 4]},
                "totalLateCharges": {"$round": ["$totalLateCharges", 2]},
                "digitalAdoptionRate": {"$round": ["$digitalAdoptionRate", 4]},
                "iAkaunSubmissions": 1,
                "counterSubmissions": 1
            }
        },

        # Sort by month descending
        {"$sort": {"month": -1}},

        # Limit to last 24 months
        {"$limit": 24},

        # Add metadata
        {
            "$addFields": {
                "viewType": "submission_trends",
                "refreshedAt": "$$NOW",
                "dataSource": "employers"
            }
        },

        # Merge into collection
        {
            "$merge": {
                "into": "mv_employer_submissions",
                "on": "month",
                "whenMatched": "replace",
                "whenNotMatched": "insert"
            }
        }
    ]


# =======================
# REFRESH FUNCTIONS
# =======================

async def refresh_member_demographics(db):
    """Refresh member demographics materialized view."""
    logger.info("Refreshing member demographics...")
    pipeline = get_member_demographics_pipeline()
    await db.members.aggregate(pipeline).to_list(None)
    logger.info("✅ Member demographics refreshed")


async def refresh_member_balances(db):
    """Refresh member balances materialized view."""
    logger.info("Refreshing member balances...")
    pipeline = get_member_balances_pipeline()
    await db.members.aggregate(pipeline).to_list(None)
    logger.info("✅ Member balances refreshed")


async def refresh_member_contribution_trends(db):
    """Refresh member contribution trends materialized view."""
    logger.info("Refreshing member contribution trends...")
    pipeline = get_member_contribution_trends_pipeline()
    await db.members.aggregate(pipeline).to_list(None)
    logger.info("✅ Member contribution trends refreshed")


async def refresh_member_compliance(db):
    """Refresh member compliance materialized view."""
    logger.info("Refreshing member compliance...")
    pipeline = get_member_compliance_pipeline()
    await db.members.aggregate(pipeline).to_list(None)
    logger.info("✅ Member compliance refreshed")


async def refresh_employer_profiles(db):
    """Refresh employer profiles materialized view."""
    logger.info("Refreshing employer profiles...")
    pipeline = get_employer_profiles_pipeline()
    await db.employers.aggregate(pipeline).to_list(None)
    logger.info("✅ Employer profiles refreshed")


async def refresh_employer_compliance(db):
    """Refresh employer compliance materialized view."""
    logger.info("Refreshing employer compliance...")
    pipeline = get_employer_compliance_pipeline()
    await db.employers.aggregate(pipeline).to_list(None)
    logger.info("✅ Employer compliance refreshed")


async def refresh_employer_workforce(db):
    """Refresh employer workforce materialized view."""
    logger.info("Refreshing employer workforce...")
    pipeline = get_employer_workforce_pipeline()
    await db.employers.aggregate(pipeline).to_list(None)
    logger.info("✅ Employer workforce refreshed")


async def refresh_employer_submissions(db):
    """Refresh employer submissions materialized view."""
    logger.info("Refreshing employer submissions...")
    pipeline = get_employer_submissions_pipeline()
    await db.employers.aggregate(pipeline).to_list(None)
    logger.info("✅ Employer submissions refreshed")


async def refresh_all_views(db):
    """Refresh all materialized views."""
    logger.info("🚀 Refreshing all materialized views...")

    # Member views
    await refresh_member_demographics(db)
    await refresh_member_balances(db)
    await refresh_member_contribution_trends(db)
    await refresh_member_compliance(db)

    # Employer views
    await refresh_employer_profiles(db)
    await refresh_employer_compliance(db)
    await refresh_employer_workforce(db)
    await refresh_employer_submissions(db)

    logger.info("✅ All materialized views refreshed successfully!")
