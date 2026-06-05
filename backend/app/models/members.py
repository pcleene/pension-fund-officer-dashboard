"""
Pydantic models for Member (contributor) entities.
Matches the MongoDB schema defined in the project prompt.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
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


class PersonalInfo(BaseModel):
    """Personal information for a member."""
    full_name: str = Field(..., alias="fullName")
    date_of_birth: datetime = Field(..., alias="dateOfBirth")
    age: int
    gender: str
    nationality: str = "Malaysian"
    region: str
    generation_group: str = Field(..., alias="generationGroup")

    model_config = ConfigDict(populate_by_name=True)


class CurrentEmployer(BaseModel):
    """Current employer reference."""
    employer_id: str = Field(..., alias="employerId")
    employer_name: str = Field(..., alias="employerName")
    employer_code: str = Field(..., alias="employerCode")
    start_date: datetime = Field(..., alias="startDate")
    is_active: bool = Field(..., alias="isActive")

    model_config = ConfigDict(populate_by_name=True)


class EmploymentProfile(BaseModel):
    """Employment profile for a member."""
    job_category: str = Field(..., alias="jobCategory")
    current_employer: CurrentEmployer = Field(..., alias="currentEmployer")
    employment_status: str = Field(..., alias="employmentStatus")
    has_multiple_employers: bool = Field(..., alias="hasMultipleEmployers")

    model_config = ConfigDict(populate_by_name=True)


class AccountInfo(BaseModel):
    """Account information for a member."""
    account_status: str = Field(..., alias="accountStatus")
    akaun1_balance: float = Field(..., alias="akaun1Balance")
    akaun2_balance: float = Field(..., alias="akaun2Balance")
    total_balance: float = Field(..., alias="totalBalance")
    last_updated: datetime = Field(..., alias="lastUpdated")
    currency: str = "MYR"

    model_config = ConfigDict(populate_by_name=True)


class ContributionRecord(BaseModel):
    """Individual contribution record (embedded in recentContributions array)."""
    contribution_month: str = Field(..., alias="contributionMonth")
    submission_date: datetime = Field(..., alias="submissionDate")
    employer_id: str = Field(..., alias="employerId")
    employer_name: str = Field(..., alias="employerName")
    wage_reported: float = Field(..., alias="wageReported")
    employer_contribution: float = Field(..., alias="employerContribution")
    employee_contribution: float = Field(..., alias="employeeContribution")
    total_contribution: float = Field(..., alias="totalContribution")
    submission_status: str = Field(..., alias="submissionStatus")
    receiving_branch: str = Field(..., alias="receivingBranch")
    is_late_payment: bool = Field(..., alias="isLatePayment")
    arrears_days: int = Field(..., alias="arrearsDays")

    model_config = ConfigDict(populate_by_name=True)


class ContributionStats(BaseModel):
    """Contribution summary statistics."""
    total_months: int = Field(..., alias="totalMonths")
    consecutive_months: int = Field(..., alias="consecutiveMonths")
    last_date: datetime = Field(..., alias="lastDate")
    avg_monthly_wage: float = Field(..., alias="avgMonthlyWage")
    avg_monthly: float = Field(..., alias="avgMonthly")
    total_lifetime: float = Field(..., alias="totalLifetime")
    has_gaps: bool = Field(..., alias="hasGaps")
    gap_months: List[str] = Field(default_factory=list, alias="gapMonths")

    model_config = ConfigDict(populate_by_name=True)


class EmployerHistory(BaseModel):
    """Employer history entry."""
    employer_id: str = Field(..., alias="employerId")
    employer_name: str = Field(..., alias="employerName")
    start_date: datetime = Field(..., alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    is_active: bool = Field(..., alias="isActive")
    total_contributions: float = Field(..., alias="totalContributions")
    months_worked: int = Field(..., alias="monthsWorked")

    model_config = ConfigDict(populate_by_name=True)


class WithdrawalRecord(BaseModel):
    """Withdrawal history entry."""
    withdrawal_id: str = Field(..., alias="withdrawalId")
    withdrawal_type: str = Field(..., alias="withdrawalType")
    withdrawal_date: datetime = Field(..., alias="withdrawalDate")
    amount: float
    purpose: str
    approval_status: str = Field(..., alias="approvalStatus")

    model_config = ConfigDict(populate_by_name=True)


class EligibilityFlags(BaseModel):
    """Eligibility flags for various withdrawal types."""
    housing_withdrawal: bool = Field(..., alias="housingWithdrawal")
    education_withdrawal: bool = Field(..., alias="educationWithdrawal")
    medical_withdrawal: bool = Field(..., alias="medicalWithdrawal")
    retirement_age: bool = Field(..., alias="retirementAge")
    minimum_balance_reached: bool = Field(..., alias="minimumBalanceReached")

    model_config = ConfigDict(populate_by_name=True)


class ComplianceFlags(BaseModel):
    """Compliance and irregularities flags."""
    has_irregularities: bool = Field(..., alias="hasIrregularities")
    has_missing_contributions: bool = Field(..., alias="hasMissingContributions")
    has_wage_discrepancies: bool = Field(..., alias="hasWageDiscrepancies")
    has_active_complaints: bool = Field(..., alias="hasActiveComplaints")
    last_audit_date: datetime = Field(..., alias="lastAuditDate")
    risk_score: str = Field(..., alias="riskScore")

    model_config = ConfigDict(populate_by_name=True)


class Metadata(BaseModel):
    """Document metadata."""
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    last_accessed_by: Optional[str] = Field(None, alias="lastAccessedBy")
    data_source: str = Field(..., alias="dataSource")
    version: int = 1

    model_config = ConfigDict(populate_by_name=True)


class Member(BaseModel):
    """Complete member document model."""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    member_id: str = Field(..., alias="memberId")
    ic_number: str = Field(..., alias="icNumber")
    personal_info: PersonalInfo = Field(..., alias="personalInfo")
    employment_profile: EmploymentProfile = Field(..., alias="employmentProfile")
    account_info: AccountInfo = Field(..., alias="accountInfo")
    recent_contributions: List[ContributionRecord] = Field(
        default_factory=list, alias="recentContributions"
    )
    contribution_stats: ContributionStats = Field(..., alias="contributionStats")
    employer_history: List[EmployerHistory] = Field(
        default_factory=list, alias="employerHistory"
    )
    withdrawal_history: List[WithdrawalRecord] = Field(
        default_factory=list, alias="withdrawalHistory"
    )
    eligibility_flags: EligibilityFlags = Field(..., alias="eligibilityFlags")
    compliance_flags: ComplianceFlags = Field(..., alias="complianceFlags")
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


class MemberResponse(BaseModel):
    """API response for a single member."""
    member: Member
    message: Optional[str] = None


class MemberSearchResponse(BaseModel):
    """API response for member search results."""
    results: List[Member]
    total_count: Optional[int] = Field(None, alias="totalCount")
    pagination: dict
    facets: Optional[List[dict]] = None

    model_config = ConfigDict(populate_by_name=True)
