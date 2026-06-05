"""
Sample data generation script for PensionFund Officer Dashboard.

This script generates realistic Malaysian PensionFund data for testing purposes.

Usage:
    python generate_sample_data.py --members 1000 --employers 100
    python generate_sample_data.py --members 1000000 --employers 650000  # Full scale
    python generate_sample_data.py --clear  # Clear all data

Requirements:
    - MongoDB Atlas connection configured
    - Faker library: pip install faker
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import argparse
import sys

from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

# Initialize Faker with multiple locales for Malaysian diversity
fake = Faker(['ms_MY', 'en_MY', 'zh_CN', 'ta_IN'])
Faker.seed(42)  # For reproducible data

# ============================================================================
# MALAYSIAN-SPECIFIC DATA
# ============================================================================

MALAYSIAN_STATES = [
    "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan",
    "Pahang", "Penang", "Perak", "Perlis", "Sabah", "Sarawak",
    "Selangor", "Terengganu", "Kuala Lumpur", "Labuan", "Putrajaya"
]

# Weighted distribution - more populous states have higher weights
STATE_WEIGHTS = {
    "Selangor": 0.20,
    "Kuala Lumpur": 0.15,
    "Johor": 0.12,
    "Penang": 0.08,
    "Perak": 0.08,
    "Sabah": 0.07,
    "Sarawak": 0.07,
    "Kedah": 0.05,
    "Kelantan": 0.05,
    "Pahang": 0.04,
    "Negeri Sembilan": 0.03,
    "Terengganu": 0.03,
    "Malacca": 0.02,
    "Perlis": 0.01,
    "Labuan": 0.005,
    "Putrajaya": 0.005
}

MALAYSIAN_CITIES = {
    "Kuala Lumpur": ["Kuala Lumpur"],
    "Selangor": ["Petaling Jaya", "Shah Alam", "Subang Jaya", "Cyberjaya", "Puchong", "Klang"],
    "Johor": ["Johor Bahru", "Skudai", "Batu Pahat", "Muar"],
    "Penang": ["George Town", "Butterworth", "Bukit Mertajam"],
    "Perak": ["Ipoh", "Taiping"],
    "Sabah": ["Kota Kinabalu", "Sandakan"],
    "Sarawak": ["Kuching", "Miri", "Sibu"],
    "Kedah": ["Alor Setar", "Sungai Petani"],
    "Kelantan": ["Kota Bharu"],
    "Pahang": ["Kuantan", "Temerloh"],
    "Negeri Sembilan": ["Seremban"],
    "Terengganu": ["Kuala Terengganu"],
    "Malacca": ["Malacca City"],
    "Perlis": ["Kangar"],
    "Labuan": ["Victoria"],
    "Putrajaya": ["Putrajaya"]
}

JOB_CATEGORIES = [
    "Professional", "Technical", "Clerical", "Executive",
    "General", "Skilled", "Semi-skilled", "Managerial"
]

# Job category weights (realistic distribution)
JOB_CATEGORY_WEIGHTS = [0.15, 0.20, 0.25, 0.10, 0.15, 0.10, 0.03, 0.02]

EMPLOYMENT_STATUSES = ["Active", "Inactive", "Resigned", "Transferred"]
EMPLOYMENT_STATUS_WEIGHTS = [0.70, 0.15, 0.10, 0.05]

ACCOUNT_STATUSES = ["Active", "Inactive", "Suspended", "Dormant"]
ACCOUNT_STATUS_WEIGHTS = [0.75, 0.15, 0.05, 0.05]

RISK_SCORES = ["Low", "Medium", "High", "Critical"]
RISK_SCORE_WEIGHTS = [0.70, 0.20, 0.08, 0.02]

GENERATION_GROUPS = ["Gen Z", "Millennials", "Gen X", "Baby Boomers"]

# Industry sectors with MSIC codes
INDUSTRY_SECTORS = [
    {"sector": "Information Technology", "msic": "62000", "description": "Computer programming, consultancy and related activities"},
    {"sector": "Manufacturing", "msic": "25000", "description": "Manufacture of fabricated metal products"},
    {"sector": "Finance", "msic": "64000", "description": "Financial service activities"},
    {"sector": "Healthcare", "msic": "86000", "description": "Human health activities"},
    {"sector": "Education", "msic": "85000", "description": "Education"},
    {"sector": "Retail", "msic": "47000", "description": "Retail trade"},
    {"sector": "Construction", "msic": "41000", "description": "Construction of buildings"},
    {"sector": "Transportation", "msic": "49000", "description": "Land transport"},
    {"sector": "Hospitality", "msic": "56000", "description": "Food and beverage service activities"},
    {"sector": "Professional Services", "msic": "69000", "description": "Legal and accounting activities"},
    {"sector": "Real Estate", "msic": "68000", "description": "Real estate activities"},
    {"sector": "Telecommunications", "msic": "61000", "description": "Telecommunications"},
    {"sector": "Agriculture", "msic": "01000", "description": "Crop and animal production"},
    {"sector": "Energy", "msic": "35000", "description": "Electricity, gas, steam supply"},
    {"sector": "Logistics", "msic": "52000", "description": "Warehousing and support activities"}
]

COMPANY_SIZES = ["Micro", "Small", "Medium", "Large"]
COMPANY_SIZE_WEIGHTS = [0.40, 0.35, 0.20, 0.05]

# Company size to employee count mapping
COMPANY_SIZE_EMPLOYEES = {
    "Micro": (1, 5),
    "Small": (6, 30),
    "Medium": (31, 75),
    "Large": (76, 200)
}

EMPLOYER_ACCOUNT_TYPES = ["Standard", "Priority", "Corporate", "SME"]
EMPLOYER_ACCOUNT_TYPE_WEIGHTS = [0.50, 0.10, 0.15, 0.25]

SUBMISSION_METHODS = ["E-Submission", "Manual", "Bank Transfer", "Counter"]
SUBMISSION_STATUS = ["Approved", "Pending", "Rejected", "Under Review"]
PAYMENT_STATUS = ["Paid", "Pending", "Partially Paid", "Overdue"]

RECEIVING_BRANCHES = [
    "KL Main", "Johor Bahru", "Penang", "Ipoh", "Kuching",
    "Kota Kinabalu", "Shah Alam", "Petaling Jaya", "Klang"
]

PRODUCT_TAGS = [
    "i-Akaun", "i-Invest", "i-Saraan", "Flexi Withdrawal",
    "Housing Withdrawal", "Education Withdrawal", "Medical Withdrawal"
]

WITHDRAWAL_TYPES = [
    "Housing", "Education", "Medical", "Retirement",
    "Age 50 Partial", "Age 55 Full", "Critical Illness"
]

LEGAL_CASE_TYPES = [
    "Non-payment of contributions", "Late payment charges",
    "Wage discrepancies", "Employee complaint", "Audit non-compliance"
]

AUDIT_RESULTS = ["Satisfactory", "Minor Issues", "Major Issues", "Critical"]

MALAYSIAN_NAME_PREFIXES = {
    "Malay": ["Ahmad", "Muhammad", "Abdul", "Siti", "Nur", "Mohd", "Norhayati", "Fatimah"],
    "Chinese": ["Tan", "Lee", "Lim", "Wong", "Ng", "Ong", "Chan", "Chong", "Teo"],
    "Indian": ["Kumar", "Raj", "Devi", "Muthu", "Ravi", "Siva", "Lakshmi", "Suresh"]
}

MALAYSIAN_COMPANY_PREFIXES = [
    "Malaysia", "Global", "Asia", "United", "Golden", "Supreme",
    "Elite", "Premier", "Dynamic", "Innovative", "Smart", "Synergy"
]

MALAYSIAN_COMPANY_TYPES = [
    "Technology", "Manufacturing", "Solutions", "Services", "Industries",
    "Trading", "Consulting", "Engineering", "Construction", "Resources"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def weighted_choice(choices: List[str], weights: List[float]) -> str:
    """Select item based on weights."""
    return random.choices(choices, weights=weights, k=1)[0]


def get_weighted_state() -> str:
    """Get random state based on population weights."""
    states = list(STATE_WEIGHTS.keys())
    weights = list(STATE_WEIGHTS.values())
    return random.choices(states, weights=weights, k=1)[0]


def generate_ic_number(dob: datetime) -> str:
    """Generate realistic Malaysian IC number from date of birth."""
    year = str(dob.year)[2:]
    month = f"{dob.month:02d}"
    day = f"{dob.day:02d}"
    state_code = f"{random.randint(1, 16):02d}"
    unique = f"{random.randint(1, 9999):04d}"
    return f"{year}{month}{day}-{state_code}-{unique}"


def generate_member_id() -> str:
    """Generate PensionFund member ID."""
    return f"M{random.randint(10000000, 99999999)}"


def generate_employer_id() -> str:
    """Generate PensionFund employer ID."""
    return f"ER{random.randint(100000, 999999)}"


def calculate_age(dob: datetime) -> int:
    """Calculate age from date of birth."""
    today = datetime.now()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def get_generation_group(age: int) -> str:
    """Determine generation group from age."""
    if age < 28:
        return "Gen Z"
    elif age < 44:
        return "Millennials"
    elif age < 60:
        return "Gen X"
    else:
        return "Baby Boomers"


def generate_malaysian_name() -> Tuple[str, str]:
    """Generate realistic Malaysian name and ethnicity."""
    ethnicity = random.choices(
        ["Malay", "Chinese", "Indian"],
        weights=[0.60, 0.25, 0.15],
        k=1
    )[0]

    if ethnicity == "Malay":
        first_names = ["Ahmad", "Ali", "Hassan", "Ibrahim", "Aziz", "Siti", "Fatimah", "Nur", "Aisyah", "Aishah"]
        last_names = ["Abdullah", "Rahman", "Ali", "Ismail", "Omar", "Ahmad", "Hassan", "Ibrahim"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
    elif ethnicity == "Chinese":
        surnames = ["Tan", "Lee", "Lim", "Wong", "Ng", "Ong", "Chan", "Chong", "Teo", "Liew"]
        first_names = ["Wei", "Ming", "Hui", "Li", "Jia", "Xin", "Ying", "Chen", "Jun", "Kai"]
        second = ["Ling", "Hao", "Rui", "Xuan", "Yi", "Zhi", "Feng", "Long"]
        name = f"{random.choice(surnames)} {random.choice(first_names)} {random.choice(second)}"
    else:  # Indian
        first_names = ["Kumar", "Raj", "Ravi", "Siva", "Muthu", "Devi", "Lakshmi", "Priya", "Suresh", "Arjun"]
        last_names = ["Kumar", "Raj", "Murugan", "Devi", "Krishnan", "Samy", "Maniam", "Selvam"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"

    return name, ethnicity


def generate_malaysian_company_name() -> str:
    """Generate realistic Malaysian company name."""
    company_type_suffix = random.choices(
        ["Sdn Bhd", "Bhd", "(M) Sdn Bhd", "Enterprise"],
        weights=[0.70, 0.15, 0.10, 0.05],
        k=1
    )[0]

    prefix = random.choice(MALAYSIAN_COMPANY_PREFIXES)
    business_type = random.choice(MALAYSIAN_COMPANY_TYPES)

    patterns = [
        f"{prefix} {business_type} {company_type_suffix}",
        f"{prefix} {company_type_suffix}",
        f"{fake.last_name()} {business_type} {company_type_suffix}",
        f"{business_type} {company_type_suffix}"
    ]

    return random.choice(patterns)


def generate_postcode(state: str) -> str:
    """Generate realistic postcode for state."""
    postcode_ranges = {
        "Kuala Lumpur": (50000, 60000),
        "Selangor": (40000, 48999),
        "Johor": (79000, 86000),
        "Penang": (10000, 14400),
        "Perak": (30000, 36800),
        "Sabah": (87000, 91309),
        "Sarawak": (93000, 98859),
        "Kedah": (5000, 9810),
        "Kelantan": (15000, 19800),
        "Pahang": (25000, 28800),
        "Negeri Sembilan": (70000, 73509),
        "Terengganu": (20000, 24300),
        "Malacca": (75000, 78309),
        "Perlis": (1000, 2800),
        "Labuan": (87000, 87033),
        "Putrajaya": (62000, 62988)
    }

    min_code, max_code = postcode_ranges.get(state, (50000, 60000))
    return str(random.randint(min_code, max_code))


def generate_phone_number() -> str:
    """Generate Malaysian phone number."""
    prefixes = ["03", "04", "05", "06", "07", "08", "09"]
    mobile_prefixes = ["010", "011", "012", "013", "014", "016", "017", "018", "019"]

    if random.random() < 0.6:  # 60% mobile
        return f"+60{random.choice(mobile_prefixes)}-{random.randint(1000000, 9999999)}"
    else:  # 40% landline
        return f"+60{random.choice(prefixes)}-{random.randint(1000000, 9999999)}"


def generate_contribution_month(months_ago: int) -> str:
    """Generate contribution month string (YYYY-MM)."""
    date = datetime.now() - timedelta(days=30 * months_ago)
    return date.strftime("%Y-%m")


# ============================================================================
# MEMBER DOCUMENT GENERATION
# ============================================================================

def generate_member_document(employer_id: str, employer_name: str, employer_code: str) -> Dict[str, Any]:
    """
    Generate a realistic member document with all fields.
    """
    member_id = generate_member_id()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65)
    age = calculate_age(dob)
    full_name, ethnicity = generate_malaysian_name()
    gender = random.choice(["Male", "Female"])
    state = get_weighted_state()

    # Employment details
    employment_status = weighted_choice(EMPLOYMENT_STATUSES, EMPLOYMENT_STATUS_WEIGHTS)
    job_category = weighted_choice(JOB_CATEGORIES, JOB_CATEGORY_WEIGHTS)
    start_date = fake.date_between(start_date="-10y", end_date="-1y")

    # Account details
    account_status = weighted_choice(ACCOUNT_STATUSES, ACCOUNT_STATUS_WEIGHTS)

    # Generate realistic balances based on age and employment duration
    years_employed = (datetime.now() - start_date).days / 365
    base_monthly_wage = random.uniform(2000, 15000)

    # Account 1 (retirement) - 70% of contributions
    akaun1_balance = base_monthly_wage * years_employed * 12 * 0.13 * 0.70
    # Account 2 (flexible) - 30% of contributions
    akaun2_balance = base_monthly_wage * years_employed * 12 * 0.13 * 0.30

    # Add some randomness
    akaun1_balance *= random.uniform(0.8, 1.2)
    akaun2_balance *= random.uniform(0.8, 1.2)

    total_balance = akaun1_balance + akaun2_balance

    # Generate recent contributions (last 12 months)
    num_contributions = random.randint(8, 12) if employment_status == "Active" else random.randint(0, 6)
    recent_contributions = []
    contribution_total = 0
    late_count = 0

    for i in range(num_contributions):
        month = generate_contribution_month(i)
        wage = base_monthly_wage * random.uniform(0.9, 1.1)
        employer_contrib = wage * 0.13  # 13% employer
        employee_contrib = wage * 0.11  # 11% employee
        total_contrib = employer_contrib + employee_contrib
        contribution_total += total_contrib

        is_late = random.random() < 0.15  # 15% late payments
        if is_late:
            late_count += 1

        recent_contributions.append({
            "contributionMonth": month,
            "submissionDate": datetime.now() - timedelta(days=30 * i + random.randint(1, 15)),
            "employerId": employer_id,
            "employerName": employer_name,
            "wageReported": round(wage, 2),
            "employerContribution": round(employer_contrib, 2),
            "employeeContribution": round(employee_contrib, 2),
            "totalContribution": round(total_contrib, 2),
            "submissionStatus": weighted_choice(["Approved", "Pending"], [0.95, 0.05]),
            "receivingBranch": random.choice(RECEIVING_BRANCHES),
            "isLatePayment": is_late,
            "arrearsDays": random.randint(15, 90) if is_late else 0
        })

    # Contribution stats
    has_gaps = num_contributions < 12
    gap_months = []
    if has_gaps:
        all_months = [generate_contribution_month(i) for i in range(12)]
        contrib_months = [c["contributionMonth"] for c in recent_contributions]
        gap_months = [m for m in all_months if m not in contrib_months]

    # Employer history
    num_previous_employers = random.randint(0, 3)
    employer_history = []

    for i in range(num_previous_employers):
        prev_start = fake.date_between(start_date="-15y", end_date=start_date)
        prev_end = fake.date_between(start_date=prev_start, end_date=start_date)
        months_worked = max(1, int((prev_end - prev_start).days / 30))

        employer_history.append({
            "employerId": generate_employer_id(),
            "employerName": generate_malaysian_company_name(),
            "startDate": prev_start,
            "endDate": prev_end,
            "isActive": False,
            "totalContributions": round(random.uniform(5000, 50000), 2),
            "monthsWorked": months_worked
        })

    # Add current employer
    employer_history.append({
        "employerId": employer_id,
        "employerName": employer_name,
        "startDate": start_date,
        "endDate": None,
        "isActive": employment_status == "Active",
        "totalContributions": round(contribution_total, 2),
        "monthsWorked": int(years_employed * 12)
    })

    # Withdrawal history (random, more for older members)
    withdrawal_history = []
    if age > 40 and random.random() < 0.3:  # 30% of members over 40 have withdrawals
        num_withdrawals = random.randint(1, 3)
        for _ in range(num_withdrawals):
            withdrawal_history.append({
                "withdrawalId": f"W{random.randint(1000000, 9999999)}",
                "withdrawalType": random.choice(WITHDRAWAL_TYPES),
                "withdrawalDate": fake.date_between(start_date="-5y", end_date="today"),
                "amount": round(random.uniform(5000, 50000), 2),
                "purpose": random.choice(["Housing purchase", "Education", "Medical", "Retirement"]),
                "approvalStatus": weighted_choice(["Approved", "Pending", "Rejected"], [0.85, 0.10, 0.05])
            })

    # Eligibility flags
    eligibility_flags = {
        "housingWithdrawal": total_balance > 30000 and age >= 25,
        "educationWithdrawal": total_balance > 10000,
        "medicalWithdrawal": age >= 40,
        "retirementAge": age >= 55,
        "minimumBalanceReached": total_balance > 1000
    }

    # Compliance flags
    risk_score = weighted_choice(RISK_SCORES, RISK_SCORE_WEIGHTS)
    has_irregularities = risk_score in ["High", "Critical"]

    compliance_flags = {
        "hasIrregularities": has_irregularities,
        "hasMissingContributions": has_gaps,
        "hasWageDiscrepancies": random.random() < 0.05,
        "hasActiveComplaints": random.random() < 0.03,
        "lastAuditDate": fake.date_between(start_date="-2y", end_date="today"),
        "riskScore": risk_score
    }

    member = {
        "memberId": member_id,
        "icNumber": generate_ic_number(dob),
        "personalInfo": {
            "fullName": full_name,
            "dateOfBirth": dob,
            "age": age,
            "gender": gender,
            "nationality": "Malaysian",
            "region": state,
            "generationGroup": get_generation_group(age)
        },
        "employmentProfile": {
            "jobCategory": job_category,
            "currentEmployer": {
                "employerId": employer_id,
                "employerName": employer_name,
                "employerCode": employer_code,
                "startDate": start_date,
                "isActive": employment_status == "Active"
            },
            "employmentStatus": employment_status,
            "hasMultipleEmployers": random.random() < 0.10  # 10% have multiple employers
        },
        "accountInfo": {
            "accountStatus": account_status,
            "akaun1Balance": round(akaun1_balance, 2),
            "akaun2Balance": round(akaun2_balance, 2),
            "totalBalance": round(total_balance, 2),
            "lastUpdated": datetime.now(),
            "currency": "MYR"
        },
        "recentContributions": recent_contributions[:12],  # Last 12 months
        "contributionStats": {
            "totalMonths": int(years_employed * 12),
            "consecutiveMonths": num_contributions,
            "lastDate": recent_contributions[0]["submissionDate"] if recent_contributions else None,
            "avgMonthlyWage": round(base_monthly_wage, 2),
            "avgMonthly": round(base_monthly_wage * 0.24, 2),  # 24% total contribution
            "totalLifetime": round(total_balance * 1.2, 2),  # Approximation
            "hasGaps": has_gaps,
            "gapMonths": gap_months
        },
        "employerHistory": employer_history,
        "withdrawalHistory": withdrawal_history,
        "eligibilityFlags": eligibility_flags,
        "complianceFlags": compliance_flags,
        "metadata": {
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "dataSource": "Sample Data Generator",
            "version": 1
        }
    }

    return member


# ============================================================================
# EMPLOYER DOCUMENT GENERATION
# ============================================================================

def generate_employer_document() -> Dict[str, Any]:
    """
    Generate a realistic employer document with all fields.
    """
    employer_id = generate_employer_id()
    company_name = generate_malaysian_company_name()
    employer_code = f"COMP{random.randint(1000, 9999)}"

    # Location
    state = get_weighted_state()
    city = random.choice(MALAYSIAN_CITIES[state])
    postcode = generate_postcode(state)

    # Company size and employees
    company_size = weighted_choice(COMPANY_SIZES, COMPANY_SIZE_WEIGHTS)
    min_emp, max_emp = COMPANY_SIZE_EMPLOYEES[company_size]
    num_employees = random.randint(min_emp, max_emp)

    # Industry
    industry = random.choice(INDUSTRY_SECTORS)

    # Account details
    account_status = weighted_choice(ACCOUNT_STATUSES, ACCOUNT_STATUS_WEIGHTS)
    account_type = weighted_choice(EMPLOYER_ACCOUNT_TYPES, EMPLOYER_ACCOUNT_TYPE_WEIGHTS)
    registration_date = fake.date_between(start_date="-20y", end_date="-1y")
    last_active_date = fake.date_between(start_date=registration_date, end_date="today")

    # Member summary
    active_members = int(num_employees * random.uniform(0.85, 1.0))
    inactive_members = num_employees - active_members

    members_by_gender = {
        "Male": int(num_employees * random.uniform(0.45, 0.65)),
        "Female": 0
    }
    members_by_gender["Female"] = num_employees - members_by_gender["Male"]

    members_by_age_group = {
        "18-25": int(num_employees * 0.15),
        "26-35": int(num_employees * 0.35),
        "36-45": int(num_employees * 0.30),
        "46-55": int(num_employees * 0.15),
        "55+": int(num_employees * 0.05)
    }

    members_by_job_category = {}
    for category in JOB_CATEGORIES[:5]:  # Top 5 categories
        members_by_job_category[category] = random.randint(1, num_employees // 2)

    # Product tags
    num_tags = random.randint(1, 4)
    product_tags = random.sample(PRODUCT_TAGS, num_tags)

    # Generate recent submissions (last 12 months)
    num_submissions = random.randint(10, 12)
    recent_submissions = []
    total_lifetime_contrib = 0
    on_time_count = 0
    late_payment_charges_total = 0

    for i in range(num_submissions):
        month = generate_contribution_month(i)
        submission_date = datetime.now() - timedelta(days=30 * i + random.randint(1, 15))
        due_date = datetime.now() - timedelta(days=30 * i + 15)
        is_late = submission_date > due_date
        late_days = (submission_date - due_date).days if is_late else 0
        late_charges = late_days * num_employees * 0.5 if is_late else 0

        if not is_late:
            on_time_count += 1

        total_wages = num_employees * random.uniform(2500, 8000)
        employer_contrib = total_wages * 0.13
        employee_contrib = total_wages * 0.11
        total_contrib = employer_contrib + employee_contrib
        total_lifetime_contrib += total_contrib
        late_payment_charges_total += late_charges

        recent_submissions.append({
            "submissionId": f"SUB{random.randint(1000000, 9999999)}",
            "contributionMonth": month,
            "submissionDate": submission_date,
            "submissionMethod": weighted_choice(SUBMISSION_METHODS, [0.70, 0.15, 0.10, 0.05]),
            "receivingBranch": random.choice(RECEIVING_BRANCHES),
            "totalMembers": num_employees,
            "totalWages": round(total_wages, 2),
            "totalEmployerContribution": round(employer_contrib, 2),
            "totalEmployeeContribution": round(employee_contrib, 2),
            "totalContribution": round(total_contrib, 2),
            "submissionStatus": weighted_choice(SUBMISSION_STATUS, [0.90, 0.05, 0.03, 0.02]),
            "validationErrors": [] if random.random() > 0.10 else ["Wage discrepancy detected"],
            "paymentStatus": weighted_choice(PAYMENT_STATUS, [0.85, 0.08, 0.05, 0.02]),
            "paymentDate": submission_date + timedelta(days=random.randint(1, 5)) if random.random() > 0.15 else None,
            "paymentReference": f"PAY{random.randint(100000, 999999)}" if random.random() > 0.15 else None,
            "dueDate": due_date,
            "isLateSubmission": is_late,
            "lateDays": late_days,
            "latePaymentCharges": round(late_charges, 2),
            "processedBy": f"Officer{random.randint(1, 50)}",
            "processedDate": submission_date + timedelta(days=1),
            "remarks": "Late submission penalty applied" if is_late else ""
        })

    # Contribution statistics
    on_time_rate = on_time_count / num_submissions if num_submissions > 0 else 1.0
    avg_monthly = total_lifetime_contrib / num_submissions if num_submissions > 0 else 0

    # Determine trend
    if num_submissions >= 3:
        recent_avg = sum(s["totalContribution"] for s in recent_submissions[:3]) / 3
        older_avg = sum(s["totalContribution"] for s in recent_submissions[-3:]) / 3
        if recent_avg > older_avg * 1.1:
            trend = "Increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "Decreasing"
        else:
            trend = "Stable"
    else:
        trend = "Stable"

    contribution_stats = {
        "totalLifetime": round(total_lifetime_contrib * random.uniform(8, 15), 2),  # Approximate lifetime
        "avgMonthly": round(avg_monthly, 2),
        "last12MonthsTotal": round(total_lifetime_contrib, 2),
        "trend": trend,
        "onTimeRate": round(on_time_rate, 2),
        "totalLatePayments": num_submissions - on_time_count,
        "totalLateCharges": round(late_payment_charges_total, 2)
    }

    # Compliance status
    has_arrears = random.random() < 0.15  # 15% have arrears
    arrears_amount = random.uniform(10000, 100000) if has_arrears else 0
    arrears_months = []
    if has_arrears:
        num_arrears = random.randint(1, 4)
        arrears_months = [generate_contribution_month(i) for i in range(num_arrears)]

    has_legal_cases = random.random() < 0.05  # 5% have legal cases
    legal_case_types = []
    active_cases = []
    if has_legal_cases:
        num_cases = random.randint(1, 2)
        legal_case_types = random.sample(LEGAL_CASE_TYPES, num_cases)
        active_cases = [f"CASE{random.randint(1000, 9999)}" for _ in range(num_cases)]

    last_audit_date = fake.date_between(start_date="-2y", end_date="today")
    next_audit_date = last_audit_date + timedelta(days=365)
    audit_result = weighted_choice(AUDIT_RESULTS, [0.70, 0.20, 0.08, 0.02])

    # Risk rating based on compliance
    if has_legal_cases or audit_result == "Critical":
        risk_rating = "Critical"
    elif has_arrears or audit_result == "Major Issues":
        risk_rating = "High"
    elif audit_result == "Minor Issues" or on_time_rate < 0.80:
        risk_rating = "Medium"
    else:
        risk_rating = "Low"

    compliance_status = {
        "hasArrears": has_arrears,
        "arrearsAmount": round(arrears_amount, 2),
        "arrearsMonths": arrears_months,
        "hasLegalCases": has_legal_cases,
        "legalCaseTypes": legal_case_types,
        "activeCases": active_cases,
        "lastAuditDate": last_audit_date,
        "auditResult": audit_result,
        "nextAuditDate": next_audit_date,
        "riskRating": risk_rating
    }

    # Legal cases (if any)
    legal_cases = []
    if has_legal_cases:
        for i, case_type in enumerate(legal_case_types):
            legal_cases.append({
                "caseId": active_cases[i],
                "caseType": case_type,
                "filedDate": fake.date_between(start_date="-2y", end_date="today"),
                "status": weighted_choice(["Open", "Under Review", "Closed"], [0.50, 0.30, 0.20]),
                "amountInDispute": round(random.uniform(5000, 50000), 2),
                "description": f"{case_type} - pending resolution"
            })

    # Member list will be populated later when generating members
    member_list = []

    employer = {
        "employerId": employer_id,
        "employerCode": employer_code,
        "companyProfile": {
            "companyName": company_name,
            "registrationNumber": f"{random.randint(1990, 2024)}{random.randint(10000000, 99999999)}",
            "businessAddress": {
                "street": fake.street_address(),
                "city": city,
                "state": state,
                "postcode": postcode,
                "country": "Malaysia"
            },
            "contactInfo": {
                "phone": generate_phone_number(),
                "email": f"info@{company_name.lower().replace(' ', '').replace('sdnbhd', '').replace('bhd', '')[:15]}.com.my",
                "website": f"www.{company_name.lower().replace(' ', '').replace('sdnbhd', '').replace('bhd', '')[:15]}.com.my" if random.random() > 0.30 else None
            },
            "industryClassification": {
                "msicCode": industry["msic"],
                "msicDescription": industry["description"],
                "sector": industry["sector"]
            },
            "companySize": company_size,
            "numberOfEmployees": num_employees
        },
        "accountStatus": {
            "status": account_status,
            "registrationDate": registration_date,
            "lastActiveDate": last_active_date,
            "suspensionReason": "Late payment arrears" if account_status == "Suspended" else None,
            "accountType": account_type
        },
        "memberSummary": {
            "totalMembers": num_employees,
            "activeMembers": active_members,
            "inactiveMembers": inactive_members,
            "membersByGender": members_by_gender,
            "membersByAgeGroup": members_by_age_group,
            "membersByJobCategory": members_by_job_category,
            "lastUpdated": datetime.now()
        },
        "productTags": product_tags,
        "recentSubmissions": recent_submissions[:12],  # Last 12 months
        "contributionStats": contribution_stats,
        "complianceStatus": compliance_status,
        "legalCases": legal_cases,
        "memberList": member_list,  # Will be populated when generating members
        "metadata": {
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "dataSource": "Sample Data Generator",
            "version": 1
        }
    }

    return employer


# ============================================================================
# BATCH INSERTION
# ============================================================================

async def batch_insert(collection, documents: List[Dict], batch_size: int = 1000, entity_type: str = "documents"):
    """Insert documents in batches with progress tracking."""
    total = len(documents)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        await collection.insert_many(batch, ordered=False)
        inserted += len(batch)

        # Progress indicator
        percentage = (inserted / total) * 100
        print(f"   Progress: {inserted:,}/{total:,} {entity_type} ({percentage:.1f}%) inserted", end='\r')

    print()  # New line after progress
    return inserted


# ============================================================================
# MAIN DATA GENERATION FUNCTION
# ============================================================================

async def generate_sample_data(num_members: int, num_employers: int):
    """
    Generate sample data and insert into MongoDB with batch processing.

    Args:
        num_members: Number of member documents to generate
        num_employers: Number of employer documents to generate
    """
    print(f"🚀 Starting sample data generation...")
    print(f"   Members: {num_members:,}")
    print(f"   Employers: {num_employers:,}")
    print()

    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    try:
        # ========================================
        # PHASE 1: Generate and Insert Employers
        # ========================================
        print(f"📊 Phase 1: Generating {num_employers:,} employers...")
        employers = []

        for i in range(num_employers):
            employer = generate_employer_document()
            employers.append(employer)

            if (i + 1) % 10000 == 0:
                print(f"   Generated {i + 1:,}/{num_employers:,} employers")

        print(f"   ✅ Generated {len(employers):,} employers")

        if employers:
            print(f"\n   Inserting employers into database (batch size: 1000)...")
            await batch_insert(db.employers, employers, batch_size=1000, entity_type="employers")
            print(f"   ✅ Inserted {len(employers):,} employers")

        # ========================================
        # PHASE 2: Generate and Insert Members
        # ========================================
        print(f"\n👥 Phase 2: Generating {num_members:,} members...")
        members = []
        member_references = {}  # Track member refs for each employer

        for employer in employers:
            member_references[employer["employerId"]] = []

        for i in range(num_members):
            # Randomly assign to an employer (weighted by company size)
            employer = random.choice(employers)

            member = generate_member_document(
                employer["employerId"],
                employer["companyProfile"]["companyName"],
                employer["employerCode"]
            )
            members.append(member)

            # Create member reference for employer
            member_ref = {
                "memberId": member["memberId"],
                "fullName": member["personalInfo"]["fullName"],
                "icNumber": member["icNumber"],
                "employmentStatus": member["employmentProfile"]["employmentStatus"],
                "startDate": member["employmentProfile"]["currentEmployer"]["startDate"],
                "lastContributionMonth": member["recentContributions"][0]["contributionMonth"] if member["recentContributions"] else "N/A",
                "averageWage": member["contributionStats"]["avgMonthlyWage"]
            }
            member_references[employer["employerId"]].append(member_ref)

            if (i + 1) % 10000 == 0:
                print(f"   Generated {i + 1:,}/{num_members:,} members")

        print(f"   ✅ Generated {len(members):,} members")

        if members:
            print(f"\n   Inserting members into database (batch size: 1000)...")
            await batch_insert(db.members, members, batch_size=1000, entity_type="members")
            print(f"   ✅ Inserted {len(members):,} members")

        # ========================================
        # PHASE 3: Update Employer Member Lists
        # ========================================
        print(f"\n🔗 Phase 3: Updating employer member lists...")
        update_count = 0

        for employer_id, member_refs in member_references.items():
            if member_refs:
                await db.employers.update_one(
                    {"employerId": employer_id},
                    {"$set": {"memberList": member_refs[:100]}}  # Store max 100 refs
                )
                update_count += 1

                if update_count % 1000 == 0:
                    print(f"   Updated {update_count:,}/{len(member_references):,} employers", end='\r')

        print(f"\n   ✅ Updated {update_count:,} employer member lists")

        # ========================================
        # SUMMARY
        # ========================================
        print(f"\n✅ Sample data generation complete!")
        print(f"\n📈 Summary:")
        print(f"   Total employers: {await db.employers.count_documents({}):,}")
        print(f"   Total members: {await db.members.count_documents({}):,}")
        print(f"\n💡 Next steps:")
        print(f"   1. Create Atlas Search indexes (see backend/atlas_search_indexes/)")
        print(f"   2. Set up Atlas Triggers for materialized views (see backend/ATLAS_TRIGGERS_SETUP.md)")
        print(f"   3. Start the FastAPI backend: cd backend && uvicorn app.main:app --reload")

    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        client.close()


async def clear_sample_data():
    """Clear all sample data from the database."""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    try:
        print("🗑️  Clearing sample data...")

        members_count = await db.members.count_documents({})
        employers_count = await db.employers.count_documents({})

        if members_count > 0 or employers_count > 0:
            print(f"\n⚠️  WARNING: This will delete:")
            print(f"   - {members_count:,} members")
            print(f"   - {employers_count:,} employers")

            confirm = input("\nType 'DELETE' to confirm: ")

            if confirm == "DELETE":
                print("\n   Deleting members...")
                await db.members.delete_many({})
                print(f"   ✅ Deleted {members_count:,} members")

                print("   Deleting employers...")
                await db.employers.delete_many({})
                print(f"   ✅ Deleted {employers_count:,} employers")

                print("\n✅ Sample data cleared")
            else:
                print("❌ Operation cancelled")
        else:
            print("ℹ️  No data to clear")

    finally:
        client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate realistic Malaysian PensionFund sample data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 1,000 members and 100 employers (development)
  python generate_sample_data.py --members 1000 --employers 100

  # Generate full production-scale data (1M members, 650K employers)
  python generate_sample_data.py --members 1000000 --employers 650000

  # Clear all existing data
  python generate_sample_data.py --clear
        """
    )
    parser.add_argument(
        "--members",
        type=int,
        default=1000,
        help="Number of member records to generate (default: 1000, max: 1000000)"
    )
    parser.add_argument(
        "--employers",
        type=int,
        default=100,
        help="Number of employer records to generate (default: 100, max: 650000)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing sample data"
    )

    args = parser.parse_args()

    # Validate inputs
    if args.members > 1000000:
        print("⚠️  Warning: Member count exceeds 1M. Capping at 1,000,000.")
        args.members = 1000000

    if args.employers > 650000:
        print("⚠️  Warning: Employer count exceeds 650K. Capping at 650,000.")
        args.employers = 650000

    if args.clear:
        asyncio.run(clear_sample_data())
    else:
        asyncio.run(generate_sample_data(args.members, args.employers))


if __name__ == "__main__":
    main()
