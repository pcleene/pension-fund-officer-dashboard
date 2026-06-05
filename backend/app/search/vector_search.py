"""
Vector search utilities using Anthropic Voyage AI embeddings.

This module provides semantic search capabilities using 512-dimensional
embeddings from Anthropic's Voyage Large 2 model.
"""
from typing import List, Dict, Any, Optional
import logging

from anthropic import Anthropic

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Anthropic client
anthropic_client = None
if settings.anthropic_api_key:
    anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
else:
    logger.warning("ANTHROPIC_API_KEY not set. Vector search will not be available.")


def generate_embedding(text: str) -> List[float]:
    """
    Generate 512-dimensional embedding using Anthropic Voyage Large 2.

    Args:
        text: Text to embed

    Returns:
        List of 512 floats representing the embedding vector

    Raises:
        RuntimeError: If Anthropic client is not initialized
        Exception: If embedding generation fails
    """
    if not anthropic_client:
        raise RuntimeError(
            "Anthropic client not initialized. Please set ANTHROPIC_API_KEY environment variable."
        )

    try:
        response = anthropic_client.embeddings.create(
            model=settings.voyage_model,
            input=text
        )

        embedding = response.embeddings[0]

        # Verify dimensions
        if len(embedding) != settings.voyage_dimensions:
            logger.warning(
                f"Expected {settings.voyage_dimensions} dimensions, got {len(embedding)}"
            )

        return embedding

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def generate_member_embedding_text(member_doc: Dict[str, Any]) -> str:
    """
    Create rich text representation for member semantic embedding.

    Args:
        member_doc: Member document

    Returns:
        Text representation optimized for semantic search
    """
    text_parts = [
        f"Member: {member_doc.get('personalInfo', {}).get('fullName', 'Unknown')}",
        f"ID: {member_doc.get('memberId', 'Unknown')}",
        f"Region: {member_doc.get('personalInfo', {}).get('region', 'Unknown')}",
        f"Job: {member_doc.get('employmentProfile', {}).get('jobCategory', 'Unknown')}",
        f"Employer: {member_doc.get('employmentProfile', {}).get('currentEmployer', {}).get('employerName', 'Unknown')}",
        f"Account Status: {member_doc.get('accountInfo', {}).get('accountStatus', 'Unknown')}",
        f"Balance: RM {member_doc.get('accountInfo', {}).get('totalBalance', 0):.2f}",
        f"Risk: {member_doc.get('complianceFlags', {}).get('riskScore', 'Unknown')}"
    ]

    # Add compliance context if relevant
    compliance = member_doc.get('complianceFlags', {})
    if compliance.get('hasMissingContributions'):
        text_parts.append("Has missing contributions")
    if compliance.get('hasWageDiscrepancies'):
        text_parts.append("Has wage discrepancies")
    if compliance.get('hasIrregularities'):
        text_parts.append("Has compliance irregularities")

    # Add eligibility context
    eligibility = member_doc.get('eligibilityFlags', {})
    eligible_for = []
    if eligibility.get('housingWithdrawal'):
        eligible_for.append("housing withdrawal")
    if eligibility.get('educationWithdrawal'):
        eligible_for.append("education withdrawal")
    if eligibility.get('medicalWithdrawal'):
        eligible_for.append("medical withdrawal")
    if eligibility.get('retirementAge'):
        eligible_for.append("retirement")

    if eligible_for:
        text_parts.append(f"Eligible for: {', '.join(eligible_for)}")

    return ". ".join(text_parts)


def generate_employer_embedding_text(employer_doc: Dict[str, Any]) -> str:
    """
    Create rich text representation for employer semantic embedding.

    Args:
        employer_doc: Employer document

    Returns:
        Text representation optimized for semantic search
    """
    company = employer_doc.get('companyProfile', {})
    compliance = employer_doc.get('complianceStatus', {})
    stats = employer_doc.get('contributionStats', {})

    text_parts = [
        f"Company: {company.get('companyName', 'Unknown')}",
        f"ID: {employer_doc.get('employerId', 'Unknown')}",
        f"Sector: {company.get('industryClassification', {}).get('sector', 'Unknown')}",
        f"Size: {company.get('companySize', 'Unknown')}",
        f"Location: {company.get('businessAddress', {}).get('state', 'Unknown')}",
        f"Employees: {employer_doc.get('memberSummary', {}).get('totalMembers', 0)}",
        f"Status: {employer_doc.get('accountStatus', {}).get('status', 'Unknown')}",
        f"Risk: {compliance.get('riskRating', 'Unknown')}"
    ]

    # Add compliance context
    if compliance.get('hasArrears'):
        text_parts.append(f"Arrears: RM {compliance.get('arrearsAmount', 0):.2f}")
    if compliance.get('hasLegalCases'):
        case_types = compliance.get('legalCaseTypes', [])
        if case_types:
            text_parts.append(f"Legal cases: {', '.join(case_types)}")

    # Add contribution trend
    trend = stats.get('trend', 'Unknown')
    text_parts.append(f"Contribution trend: {trend}")

    # Add on-time payment rate
    on_time_rate = stats.get('onTimeRate', 0)
    text_parts.append(f"On-time payment rate: {on_time_rate:.1%}")

    return ". ".join(text_parts)


