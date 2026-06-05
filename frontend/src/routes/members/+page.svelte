<script lang="ts">
	import { onMount } from 'svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import FacetPanel from '$lib/components/FacetPanel.svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { searchMembers, type Member, type SearchFilters } from '$lib/api';
	import { goto } from '$app/navigation';

	let searchText = '';
	let loading = false;
	let results: Member[] = [];
	let facets: any[] = [];
	let selectedFilters: Record<string, string[]> = {};
	let totalCount: number | undefined;
	let hasMore = false;
	let cursor: string | null = null;
	let currentPage = 1;
	let error = '';

	// Computed statistics from results
	$: stats = {
		total: results.length,
		activeMembers: results.filter((m) => m.accountInfo.accountStatus === 'Active').length,
		averageBalance:
			results.length > 0
				? results.reduce((sum, m) => sum + m.accountInfo.totalBalance, 0) / results.length
				: 0,
		highRiskCount: results.filter((m) => m.complianceFlags.riskScore === 'High' || m.complianceFlags.riskScore === 'Critical').length
	};

	// Column definitions for the data table
	const columns = [
		{ key: 'memberId', label: 'Member ID' },
		{
			key: 'personalInfo.fullName',
			label: 'Full Name',
			formatter: (value: string, row: Member) => {
				const masked = row.icNumber.replace(/(\d{6})-(\d{2})-(\d{4})/, '$1-**-****');
				return `<div><div class="font-medium">${value}</div><div class="text-xs text-gray-500">IC: ${masked}</div></div>`;
			}
		},
		{ key: 'personalInfo.region', label: 'Region' },
		{
			key: 'employmentProfile.currentEmployer.employerName',
			label: 'Current Employer',
			formatter: (value: string, row: Member) => {
				return `<div><div>${value}</div><div class="text-xs text-gray-500">${row.employmentProfile.jobCategory}</div></div>`;
			}
		},
		{
			key: 'accountInfo.totalBalance',
			label: 'Total Balance',
			formatter: (value: number) =>
				`<span class="font-medium text-green-700">RM ${value.toLocaleString('en-MY', { minimumFractionDigits: 2 })}</span>`
		},
		{
			key: 'accountInfo.accountStatus',
			label: 'Status',
			formatter: (value: string) => {
				const badgeClass =
					value === 'Active'
						? 'badge-success'
						: value === 'Inactive'
							? 'badge-warning'
							: 'badge-danger';
				return `<span class="badge ${badgeClass}">${value}</span>`;
			}
		}
	];

	async function performSearch(resetPage = true) {
		if (resetPage) {
			currentPage = 1;
			cursor = null;
		}

		loading = true;
		error = '';

		try {
			// Build filters object
			const filters: SearchFilters = {};
			for (const [field, values] of Object.entries(selectedFilters)) {
				if (values.length > 0) {
					(filters as any)[field] = values;
				}
			}

			const response = await searchMembers(
				searchText || undefined,
				Object.keys(filters).length > 0 ? filters : undefined,
				{ cursor: cursor || undefined }
			);

			results = response.results;
			facets = response.facets || [];
			totalCount = response.totalCount;
			hasMore = response.pagination.hasMore;
			cursor = response.pagination.cursor;
		} catch (err: any) {
			error = err.message || 'Failed to search members';
			console.error('Search error:', err);
		} finally {
			loading = false;
		}
	}

	function handleFilterChange(event: CustomEvent) {
		const { field, values } = event.detail;
		if (values.length === 0) {
			delete selectedFilters[field];
		} else {
			selectedFilters[field] = values;
		}
		selectedFilters = { ...selectedFilters };
		performSearch(true);
	}

	function handleClearFilters() {
		selectedFilters = {};
		performSearch(true);
	}

	function handleRowClick(member: Member) {
		goto(`/members/${member.memberId}`);
	}

	function handleNext() {
		currentPage++;
		performSearch(false);
	}

	function handlePrevious() {
		if (currentPage > 1) {
			currentPage--;
			// Note: Going back requires storing previous cursors
			// For simplicity, we'll reset to page 1
			currentPage = 1;
			cursor = null;
			performSearch(false);
		}
	}

	onMount(() => {
		performSearch();
	});
</script>

<svelte:head>
	<title>Member Search - PensionFund Officer Dashboard</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div>
		<h1 class="text-3xl font-bold text-gray-900">Member Search</h1>
		<p class="mt-2 text-sm text-gray-600">
			Search and filter members by name, IC number, employment status, and more.
		</p>
	</div>

	<!-- Search Bar -->
	<SearchBar
		placeholder="Search by name, Member ID, or IC number..."
		bind:value={searchText}
		{loading}
		on:search={() => performSearch(true)}
		on:clear={() => {
			searchText = '';
			performSearch(true);
		}}
	/>

	{#if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{/if}

	<!-- Statistics Cards -->
	{#if !loading && results.length > 0}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<!-- Total Members -->
			<div class="card bg-gradient-to-br from-blue-50 to-white border border-blue-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Results</p>
						<p class="text-2xl font-bold text-PensionFund-blue">{stats.total.toLocaleString()}</p>
					</div>
					<div class="p-2 bg-PensionFund-blue rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- Active Members -->
			<div class="card bg-gradient-to-br from-green-50 to-white border border-green-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Active Members</p>
						<p class="text-2xl font-bold text-green-700">{stats.activeMembers.toLocaleString()}</p>
						<p class="text-xs text-gray-500 mt-1">
							{((stats.activeMembers / stats.total) * 100).toFixed(1)}%
						</p>
					</div>
					<div class="p-2 bg-green-600 rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- Average Balance -->
			<div class="card bg-gradient-to-br from-purple-50 to-white border border-purple-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Avg Balance</p>
						<p class="text-2xl font-bold text-purple-700">
							RM {stats.averageBalance.toLocaleString('en-MY', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
						</p>
					</div>
					<div class="p-2 bg-purple-600 rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

			<!-- High Risk -->
			<div class="card bg-gradient-to-br from-red-50 to-white border border-red-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">High/Critical Risk</p>
						<p class="text-2xl font-bold text-red-700">{stats.highRiskCount.toLocaleString()}</p>
						<p class="text-xs text-gray-500 mt-1">
							{stats.total > 0 ? ((stats.highRiskCount / stats.total) * 100).toFixed(1) : '0.0'}%
						</p>
					</div>
					<div class="p-2 bg-red-600 rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
	{/if}

	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
		<!-- Facet Panel (Sidebar) -->
		<div class="lg:col-span-1">
			<FacetPanel
				{facets}
				{selectedFilters}
				on:filterChange={handleFilterChange}
				on:clearFilters={handleClearFilters}
			/>
		</div>

		<!-- Results Table -->
		<div class="lg:col-span-3 space-y-4">
			<!-- Results Count -->
			{#if !loading && results.length > 0}
				<div class="text-sm text-gray-600">
					Showing <span class="font-medium">{results.length}</span> results
					{#if totalCount !== undefined}
						out of approximately <span class="font-medium">{totalCount.toLocaleString()}</span>
					{/if}
				</div>
			{/if}

			<!-- Data Table -->
			<DataTable {columns} data={results} {loading} onRowClick={handleRowClick} />

			<!-- Pagination -->
			{#if results.length > 0}
				<Pagination
					{hasMore}
					{totalCount}
					{currentPage}
					{loading}
					on:next={handleNext}
					on:previous={handlePrevious}
				/>
			{/if}
		</div>
	</div>
</div>
