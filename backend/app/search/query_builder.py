"""
Atlas Search query builder for Members and Employers.

This module provides utilities to build compound Atlas Search queries
with proper filtering, faceting, and scoring.
"""
from typing import Optional, Dict, Any, List


def build_text_search_clause(
    search_text: str,
    paths: List[str],
    fuzzy: bool = False
) -> Dict[str, Any]:
    """
    Build a text search clause for compound operator.

    Args:
        search_text: Text to search for
        paths: Field paths to search in
        fuzzy: Enable fuzzy matching

    Returns:
        Text search clause
    """
    clause = {
        "text": {
            "query": search_text,
            "path": paths
        }
    }

    if fuzzy:
        clause["text"]["fuzzy"] = {
            "maxEdits": 1,
            "prefixLength": 2
        }

    return clause


def build_autocomplete_clause(
    search_text: str,
    path: str,
    fuzzy: bool = True
) -> Dict[str, Any]:
    """
    Build an autocomplete search clause.

    Args:
        search_text: Text to autocomplete
        path: Field path with autocomplete index
        fuzzy: Enable fuzzy matching

    Returns:
        Autocomplete search clause
    """
    clause = {
        "autocomplete": {
            "query": search_text,
            "path": path
        }
    }

    if fuzzy:
        clause["autocomplete"]["fuzzy"] = {
            "maxEdits": 1,
            "prefixLength": 2
        }

    return clause


def build_filter_clause(
    path: str,
    values: List[Any],
    operator: str = "in"
) -> Dict[str, Any]:
    """
    Build a filter clause for multi-select filters.

    Args:
        path: Field path to filter on
        values: List of values to match
        operator: Filter operator ("in", "equals", etc.)

    Returns:
        Filter clause
    """
    if operator == "in":
        return {
            "in": {
                "path": path,
                "value": values
            }
        }
    elif operator == "equals":
        return {
            "equals": {
                "path": path,
                "value": values[0] if values else None
            }
        }
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def build_range_clause(
    path: str,
    min_value: Optional[Any] = None,
    max_value: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Build a range filter clause for numbers or dates.

    Args:
        path: Field path to filter on
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)

    Returns:
        Range filter clause
    """
    range_clause = {
        "range": {
            "path": path
        }
    }

    if min_value is not None:
        range_clause["range"]["gte"] = min_value

    if max_value is not None:
        range_clause["range"]["lte"] = max_value

    return range_clause


# Filter mappings for members (filter_key -> MongoDB path)
MEMBER_FILTER_MAPPING = {
    "account_status": "accountInfo.accountStatus",
    "region": "personalInfo.region",
    "generation": "personalInfo.generationGroup",
    "job_category": "employmentProfile.jobCategory",
    "risk_score": "complianceFlags.riskScore",
    "employment_status": "employmentProfile.employmentStatus",
}

# Filter mappings for employers (filter_key -> MongoDB path)
EMPLOYER_FILTER_MAPPING = {
    "account_status": "accountStatus.status",
    "sector": "companyProfile.industryClassification.sector",
    "company_size": "companyProfile.companySize",
    "state": "companyProfile.businessAddress.state",
    "account_type": "accountStatus.accountType",
    "risk_rating": "complianceStatus.riskRating",
    "product_tags": "productTags",
}


def build_members_compound_operator(
    search_text: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build compound operator for member search.

    Args:
        search_text: Optional text to search for
        filters: Optional filters dict with keys:
            - account_status: List[str]
            - region: List[str]
            - generation: List[str]
            - job_category: List[str]
            - risk_score: List[str]
            - employment_status: List[str]
            - min_balance: float
            - max_balance: float

    Returns:
        Compound operator for Atlas Search
    """
    compound = {
        "must": [],
        "should": [],
        "filter": []
    }

    # Add text search if provided
    if search_text:
        # Primary text search on name, ID, IC number
        compound["must"].append(
            build_text_search_clause(
                search_text,
                ["personalInfo.fullName", "memberId", "icNumber"],
                fuzzy=True
            )
        )

        # Boost autocomplete on name
        compound["should"].append({
            **build_autocomplete_clause(search_text, "personalInfo.fullName"),
            "score": {"boost": {"value": 2.0}}
        })

    # Apply list-based filters using loop
    if filters:
        for filter_key, mongo_path in MEMBER_FILTER_MAPPING.items():
            if filters.get(filter_key):
                compound["filter"].append(
                    build_filter_clause(mongo_path, filters[filter_key])
                )

        # Handle range filter for balance (special case)
        if filters.get("min_balance") is not None or filters.get("max_balance") is not None:
            compound["filter"].append(
                build_range_clause(
                    "accountInfo.totalBalance",
                    filters.get("min_balance"),
                    filters.get("max_balance")
                )
            )

    # Remove empty arrays
    compound = {k: v for k, v in compound.items() if v}

    # If compound is empty, return match all
    if not compound:
        return {}

    return compound


