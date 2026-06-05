"""
Pydantic models for dashboard statistics and aggregated data.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardStats(BaseModel):
    """Base dashboard statistics model."""
    refreshed_at: datetime = Field(..., alias="refreshedAt")
    view_type: str = Field(..., alias="viewType")
    data_source: str = Field(..., alias="dataSource")

    model_config = {"populate_by_name": True}


class MemberDemographics(DashboardStats):
    """Member demographics statistics."""
    total_members: List[Dict[str, int]] = Field(..., alias="totalMembers")
    by_gender: List[Dict[str, Any]] = Field(..., alias="byGender")
    by_region: List[Dict[str, Any]] = Field(..., alias="byRegion")
    by_generation_group: List[Dict[str, Any]] = Field(..., alias="byGenerationGroup")
    by_job_category: List[Dict[str, Any]] = Field(..., alias="byJobCategory")
    by_account_status: List[Dict[str, Any]] = Field(..., alias="byAccountStatus")
    by_risk_score: List[Dict[str, Any]] = Field(..., alias="byRiskScore")
    by_employment_status: List[Dict[str, Any]] = Field(..., alias="byEmploymentStatus")
    record_count: Optional[int] = Field(None, alias="recordCount")

    model_config = {"populate_by_name": True}


class MemberBalances(DashboardStats):
    """Member balance statistics."""
    total_balances: List[Dict[str, Any]] = Field(..., alias="totalBalances")
    balance_distribution: List[Dict[str, Any]] = Field(..., alias="balanceDistribution")
    balance_percentiles: List[Dict[str, Any]] = Field(..., alias="balancePercentiles")
    akaun1_distribution: List[Dict[str, Any]] = Field(..., alias="akaun1Distribution")
    akaun2_distribution: List[Dict[str, Any]] = Field(..., alias="akaun2Distribution")

    model_config = {"populate_by_name": True}


class ContributionTrend(BaseModel):
    """Monthly contribution trend data."""
    month: str
    total_contribution: float = Field(..., alias="totalContribution")
    total_wages: float = Field(..., alias="totalWages")
    employer_contribution: float = Field(..., alias="employerContribution")
    employee_contribution: float = Field(..., alias="employeeContribution")
    member_count: int = Field(..., alias="memberCount")
    avg_wage: float = Field(..., alias="avgWage")
    avg_contribution: float = Field(..., alias="avgContribution")
    accepted_count: int = Field(..., alias="acceptedCount")
    pending_count: int = Field(..., alias="pendingCount")
    late_payment_count: int = Field(..., alias="latePaymentCount")
    on_time_rate: float = Field(..., alias="onTimeRate")

    model_config = {"populate_by_name": True}


class MemberCompliance(DashboardStats):
    """Member compliance statistics."""
    eligibility_summary: List[Dict[str, Any]] = Field(..., alias="eligibilitySummary")
    compliance_summary: List[Dict[str, Any]] = Field(..., alias="complianceSummary")
    risk_distribution: List[Dict[str, Any]] = Field(..., alias="riskDistribution")
    recent_flags: List[Dict[str, Any]] = Field(..., alias="recentFlags")
    gap_analysis: List[Dict[str, Any]] = Field(..., alias="gapAnalysis")

    model_config = {"populate_by_name": True}


class MemberDashboardStats(BaseModel):
    """Complete member dashboard statistics."""
    demographics: Optional[MemberDemographics] = None
    balances: Optional[MemberBalances] = None
    compliance: Optional[MemberCompliance] = None
    contribution_trends: Optional[List[ContributionTrend]] = Field(None, alias="contributionTrends")
    refreshed_at: Optional[datetime] = Field(None, alias="refreshedAt")

    model_config = {"populate_by_name": True}


class EmployerProfiles(DashboardStats):
    """Employer profile statistics."""
    total_employers: List[Dict[str, int]] = Field(..., alias="totalEmployers")
    by_account_status: List[Dict[str, Any]] = Field(..., alias="byAccountStatus")
    by_account_type: List[Dict[str, Any]] = Field(..., alias="byAccountType")
    by_sector: List[Dict[str, Any]] = Field(..., alias="bySector")
    by_company_size: List[Dict[str, Any]] = Field(..., alias="byCompanySize")
    by_state: List[Dict[str, Any]] = Field(..., alias="byState")
    by_risk_rating: List[Dict[str, Any]] = Field(..., alias="byRiskRating")
    trend_analysis: List[Dict[str, Any]] = Field(..., alias="trendAnalysis")
    by_product_tags: List[Dict[str, Any]] = Field(..., alias="byProductTags")
    total_count: Optional[int] = Field(None, alias="totalCount")

    model_config = {"populate_by_name": True}


class EmployerCompliance(DashboardStats):
    """Employer compliance statistics."""
    compliance_metrics: List[Dict[str, Any]] = Field(..., alias="complianceMetrics")
    arrears_by_risk_rating: List[Dict[str, Any]] = Field(..., alias="arrearsByRiskRating")
    legal_cases_by_type: List[Dict[str, Any]] = Field(..., alias="legalCasesByType")
    audit_compliance: List[Dict[str, Any]] = Field(..., alias="auditCompliance")
    on_time_payment_distribution: List[Dict[str, Any]] = Field(..., alias="onTimePaymentDistribution")

    model_config = {"populate_by_name": True}


class EmployerWorkforce(DashboardStats):
    """Employer workforce statistics."""
    workforce_metrics: List[Dict[str, Any]] = Field(..., alias="workforceMetrics")
    employers_by_member_count: List[Dict[str, Any]] = Field(..., alias="employersByMemberCount")
    gender_distribution: List[Dict[str, Any]] = Field(..., alias="genderDistribution")
    job_category_distribution: List[Dict[str, Any]] = Field(..., alias="jobCategoryDistribution")
    age_group_distribution: List[Dict[str, Any]] = Field(..., alias="ageGroupDistribution")

    model_config = {"populate_by_name": True}


class SubmissionTrend(BaseModel):
    """Monthly submission trend data."""
    month: str
    total_contribution: float = Field(..., alias="totalContribution")
    total_employer_contribution: float = Field(..., alias="totalEmployerContribution")
    total_employee_contribution: float = Field(..., alias="totalEmployeeContribution")
    total_wages: float = Field(..., alias="totalWages")
    total_members: int = Field(..., alias="totalMembers")
    employer_count: int = Field(..., alias="employerCount")
    avg_contribution: float = Field(..., alias="avgContribution")
    avg_wage: float = Field(..., alias="avgWage")
    avg_members_per_employer: float = Field(..., alias="avgMembersPerEmployer")
    on_time_submissions: int = Field(..., alias="onTimeSubmissions")
    late_submissions: int = Field(..., alias="lateSubmissions")
    on_time_rate: float = Field(..., alias="onTimeRate")
    accepted_submissions: int = Field(..., alias="acceptedSubmissions")
    pending_submissions: int = Field(..., alias="pendingSubmissions")
    rejected_submissions: int = Field(..., alias="rejectedSubmissions")
    acceptance_rate: float = Field(..., alias="acceptanceRate")
    total_late_charges: float = Field(..., alias="totalLateCharges")
    digital_adoption_rate: float = Field(..., alias="digitalAdoptionRate")
    i_akaun_submissions: int = Field(..., alias="iAkaunSubmissions")
    counter_submissions: int = Field(..., alias="counterSubmissions")

    model_config = {"populate_by_name": True}


class EmployerDashboardStats(BaseModel):
    """Complete employer dashboard statistics."""
    profiles: Optional[EmployerProfiles] = None
    compliance: Optional[EmployerCompliance] = None
    workforce: Optional[EmployerWorkforce] = None
    submission_trends: Optional[List[SubmissionTrend]] = Field(None, alias="submissionTrends")
    refreshed_at: Optional[datetime] = Field(None, alias="refreshedAt")

    model_config = {"populate_by_name": True}
