"""
Cursor-based pagination utilities for Atlas Search.

This module provides utilities for efficient cursor-based pagination
using Atlas Search's searchSequenceToken feature.
"""
from typing import Dict, Any, List, Optional, Tuple
import logging

from app.search.query_builder import (
    MEMBERS_FACETS,
    EMPLOYERS_FACETS,
    MEMBERS_FACET_MAPPING,
    EMPLOYERS_FACET_MAPPING
)

logger = logging.getLogger(__name__)


def build_search_command(
    index_name: str,
    compound_operator: Dict[str, Any],
    facets: Optional[Dict[str, Any]] = None,
    cursor: Optional[str] = None,
    direction: str = "next",
    limit: int = 20,
    sort: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Build Atlas Search command with pagination support.

    Args:
        index_name: Name of the Atlas Search index
        compound_operator: Compound operator for filtering/searching
        facets: Facet definitions (optional)
        cursor: Pagination cursor (searchSequenceToken from previous results)
        direction: "next" or "prev"
        limit: Number of results to return
        sort: Sort specification (must include _id for deterministic ordering)

    Returns:
        Complete $search command
    """
    # Default sort: by updatedAt descending, then _id for deterministic ordering
    if sort is None:
        sort = {"metadata.updatedAt": -1, "_id": 1}

    # Build base search command
    search_cmd: Dict[str, Any] = {
        "index": index_name,
        "sort": sort,
        "count": {"type": "total"}
    }

    # Add compound operator or facet
    if facets:
        # Use facet operator for faceted search
        search_cmd["facet"] = {
            "operator": {
                "compound": compound_operator
            } if compound_operator else {},
            "facets": facets
        }
    else:
        # Use compound operator directly
        if compound_operator:
            search_cmd["compound"] = compound_operator

    # Add pagination cursor (CRITICAL: at top level, not inside compound!)
    if cursor:
        if direction == "next":
            search_cmd["searchAfter"] = cursor
        elif direction == "prev":
            search_cmd["searchBefore"] = cursor
        else:
            raise ValueError(f"Invalid direction: {direction}. Must be 'next' or 'prev'")

    return search_cmd


def build_aggregation_pipeline(
    search_cmd: Dict[str, Any],
    limit: int,
    projection: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Build aggregation pipeline for Atlas Search with pagination.

    Args:
        search_cmd: Complete $search command
        limit: Number of results to fetch
        projection: Optional field projection

    Returns:
        Aggregation pipeline
    """
    pipeline = [
        # Stage 1: $search
        {"$search": search_cmd},

        # Stage 2: Add search metadata BEFORE $limit
        # CRITICAL: This must come before $limit to get pagination tokens
        {
            "$addFields": {
                "searchScore": {"$meta": "searchScore"},
                "paginationToken": {"$meta": "searchSequenceToken"}
            }
        },

        # Stage 3: Fetch limit + 1 to determine if more results exist
        {"$limit": limit + 1},

        # Stage 4: Use $facet to separate results from metadata
        {
            "$facet": {
                "results": [
                    {"$project": projection} if projection else {"$project": {}}
                ],
                "metadata": [
                    {"$replaceWith": "$$SEARCH_META"},
                    {"$limit": 1}
                ]
            }
        }
    ]

    return pipeline


async def execute_paginated_search(
    collection,
    search_cmd: Dict[str, Any],
    limit: int,
    projection: Optional[Dict[str, Any]] = None,
    direction: str = "next"
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Optional[List[Dict[str, Any]]]]:
    """
    Execute a paginated Atlas Search query.

    Args:
        collection: MongoDB collection
        search_cmd: Complete $search command
        limit: Number of results per page
        projection: Optional field projection
        direction: "next" or "prev"

    Returns:
        Tuple of (results, pagination_info, facets)
        - results: List of documents
        - pagination_info: Dict with pagination metadata
        - facets: Optional list of facets (if faceted search)
    """
    # Build pipeline
    pipeline = build_aggregation_pipeline(search_cmd, limit, projection)

    # Execute aggregation
    cursor = collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)

    if not result:
        # No results
        return [], {
            "limit": limit,
            "hasMore": False,
            "nextCursor": None,
            "prevCursor": None,
            "totalCount": 0,
            "currentPageSize": 0
        }, None

    # Extract results and metadata
    results_list = result[0].get("results", [])
    metadata = result[0].get("metadata", [{}])[0]

    # Parse facets if present
    facets = None
    if "facet" in metadata:
        facets = parse_facets(metadata["facet"], MEMBERS_FACET_MAPPING)  # Will be determined by caller

    # Determine pagination state
    has_more = len(results_list) > limit

    # Remove the extra document if we fetched limit + 1
    if has_more:
        results_list = results_list[:limit]

    # Extract cursors from first and last documents
    first_cursor = results_list[0].get("paginationToken") if results_list else None
    last_cursor = results_list[-1].get("paginationToken") if results_list else None

    # Determine next and previous cursors based on direction
    if direction == "next":
        next_cursor = last_cursor if has_more else None
        prev_cursor = first_cursor  # Can navigate back
    else:  # direction == "prev"
        next_cursor = last_cursor  # Can navigate forward
        prev_cursor = first_cursor if results_list else None

    # Get total count (lower bound estimate from Atlas Search)
    total_count = metadata.get("count", {}).get("lowerBound")

    pagination_info = {
        "limit": limit,
        "hasMore": has_more,
        "nextCursor": next_cursor,
        "prevCursor": prev_cursor,
        "totalCount": total_count,
        "currentPageSize": len(results_list)
    }

    return results_list, pagination_info, facets


