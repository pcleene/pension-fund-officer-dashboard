"""
Pydantic models for Employer (company) entities.
Matches the MongoDB schema defined in the project prompt.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class BusinessAddress(BaseModel):
    """Business address for employer."""
    street: str
    city: str
    state: str
    postcode: str
    country: str = "Malaysia"


class ContactInfo(BaseModel):
    """Contact information for employer."""
    phone: str
    email: str
    website: Optional[str] = None


class IndustryClassification(BaseModel):
    """Industry classification details."""
    msic_code: str = Field(..., alias="msicCode")
    msic_description: str = Field(..., alias="msicDescription")
    sector: str

    model_config = ConfigDict(populate_by_name=True)


class CompanyProfile(BaseModel):
    """Company profile information."""
    company_name: str = Field(..., alias="companyName")
    registration_number: str = Field(..., alias="registrationNumber")
    business_address: BusinessAddress = Field(..., alias="businessAddress")
    contact_info: ContactInfo = Field(..., alias="contactInfo")
    industry_classification: IndustryClassification = Field(..., alias="industryClassification")
    company_size: str = Field(..., alias="companySize")
    number_of_employees: int = Field(..., alias="numberOfEmployees")

    model_config = ConfigDict(populate_by_name=True)


class AccountStatus(BaseModel):
    """Account status for employer."""
    status: str
    registration_date: datetime = Field(..., alias="registrationDate")
    last_active_date: datetime = Field(..., alias="lastActiveDate")
    suspension_reason: Optional[str] = Field(None, alias="suspensionReason")
    account_type: str = Field(..., alias="accountType")

    model_config = ConfigDict(populate_by_name=True)


class MemberSummary(BaseModel):
    """Summary of members employed."""
    total_members: int = Field(..., alias="totalMembers")
    active_members: int = Field(..., alias="activeMembers")
    inactive_members: int = Field(..., alias="inactiveMembers")
    members_by_gender: Dict[str, int] = Field(..., alias="membersByGender")
    members_by_age_group: Dict[str, int] = Field(..., alias="membersByAgeGroup")
    members_by_job_category: Dict[str, int] = Field(..., alias="membersByJobCategory")
    last_updated: datetime = Field(..., alias="lastUpdated")

    model_config = ConfigDict(populate_by_name=True)


class ContributionSubmission(BaseModel):
    """Individual contribution submission record."""
    submission_id: str = Field(..., alias="submissionId")
    contribution_month: str = Field(..., alias="contributionMonth")
    submission_date: datetime = Field(..., alias="submissionDate")
    submission_method: str = Field(..., alias="submissionMethod")
    receiving_branch: str = Field(..., alias="receivingBranch")
    total_members: int = Field(..., alias="totalMembers")
    total_wages: float = Field(..., alias="totalWages")
    total_employer_contribution: float = Field(..., alias="totalEmployerContribution")
    total_employee_contribution: float = Field(..., alias="totalEmployeeContribution")
    total_contribution: float = Field(..., alias="totalContribution")
    submission_status: str = Field(..., alias="submissionStatus")
    validation_errors: List[str] = Field(default_factory=list, alias="validationErrors")
    payment_status: str = Field(..., alias="paymentStatus")
    payment_date: Optional[datetime] = Field(None, alias="paymentDate")
    payment_reference: Optional[str] = Field(None, alias="paymentReference")
    due_date: datetime = Field(..., alias="dueDate")
    is_late_submission: bool = Field(..., alias="isLateSubmission")
    late_days: int = Field(..., alias="lateDays")
    late_payment_charges: float = Field(..., alias="latePaymentCharges")
    processed_by: str = Field(..., alias="processedBy")
    processed_date: datetime = Field(..., alias="processedDate")
    remarks: str = ""

    model_config = ConfigDict(populate_by_name=True)


class ContributionStatistics(BaseModel):
    """Contribution statistics for employer."""
    total_lifetime: float = Field(..., alias="totalLifetime")
    avg_monthly: float = Field(..., alias="avgMonthly")
    last_12_months_total: float = Field(..., alias="last12MonthsTotal")
    trend: str
    on_time_rate: float = Field(..., alias="onTimeRate")
    total_late_payments: int = Field(..., alias="totalLatePayments")
    total_late_charges: float = Field(..., alias="totalLateCharges")

    model_config = ConfigDict(populate_by_name=True)


class ComplianceStatus(BaseModel):
    """Compliance and legal status for employer."""
    has_arrears: bool = Field(..., alias="hasArrears")
    arrears_amount: float = Field(..., alias="arrearsAmount")
    arrears_months: List[str] = Field(default_factory=list, alias="arrearsMonths")
    has_legal_cases: bool = Field(..., alias="hasLegalCases")
    legal_case_types: List[str] = Field(default_factory=list, alias="legalCaseTypes")
    active_cases: List[str] = Field(default_factory=list, alias="activeCases")
    last_audit_date: datetime = Field(..., alias="lastAuditDate")
    audit_result: str = Field(..., alias="auditResult")
    next_audit_date: datetime = Field(..., alias="nextAuditDate")
    risk_rating: str = Field(..., alias="riskRating")

    model_config = ConfigDict(populate_by_name=True)


class LegalCase(BaseModel):
    """Legal case details."""
    case_id: str = Field(..., alias="caseId")
    case_type: str = Field(..., alias="caseType")
    filed_date: datetime = Field(..., alias="filedDate")
    status: str
    amount_in_dispute: float = Field(..., alias="amountInDispute")
    description: str

    model_config = ConfigDict(populate_by_name=True)


class MemberReference(BaseModel):
    """Lightweight member reference in employer's member list."""
    member_id: str = Field(..., alias="memberId")
    full_name: str = Field(..., alias="fullName")
    ic_number: str = Field(..., alias="icNumber")
    employment_status: str = Field(..., alias="employmentStatus")
    start_date: datetime = Field(..., alias="startDate")
    last_contribution_month: str = Field(..., alias="lastContributionMonth")
    average_wage: float = Field(..., alias="averageWage")

    model_config = ConfigDict(populate_by_name=True)