def build_employers_compound_operator(
    search_text: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build compound operator for employer search.

    Args:
        search_text: Optional text to search for
        filters: Optional filters dict with keys:
            - account_status: List[str]
            - sector: List[str]
            - company_size: List[str]
            - state: List[str]
            - account_type: List[str]
            - risk_rating: List[str]
            - has_arrears: bool
            - has_legal_cases: bool
            - product_tags: List[str]

    Returns:
        Compound operator for Atlas Search
    """
    compound = {
        "must": [],
        "should": [],
        "filter": []
    }

    # Add text search if provided
    if search_text:
        # Primary text search on company name, ID, registration number
        compound["must"].append(
            build_text_search_clause(
                search_text,
                ["companyProfile.companyName", "employerId", "employerCode",
                 "companyProfile.registrationNumber"],
                fuzzy=True
            )
        )

        # Boost autocomplete on company name
        compound["should"].append({
            **build_autocomplete_clause(search_text, "companyProfile.companyName"),
            "score": {"boost": {"value": 2.0}}
        })

    # Apply list-based filters using loop
    if filters:
        for filter_key, mongo_path in EMPLOYER_FILTER_MAPPING.items():
            if filters.get(filter_key):
                compound["filter"].append(
                    build_filter_clause(mongo_path, filters[filter_key])
                )

        # Handle boolean filters (special cases)
        if filters.get("has_arrears") is not None:
            compound["filter"].append({
                "equals": {
                    "path": "complianceStatus.hasArrears",
                    "value": filters["has_arrears"]
                }
            })

        if filters.get("has_legal_cases") is not None:
            compound["filter"].append({
                "equals": {
                    "path": "complianceStatus.hasLegalCases",
                    "value": filters["has_legal_cases"]
                }
            })

    # Remove empty arrays
    compound = {k: v for k, v in compound.items() if v}

    # If compound is empty, return match all
    if not compound:
        return {}

    return compound


# Facet definitions for Members
MEMBERS_FACETS = {
    "accountStatusFacet": {
        "type": "string",
        "path": "accountInfo.accountStatus",
        "numBuckets": 10
    },
    "regionFacet": {
        "type": "string",
        "path": "personalInfo.region",
        "numBuckets": 20
    },
    "generationFacet": {
        "type": "string",
        "path": "personalInfo.generationGroup",
        "numBuckets": 10
    },
    "genderFacet": {
        "type": "string",
        "path": "personalInfo.gender",
        "numBuckets": 5
    },
    "jobCategoryFacet": {
        "type": "string",
        "path": "employmentProfile.jobCategory",
        "numBuckets": 15
    },
    "employmentStatusFacet": {
        "type": "string",
        "path": "employmentProfile.employmentStatus",
        "numBuckets": 5
    },
    "riskScoreFacet": {
        "type": "string",
        "path": "complianceFlags.riskScore",
        "numBuckets": 5
    },
    "balanceRangeFacet": {
        "type": "number",
        "path": "accountInfo.totalBalance",
        "boundaries": [0, 10000, 50000, 100000, 200000, 500000],
        "default": "other"
    }
}

# Facet definitions for Employers
EMPLOYERS_FACETS = {
    "accountStatusFacet": {
        "type": "string",
        "path": "accountStatus.status",
        "numBuckets": 10
    },
    "sectorFacet": {
        "type": "string",
        "path": "companyProfile.industryClassification.sector",
        "numBuckets": 25
    },
    "companySizeFacet": {
        "type": "string",
        "path": "companyProfile.companySize",
        "numBuckets": 5
    },
    "stateFacet": {
        "type": "string",
        "path": "companyProfile.businessAddress.state",
        "numBuckets": 20
    },
    "accountTypeFacet": {
        "type": "string",
        "path": "accountStatus.accountType",
        "numBuckets": 5
    },
    "riskRatingFacet": {
        "type": "string",
        "path": "complianceStatus.riskRating",
        "numBuckets": 5
    },
    "contributionTrendFacet": {
        "type": "string",
        "path": "contributionStats.trend",
        "numBuckets": 5
    },
    "productTagsFacet": {
        "type": "string",
        "path": "productTags",
        "numBuckets": 10
    }
}


# Facet field mapping for parsing results
MEMBERS_FACET_MAPPING = {
    "accountStatusFacet": {
        "label": "Account Status",
        "key": "accountInfo.accountStatus"
    },
    "regionFacet": {
        "label": "Region",
        "key": "personalInfo.region"
    },
    "generationFacet": {
        "label": "Generation",
        "key": "personalInfo.generationGroup"
    },
    "genderFacet": {
        "label": "Gender",
        "key": "personalInfo.gender"
    },
    "jobCategoryFacet": {
        "label": "Job Category",
        "key": "employmentProfile.jobCategory"
    },
    "employmentStatusFacet": {
        "label": "Employment Status",
        "key": "employmentProfile.employmentStatus"
    },
    "riskScoreFacet": {
        "label": "Risk Score",
        "key": "complianceFlags.riskScore"
    },
    "balanceRangeFacet": {
        "label": "Balance Range",
        "key": "accountInfo.totalBalance"
    }
}

EMPLOYERS_FACET_MAPPING = {
    "accountStatusFacet": {
        "label": "Account Status",
        "key": "accountStatus.status"
    },
    "sectorFacet": {
        "label": "Sector",
        "key": "companyProfile.industryClassification.sector"
    },
    "companySizeFacet": {
        "label": "Company Size",
        "key": "companyProfile.companySize"
    },
    "stateFacet": {
        "label": "State",
        "key": "companyProfile.businessAddress.state"
    },
    "accountTypeFacet": {
        "label": "Account Type",
        "key": "accountStatus.accountType"
    },
    "riskRatingFacet": {
        "label": "Risk Rating",
        "key": "complianceStatus.riskRating"
    },
    "contributionTrendFacet": {
        "label": "Contribution Trend",
        "key": "contributionStats.trend"
    },
    "productTagsFacet": {
        "label": "Product Tags",
        "key": "productTags"
    }
}
