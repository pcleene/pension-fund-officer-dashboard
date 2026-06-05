<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getEmployerById, type Employer } from '$lib/api';

	let employer: Employer | null = null;
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			const employerId = $page.params.id;
			employer = await getEmployerById(employerId);
		} catch (err: any) {
			error = err.message || 'Failed to load employer details';
			console.error('Employer detail error:', err);
		} finally {
			loading = false;
		}
	});

	function formatCurrency(value: number): string {
		return `RM ${value.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	function formatDate(date: string): string {
		return new Date(date).toLocaleDateString('en-MY');
	}

	function getRiskBadgeClass(risk: string): string {
		switch (risk) {
			case 'Low':
				return 'badge-success';
			case 'Medium':
				return 'badge-info';
			case 'High':
				return 'badge-warning';
			case 'Critical':
				return 'badge-danger';
			default:
				return 'badge-info';
		}
	}
</script>

<svelte:head>
	<title>Employer Details - PensionFund Officer Dashboard</title>
</svelte:head>

{#if loading}
	<div class="flex justify-center items-center h-64">
		<div class="text-center">
			<svg class="animate-spin h-12 w-12 text-PensionFund-blue mx-auto" fill="none" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				/>
			</svg>
			<p class="mt-4 text-gray-600">Loading employer details...</p>
		</div>
	</div>
{:else if error}
	<div class="bg-red-50 border border-red-200 rounded-lg p-4">
		<p class="text-red-800">{error}</p>
	</div>
{:else if employer}
	<div class="space-y-6">
		<!-- Header with back button -->
		<div class="flex items-center space-x-4">
			<a
				href="/employers"
				class="text-PensionFund-blue hover:text-PensionFund-navy flex items-center space-x-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M10 19l-7-7m0 0l7-7m-7 7h18"
					/>
				</svg>
				<span>Back to Search</span>
			</a>
		</div>

		<!-- Company Info Card -->
		<div class="card">
			<div class="flex items-center justify-between mb-6">
				<h2 class="text-2xl font-bold text-gray-900">{employer.companyProfile.companyName}</h2>
				<span class="badge {employer.accountStatus.status === 'Active' ? 'badge-success' : 'badge-warning'}">
					{employer.accountStatus.status}
				</span>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<div>
					<p class="text-sm text-gray-600">Employer ID</p>
					<p class="font-medium">{employer.employerId}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Employer Code</p>
					<p class="font-medium">{employer.employerCode}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Registration Number</p>
					<p class="font-medium">{employer.companyProfile.registrationNumber}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Industry Sector</p>
					<p class="font-medium">{employer.companyProfile.industryClassification.sector}</p>
					<p class="text-xs text-gray-500">MSIC: {employer.companyProfile.industryClassification.msicCode}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Company Size</p>
					<p class="font-medium">{employer.companyProfile.companySize}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Number of Employees</p>
					<p class="font-medium">{employer.companyProfile.numberOfEmployees.toLocaleString()}</p>
				</div>
			</div>

			<!-- Address -->
			<div class="mt-6 pt-6 border-t border-gray-200">
				<p class="text-sm text-gray-600 mb-2">Business Address</p>
				<p class="font-medium">
					{employer.companyProfile.businessAddress.street}<br />
					{employer.companyProfile.businessAddress.city}, {employer.companyProfile.businessAddress
						.state}
					{employer.companyProfile.businessAddress.postcode}<br />
					{employer.companyProfile.businessAddress.country}
				</p>
			</div>

			<!-- Contact Info -->
			<div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
				<div>
					<p class="text-sm text-gray-600">Phone</p>
					<p class="font-medium">{employer.companyProfile.contactInfo.phone}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Email</p>
					<p class="font-medium">{employer.companyProfile.contactInfo.email}</p>
				</div>
				{#if employer.companyProfile.contactInfo.website}
					<div>
						<p class="text-sm text-gray-600">Website</p>
						<p class="font-medium">{employer.companyProfile.contactInfo.website}</p>
					</div>
				{/if}
			</div>
		</div>

		<!-- Member Summary Card -->
		<div class="card bg-gradient-to-br from-blue-50 to-white">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Workforce Summary</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				<div>
					<p class="text-sm text-gray-600">Total Members</p>
					<p class="text-2xl font-bold text-PensionFund-blue">
						{employer.memberSummary.totalMembers.toLocaleString()}
					</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Active Members</p>
					<p class="text-2xl font-bold text-green-700">
						{employer.memberSummary.activeMembers.toLocaleString()}
					</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Inactive Members</p>
					<p class="text-2xl font-bold text-gray-600">
						{employer.memberSummary.inactiveMembers.toLocaleString()}
					</p>
				</div>
			</div>
		</div>

		<!-- Contribution Stats Card -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Contribution Statistics</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<div>
					<p class="text-sm text-gray-600">Total Lifetime</p>
					<p class="font-medium">{formatCurrency(employer.contributionStats.totalLifetime)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Average Monthly</p>
					<p class="font-medium">{formatCurrency(employer.contributionStats.avgMonthly)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Last 12 Months</p>
					<p class="font-medium">{formatCurrency(employer.contributionStats.last12MonthsTotal)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Trend</p>
					<span
						class="badge {employer.contributionStats.trend === 'Increasing'
							? 'badge-success'
							: employer.contributionStats.trend === 'Stable'
								? 'badge-info'
								: 'badge-warning'}"
					>
						{employer.contributionStats.trend}
					</span>
				</div>
			</div>

			<div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
				<div>
					<p class="text-sm text-gray-600">On-Time Rate</p>
					<p class="font-medium">
						{(employer.contributionStats.onTimeRate * 100).toFixed(1)}%
					</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Total Late Payments</p>
					<p class="font-medium">{employer.contributionStats.totalLatePayments}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Total Late Charges</p>
					<p class="font-medium">{formatCurrency(employer.contributionStats.totalLateCharges)}</p>
				</div>
			</div>
		</div>

		<!-- Compliance Status Card -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<div>
					<p class="text-sm text-gray-600">Risk Rating</p>
					<span class="badge {getRiskBadgeClass(employer.complianceStatus.riskRating)}">
						{employer.complianceStatus.riskRating}
					</span>
				</div>
				<div>
					<p class="text-sm text-gray-600">Last Audit</p>
					<p class="font-medium">{formatDate(employer.complianceStatus.lastAuditDate)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Audit Result</p>
					<span
						class="badge {employer.complianceStatus.auditResult === 'Satisfactory'
							? 'badge-success'
							: 'badge-warning'}"
					>
						{employer.complianceStatus.auditResult}
					</span>
				</div>
				<div>
					<p class="text-sm text-gray-600">Next Audit</p>
					<p class="font-medium">{formatDate(employer.complianceStatus.nextAuditDate)}</p>
				</div>
			</div>

			{#if employer.complianceStatus.hasArrears}
				<div class="mt-4 p-4 bg-red-50 border border-red-200 rounded">
					<p class="text-sm font-semibold text-red-800">⚠️ Arrears Detected</p>
					<p class="text-sm text-red-700 mt-1">
						Amount: {formatCurrency(employer.complianceStatus.arrearsAmount)}
					</p>
					<p class="text-sm text-red-700">
						Months: {employer.complianceStatus.arrearsMonths.join(', ')}
					</p>
				</div>
			{/if}

			{#if employer.complianceStatus.hasLegalCases}
				<div class="mt-4 p-4 bg-orange-50 border border-orange-200 rounded">
					<p class="text-sm font-semibold text-orange-800">⚠️ Active Legal Cases</p>
					<p class="text-sm text-orange-700 mt-1">
						Cases: {employer.complianceStatus.activeCases.join(', ')}
					</p>
					<p class="text-sm text-orange-700">
						Types: {employer.complianceStatus.legalCaseTypes.join(', ')}
					</p>
				</div>
			{/if}
		</div>

		<!-- Product Tags -->
		{#if employer.productTags.length > 0}
			<div class="card">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Product Tags</h3>
				<div class="flex flex-wrap gap-2">
					{#each employer.productTags as tag}
						<span class="badge badge-info">{tag}</span>
					{/each}
				</div>
			</div>
		{/if}
	</div>
{/if}