class Metadata(BaseModel):
    """Document metadata."""
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_accessed_by: Optional[str] = Field(None, alias="lastAccessedBy")
    data_source: str = Field(..., alias="dataSource")
    version: int = 1

    model_config = ConfigDict(populate_by_name=True)


class Employer(BaseModel):
    """Complete employer document model."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    employer_id: str = Field(..., alias="employerId")
    employer_code: str = Field(..., alias="employerCode")
    company_profile: CompanyProfile = Field(..., alias="companyProfile")
    account_status: AccountStatus = Field(..., alias="accountStatus")
    member_summary: MemberSummary = Field(..., alias="memberSummary")
    product_tags: List[str] = Field(default_factory=list, alias="productTags")
    recent_submissions: List[ContributionSubmission] = Field(
        default_factory=list, alias="recentSubmissions"
    )
    contribution_stats: ContributionStatistics = Field(..., alias="contributionStats")
    compliance_status: ComplianceStatus = Field(..., alias="complianceStatus")
    legal_cases: List[LegalCase] = Field(default_factory=list, alias="legalCases")
    member_list: List[MemberReference] = Field(default_factory=list, alias="memberList")
    metadata: Metadata
    semantic_embedding: Optional[List[float]] = Field(None, alias="semanticEmbedding")

    # For search results
    search_score: Optional[float] = Field(None, alias="searchScore")
    vector_score: Optional[float] = Field(None, alias="vectorScore")
    pagination_token: Optional[str] = Field(None, alias="paginationToken")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class EmployerResponse(BaseModel):
    """API response for a single employer."""
    employer: Employer
    message: Optional[str] = None


class EmployerSearchResponse(BaseModel):
    """API response for employer search results."""
    results: List[Employer]
    total_count: Optional[int] = Field(None, alias="totalCount")
    pagination: dict
    facets: Optional[List[dict]] = None

    model_config = ConfigDict(populate_by_name=True)