async def vector_search_members(
    collection,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    num_candidates: int = 100
) -> Dict[str, Any]:
    """
    Perform semantic vector search on members collection.

    Args:
        collection: Members MongoDB collection
        query: Natural language query
        filters: Optional metadata filters to apply post-search
        limit: Number of results to return
        num_candidates: Number of candidates for vector search (should be > limit)

    Returns:
        Dict with results and pagination info
    """
    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        raise

    # Build vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.members_vector_index,
                "path": "semanticEmbedding",
                "queryVector": query_embedding,
                "numCandidates": num_candidates,
                "limit": limit
            }
        },
        {
            "$addFields": {
                "vectorScore": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # Add optional filters (post-vector search)
    if filters:
        match_filters = {}

        # Convert filter format to MongoDB query format
        if filters.get("account_status"):
            match_filters["accountInfo.accountStatus"] = {"$in": filters["account_status"]}
        if filters.get("region"):
            match_filters["personalInfo.region"] = {"$in": filters["region"]}
        if filters.get("risk_score"):
            match_filters["complianceFlags.riskScore"] = {"$in": filters["risk_score"]}
        if filters.get("min_balance") is not None or filters.get("max_balance") is not None:
            balance_filter = {}
            if filters.get("min_balance") is not None:
                balance_filter["$gte"] = filters["min_balance"]
            if filters.get("max_balance") is not None:
                balance_filter["$lte"] = filters["max_balance"]
            match_filters["accountInfo.totalBalance"] = balance_filter

        if match_filters:
            pipeline.append({"$match": match_filters})

    # Project fields
    pipeline.append({
        "$project": {
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
            "vectorScore": 1
        }
    })

    # Execute pipeline
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=limit)

    return {
        "results": results,
        "pagination": {
            "limit": limit,
            "hasMore": len(results) >= limit,
            "totalCount": len(results),
            "currentPageSize": len(results)
        },
        "query": query
    }


async def vector_search_employers(
    collection,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    num_candidates: int = 100
) -> Dict[str, Any]:
    """
    Perform semantic vector search on employers collection.

    Args:
        collection: Employers MongoDB collection
        query: Natural language query
        filters: Optional metadata filters to apply post-search
        limit: Number of results to return
        num_candidates: Number of candidates for vector search (should be > limit)

    Returns:
        Dict with results and pagination info
    """
    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        raise

    # Build vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.employers_vector_index,
                "path": "semanticEmbedding",
                "queryVector": query_embedding,
                "numCandidates": num_candidates,
                "limit": limit
            }
        },
        {
            "$addFields": {
                "vectorScore": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # Add optional filters (post-vector search)
    if filters:
        match_filters = {}

        # Convert filter format to MongoDB query format
        if filters.get("account_status"):
            match_filters["accountStatus.status"] = {"$in": filters["account_status"]}
        if filters.get("sector"):
            match_filters["companyProfile.industryClassification.sector"] = {"$in": filters["sector"]}
        if filters.get("state"):
            match_filters["companyProfile.businessAddress.state"] = {"$in": filters["state"]}
        if filters.get("risk_rating"):
            match_filters["complianceStatus.riskRating"] = {"$in": filters["risk_rating"]}
        if filters.get("has_arrears") is not None:
            match_filters["complianceStatus.hasArrears"] = filters["has_arrears"]
        if filters.get("has_legal_cases") is not None:
            match_filters["complianceStatus.hasLegalCases"] = filters["has_legal_cases"]

        if match_filters:
            pipeline.append({"$match": match_filters})

    # Project fields
    pipeline.append({
        "$project": {
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
            "vectorScore": 1
        }
    })

    # Execute pipeline
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=limit)

    return {
        "results": results,
        "pagination": {
            "limit": limit,
            "hasMore": len(results) >= limit,
            "totalCount": len(results),
            "currentPageSize": len(results)
        },
        "query": query
    }


async def hybrid_search(
    collection,
    text_query: str,
    semantic_query: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    text_weight: float = 0.4,
    vector_weight: float = 0.6
) -> Dict[str, Any]:
    """
    Perform hybrid search combining text and vector search.

    Args:
        collection: MongoDB collection
        text_query: Text search query
        semantic_query: Natural language query for vector search
        filters: Optional filters
        limit: Number of results
        text_weight: Weight for text search score (0.0 to 1.0)
        vector_weight: Weight for vector search score (0.0 to 1.0)

    Returns:
        Dict with combined results

    Note:
        This is an advanced feature. For most use cases, use either
        text search or vector search independently.
    """
    # TODO: Implement hybrid search
    # This would combine results from both text and vector search
    # with weighted scoring
    raise NotImplementedError("Hybrid search not yet implemented")
