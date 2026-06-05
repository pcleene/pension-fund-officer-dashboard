<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getMemberById, type Member } from '$lib/api';

	let member: Member | null = null;
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			const memberId = $page.params.id;
			member = await getMemberById(memberId);
		} catch (err: any) {
			error = err.message || 'Failed to load member details';
			console.error('Member detail error:', err);
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
	<title>Member Details - PensionFund Officer Dashboard</title>
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
			<p class="mt-4 text-gray-600">Loading member details...</p>
		</div>
	</div>
{:else if error}
	<div class="bg-red-50 border border-red-200 rounded-lg p-4">
		<p class="text-red-800">{error}</p>
	</div>
{:else if member}
	<div class="space-y-6">
		<!-- Header with back button -->
		<div class="flex items-center space-x-4">
			<a
				href="/members"
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

		<!-- Personal Info Card -->
		<div class="card">
			<div class="flex items-center justify-between mb-6">
				<h2 class="text-2xl font-bold text-gray-900">{member.personalInfo.fullName}</h2>
				<span class="badge {member.accountInfo.accountStatus === 'Active' ? 'badge-success' : 'badge-warning'}">
					{member.accountInfo.accountStatus}
				</span>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				<div>
					<p class="text-sm text-gray-600">Member ID</p>
					<p class="font-medium">{member.memberId}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">IC Number</p>
					<p class="font-medium">{member.icNumber.replace(/(\d{6})-(\d{2})-(\d{4})/, '$1-**-****')}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Age / Generation</p>
					<p class="font-medium">{member.personalInfo.age} / {member.personalInfo.generationGroup}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Gender</p>
					<p class="font-medium">{member.personalInfo.gender}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Region</p>
					<p class="font-medium">{member.personalInfo.region}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Date of Birth</p>
					<p class="font-medium">{formatDate(member.personalInfo.dateOfBirth)}</p>
				</div>
			</div>
		</div>

		<!-- Account Balance Card -->
		<div class="card bg-gradient-to-br from-green-50 to-white">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Account Balance</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				<div>
					<p class="text-sm text-gray-600">Account 1 (Retirement)</p>
					<p class="text-2xl font-bold text-green-700">{formatCurrency(member.accountInfo.akaun1Balance)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Account 2 (Flexible)</p>
					<p class="text-2xl font-bold text-green-700">{formatCurrency(member.accountInfo.akaun2Balance)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Total Balance</p>
					<p class="text-3xl font-bold text-green-800">{formatCurrency(member.accountInfo.totalBalance)}</p>
				</div>
			</div>
		</div>

		<!-- Employment Info Card -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Employment Information</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div>
					<p class="text-sm text-gray-600">Current Employer</p>
					<p class="font-medium">{member.employmentProfile.currentEmployer.employerName}</p>
					<p class="text-xs text-gray-500">ID: {member.employmentProfile.currentEmployer.employerId}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Job Category</p>
					<p class="font-medium">{member.employmentProfile.jobCategory}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Employment Status</p>
					<span class="badge {member.employmentProfile.employmentStatus === 'Active' ? 'badge-success' : 'badge-warning'}">
						{member.employmentProfile.employmentStatus}
					</span>
				</div>
				<div>
					<p class="text-sm text-gray-600">Start Date</p>
					<p class="font-medium">{formatDate(member.employmentProfile.currentEmployer.startDate)}</p>
				</div>
			</div>
		</div>

		<!-- Contribution Stats Card -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Contribution Statistics</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<div>
					<p class="text-sm text-gray-600">Average Monthly Wage</p>
					<p class="font-medium">{formatCurrency(member.contributionStats.avgMonthlyWage)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Average Monthly Contribution</p>
					<p class="font-medium">{formatCurrency(member.contributionStats.avgMonthly)}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Consecutive Months</p>
					<p class="font-medium">{member.contributionStats.consecutiveMonths}</p>
				</div>
				<div>
					<p class="text-sm text-gray-600">Total Lifetime</p>
					<p class="font-medium">{formatCurrency(member.contributionStats.totalLifetime)}</p>
				</div>
			</div>
			{#if member.contributionStats.hasGaps}
				<div class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
					<p class="text-sm text-yellow-800">
						⚠️ Contribution gaps detected: {member.contributionStats.gapMonths.length} missing month(s)
					</p>
				</div>
			{/if}
		</div>

		<!-- Compliance Card -->
		<div class="card">
			<h3 class="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h3>
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div>
					<p class="text-sm text-gray-600">Risk Score</p>
					<span class="badge {getRiskBadgeClass(member.complianceFlags.riskScore)}">
						{member.complianceFlags.riskScore}
					</span>
				</div>
				<div>
					<p class="text-sm text-gray-600">Last Audit Date</p>
					<p class="font-medium">{formatDate(member.complianceFlags.lastAuditDate)}</p>
				</div>
			</div>
			<div class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="flex items-center space-x-2">
					<span class={member.complianceFlags.hasIrregularities ? 'text-red-600' : 'text-green-600'}>
						{member.complianceFlags.hasIrregularities ? '✗' : '✓'}
					</span>
					<span class="text-sm">Irregularities</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class={member.complianceFlags.hasMissingContributions ? 'text-red-600' : 'text-green-600'}>
						{member.complianceFlags.hasMissingContributions ? '✗' : '✓'}
					</span>
					<span class="text-sm">Missing Contributions</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class={member.complianceFlags.hasWageDiscrepancies ? 'text-red-600' : 'text-green-600'}>
						{member.complianceFlags.hasWageDiscrepancies ? '✗' : '✓'}
					</span>
					<span class="text-sm">Wage Discrepancies</span>
				</div>
				<div class="flex items-center space-x-2">
					<span class={member.complianceFlags.hasActiveComplaints ? 'text-red-600' : 'text-green-600'}>
						{member.complianceFlags.hasActiveComplaints ? '✗' : '✓'}
					</span>
					<span class="text-sm">Active Complaints</span>
				</div>
			</div>
		</div>
	</div>
{/if}
