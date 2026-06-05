/**
 * API client for PensionFund Officer Dashboard Backend
 */
import axios, { type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		'Content-Type': 'application/json'
	},
	timeout: 30000 // 30 seconds
});

// Types
export interface SearchFilters {
	account_status?: string[];
	region?: string[];
	generation?: string[];
	job_category?: string[];
	risk_score?: string[];
	employment_status?: string[];
	min_balance?: number;
	max_balance?: number;
	sector?: string[];
	company_size?: string[];
	state?: string[];
	account_type?: string[];
	risk_rating?: string[];
	has_arrears?: boolean;
	has_legal_cases?: boolean;
	product_tags?: string[];
}

export interface PaginationParams {
	limit?: number;
	cursor?: string;
}

export interface SearchResponse<T> {
	results: T[];
	totalCount?: number;
	pagination: {
		limit: number;
		cursor: string | null;
		hasMore: boolean;
	};
	facets?: Array<{
		field: string;
		label: string;
		buckets: Array<{
			value: string;
			count: number;
		}>;
	}>;
}

export interface Member {
	memberId: string;
	icNumber: string;
	personalInfo: {
		fullName: string;
		dateOfBirth: string;
		age: number;
		gender: string;
		nationality: string;
		region: string;
		generationGroup: string;
	};
	employmentProfile: {
		jobCategory: string;
		currentEmployer: {
			employerId: string;
			employerName: string;
			employerCode: string;
			startDate: string;
			isActive: boolean;
		};
		employmentStatus: string;
		hasMultipleEmployers: boolean;
	};
	accountInfo: {
		accountStatus: string;
		akaun1Balance: number;
		akaun2Balance: number;
		totalBalance: number;
		lastUpdated: string;
		currency: string;
	};
	recentContributions: any[];
	contributionStats: {
		totalMonths: number;
		consecutiveMonths: number;
		lastDate: string;
		avgMonthlyWage: number;
		avgMonthly: number;
		totalLifetime: number;
		hasGaps: boolean;
		gapMonths: string[];
	};
	complianceFlags: {
		hasIrregularities: boolean;
		hasMissingContributions: boolean;
		hasWageDiscrepancies: boolean;
		hasActiveComplaints: boolean;
		lastAuditDate: string;
		riskScore: string;
	};
}

export interface Employer {
	employerId: string;
	employerCode: string;
	companyProfile: {
		companyName: string;
		registrationNumber: string;
		businessAddress: {
			street: string;
			city: string;
			state: string;
			postcode: string;
			country: string;
		};
		contactInfo: {
			phone: string;
			email: string;
			website?: string;
		};
		industryClassification: {
			msicCode: string;
			msicDescription: string;
			sector: string;
		};
		companySize: string;
		numberOfEmployees: number;
	};
	accountStatus: {
		status: string;
		registrationDate: string;
		lastActiveDate: string;
		suspensionReason?: string;
		accountType: string;
	};
	memberSummary: {
		totalMembers: number;
		activeMembers: number;
		inactiveMembers: number;
		membersByGender: Record<string, number>;
		membersByAgeGroup: Record<string, number>;
		membersByJobCategory: Record<string, number>;
		lastUpdated: string;
	};
	productTags: string[];
	contributionStats: {
		totalLifetime: number;
		avgMonthly: number;
		last12MonthsTotal: number;
		trend: string;
		onTimeRate: number;
		totalLatePayments: number;
		totalLateCharges: number;
	};
	complianceStatus: {
		hasArrears: boolean;
		arrearsAmount: number;
		arrearsMonths: string[];
		hasLegalCases: boolean;
		legalCaseTypes: string[];
		activeCases: string[];
		lastAuditDate: string;
		auditResult: string;
		nextAuditDate: string;
		riskRating: string;
	};
}

export interface DashboardStats {
	demographics?: any;
	balances?: any;
	compliance?: any;
	contributionTrends?: any[];
	profiles?: any;
	workforce?: any;
	submissionTrends?: any[];
	refreshedAt?: string;
}

// ============================================================================
// MEMBER API ENDPOINTS
// ============================================================================

/**
 * Search members with text and filters
 */
export async function searchMembers(
	searchText?: string,
	filters?: SearchFilters,
	pagination?: PaginationParams
): Promise<SearchResponse<Member>> {
	const response = await apiClient.post('/members/search', {
		search_text: searchText,
		filters,
		limit: pagination?.limit || 20,
		cursor: pagination?.cursor
	});
	return response.data;
}

/**
 * Vector search members (semantic search)
 */
export async function vectorSearchMembers(
	searchText: string,
	filters?: SearchFilters,
	pagination?: PaginationParams
): Promise<SearchResponse<Member>> {
	const response = await apiClient.post('/members/vector-search', {
		search_text: searchText,
		filters,
		limit: pagination?.limit || 20,
		cursor: pagination?.cursor
	});
	return response.data;
}

/**
 * Get member by ID
 */
export async function getMemberById(memberId: string): Promise<Member> {
	const response = await apiClient.get(`/members/${memberId}`);
	return response.data.member;
}

/**
 * Get member contributions
 */
export async function getMemberContributions(
	memberId: string,
	limit?: number,
	offset?: number
): Promise<any> {
	const response = await apiClient.get(`/members/${memberId}/contributions`, {
		params: { limit, offset }
	});
	return response.data;
}

// ============================================================================
// EMPLOYER API ENDPOINTS
// ============================================================================

/**
 * Search employers with text and filters
 */
export async function searchEmployers(
	searchText?: string,
	filters?: SearchFilters,
	pagination?: PaginationParams
): Promise<SearchResponse<Employer>> {
	const response = await apiClient.post('/employers/search', {
		search_text: searchText,
		filters,
		limit: pagination?.limit || 20,
		cursor: pagination?.cursor
	});
	return response.data;
}

/**
 * Vector search employers (semantic search)
 */
export async function vectorSearchEmployers(
	searchText: string,
	filters?: SearchFilters,
	pagination?: PaginationParams
): Promise<SearchResponse<Employer>> {
	const response = await apiClient.post('/employers/vector-search', {
		search_text: searchText,
		filters,
		limit: pagination?.limit || 20,
		cursor: pagination?.cursor
	});
	return response.data;
}

/**
 * Get employer by ID
 */
export async function getEmployerById(employerId: string): Promise<Employer> {
	const response = await apiClient.get(`/employers/${employerId}`);
	return response.data.employer;
}

/**
 * Get employer members
 */
export async function getEmployerMembers(
	employerId: string,
	limit?: number,
	offset?: number
): Promise<any> {
	const response = await apiClient.get(`/employers/${employerId}/members`, {
		params: { limit, offset }
	});
	return response.data;
}

// ============================================================================
// DASHBOARD API ENDPOINTS
// ============================================================================

/**
 * Get member dashboard statistics
 */
export async function getMemberDashboardStats(): Promise<DashboardStats> {
	const response = await apiClient.get('/dashboard/members');
	return response.data;
}

/**
 * Get employer dashboard statistics
 */
export async function getEmployerDashboardStats(): Promise<DashboardStats> {
	const response = await apiClient.get('/dashboard/employers');
	return response.data;
}

/**
 * Refresh materialized views
 */
export async function refreshViews(views: string[]): Promise<any> {
	const response = await apiClient.post('/dashboard/refresh', {
		views,
		force: false
	});
	return response.data;
}

export default apiClient;