def parse_facets(
    facet_data: Dict[str, Any],
    facet_mapping: Dict[str, Dict[str, str]]
) -> List[Dict[str, Any]]:
    """
    Parse facet results into UI-friendly format.

    Args:
        facet_data: Raw facet data from $$SEARCH_META
        facet_mapping: Mapping of facet keys to labels

    Returns:
        List of facets with buckets:
        [
            {
                "field": "Account Status",
                "fieldKey": "accountInfo.accountStatus",
                "buckets": [
                    {"value": "Active", "count": 8234},
                    {"value": "Dormant", "count": 1456},
                    ...
                ]
            },
            ...
        ]
    """
    facets = []

    for facet_key, config in facet_mapping.items():
        if facet_key in facet_data and "buckets" in facet_data[facet_key]:
            buckets = [
                {"value": bucket["_id"], "count": bucket["count"]}
                for bucket in facet_data[facet_key]["buckets"]
            ]

            facets.append({
                "field": config["label"],
                "fieldKey": config["key"],
                "buckets": buckets
            })

    return facets


def get_members_projection() -> Dict[str, Any]:
    """
    Get projection for member search results.

    Returns:
        Projection dict for $project stage
    """
    return {
        "_id": 1,
        "memberId": 1,
        "icNumber": 1,
        "personalInfo": 1,
        "employmentProfile": 1,
        "accountInfo": 1,
        "contributionStats": 1,
        "complianceFlags": 1,
        "eligibilityFlags": 1,
        "metadata": 1,
        "searchScore": 1,
        "paginationToken": 1
    }


def get_employers_projection() -> Dict[str, Any]:
    """
    Get projection for employer search results.

    Returns:
        Projection dict for $project stage
    """
    return {
        "_id": 1,
        "employerId": 1,
        "employerCode": 1,
        "companyProfile": 1,
        "accountStatus": 1,
        "memberSummary": 1,
        "productTags": 1,
        "contributionStats": 1,
        "complianceStatus": 1,
        "metadata": 1,
        "searchScore": 1,
        "paginationToken": 1
    }


async def search_with_pagination(
    collection,
    index_name: str,
    compound_operator: Dict[str, Any],
    facets_definition: Optional[Dict[str, Any]] = None,
    facet_mapping: Optional[Dict[str, Dict[str, str]]] = None,
    limit: int = 20,
    cursor: Optional[str] = None,
    direction: str = "next",
    projection: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    High-level function to execute paginated search with faceting.

    Args:
        collection: MongoDB collection
        index_name: Atlas Search index name
        compound_operator: Compound operator for search/filtering
        facets_definition: Facet definitions (None to disable faceting)
        facet_mapping: Mapping for parsing facet results
        limit: Number of results per page
        cursor: Pagination cursor
        direction: "next" or "prev"
        projection: Field projection
        sort: Sort specification

    Returns:
        Dict with results, pagination, and optional facets
    """
    # Build search command
    search_cmd = build_search_command(
        index_name=index_name,
        compound_operator=compound_operator,
        facets=facets_definition,
        cursor=cursor,
        direction=direction,
        limit=limit,
        sort=sort
    )

    # Execute search
    results, pagination_info, facets = await execute_paginated_search(
        collection=collection,
        search_cmd=search_cmd,
        limit=limit,
        projection=projection,
        direction=direction
    )

    # Parse facets if present and mapping provided
    if facets and facet_mapping:
        # Re-parse with correct mapping
        pipeline = build_aggregation_pipeline(search_cmd, limit, projection)
        cursor_obj = collection.aggregate(pipeline)
        result = await cursor_obj.to_list(length=1)
        if result and "metadata" in result[0]:
            metadata = result[0]["metadata"][0] if result[0]["metadata"] else {}
            if "facet" in metadata:
                facets = parse_facets(metadata["facet"], facet_mapping)

    return {
        "results": results,
        "pagination": pagination_info,
        "facets": facets
    }
