<script lang="ts">
	import { onMount } from 'svelte';
	import { getMemberDashboardStats, getEmployerDashboardStats } from '$lib/api';
	import type { DashboardStats } from '$lib/api';

	let memberStats: DashboardStats | null = null;
	let employerStats: DashboardStats | null = null;
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			const [memberData, employerData] = await Promise.all([
				getMemberDashboardStats(),
				getEmployerDashboardStats()
			]);
			memberStats = memberData;
			employerStats = employerData;
		} catch (err: any) {
			error = err.message || 'Failed to load dashboard statistics';
			console.error('Dashboard error:', err);
		} finally {
			loading = false;
		}
	});

	function formatCurrency(value: number): string {
		return `RM ${value.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
	}

	function formatNumber(value: number): string {
		return value.toLocaleString('en-MY');
	}
</script>

<svelte:head>
	<title>PensionFund Officer Dashboard - Home</title>
</svelte:head>

<div class="space-y-8">
	<!-- Page Header -->
	<div>
		<h1 class="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
		<p class="mt-2 text-sm text-gray-600">
			Comprehensive statistics and insights for member contributions and employer compliance.
		</p>
	</div>

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
				<p class="mt-4 text-gray-600">Loading dashboard...</p>
			</div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else}
		<!-- Quick Stats Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<!-- Total Members -->
			<div class="card bg-gradient-to-br from-blue-50 to-white border border-blue-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Members</p>
						<p class="text-2xl font-bold text-PensionFund-blue mt-1">
							{memberStats?.demographics?.recordCount
								? formatNumber(memberStats.demographics.recordCount)
								: '-'}
						</p>
					</div>
					<div class="p-3 bg-PensionFund-blue rounded-full">
						<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- Total Balance -->
			<div class="card bg-gradient-to-br from-green-50 to-white border border-green-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Balance</p>
						<p class="text-2xl font-bold text-green-700 mt-1">
							{memberStats?.balances?.totalBalance
								? formatCurrency(memberStats.balances.totalBalance)
								: '-'}
						</p>
					</div>
					<div class="p-3 bg-green-600 rounded-full">
						<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- Total Employers -->
			<div class="card bg-gradient-to-br from-purple-50 to-white border border-purple-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Total Employers</p>
						<p class="text-2xl font-bold text-purple-700 mt-1">
							{employerStats?.profiles?.recordCount
								? formatNumber(employerStats.profiles.recordCount)
								: '-'}
						</p>
					</div>
					<div class="p-3 bg-purple-600 rounded-full">
						<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- Compliance Issues -->
			<div class="card bg-gradient-to-br from-red-50 to-white border border-red-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm font-medium text-gray-600">Compliance Issues</p>
						<p class="text-2xl font-bold text-red-700 mt-1">
							{employerStats?.compliance?.withArrears
								? formatNumber(employerStats.compliance.withArrears)
								: '-'}
						</p>
					</div>
					<div class="p-3 bg-red-600 rounded-full">
						<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
							/>
						</svg>
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Links -->
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
			<a
				href="/members"
				class="card hover:shadow-lg transition-shadow border-2 border-transparent hover:border-PensionFund-blue"
			>
				<div class="flex items-center space-x-4">
					<div class="p-4 bg-PensionFund-lightblue rounded-lg">
						<svg class="w-8 h-8 text-PensionFund-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="text-lg font-semibold text-gray-900">Member Search</h3>
						<p class="text-sm text-gray-600">Search and manage member accounts</p>
					</div>
				</div>
			</a>

			<a
				href="/employers"
				class="card hover:shadow-lg transition-shadow border-2 border-transparent hover:border-PensionFund-blue"
			>
				<div class="flex items-center space-x-4">
					<div class="p-4 bg-purple-100 rounded-lg">
						<svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
							/>
						</svg>
					</div>
					<div>
						<h3 class="text-lg font-semibold text-gray-900">Employer Search</h3>
						<p class="text-sm text-gray-600">Monitor employer compliance and submissions</p>
					</div>
				</div>
			</a>
		</div>

		<!-- Last Updated -->
		{#if memberStats?.refreshedAt || employerStats?.refreshedAt}
			<div class="text-center text-sm text-gray-500 mt-8">
				Last updated: {new Date(
					memberStats?.refreshedAt || employerStats?.refreshedAt || ''
				).toLocaleString('en-MY')}
			</div>
		{/if}
	{/if}
</div>
