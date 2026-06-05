<script lang="ts">
	import { onMount } from 'svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import FacetPanel from '$lib/components/FacetPanel.svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import Pagination from '$lib/components/Pagination.svelte';
	import { searchEmployers, type Employer, type SearchFilters } from '$lib/api';
	import { goto } from '$app/navigation';

	let searchText = '';
	let loading = false;
	let results: Employer[] = [];
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
		averageOnTimeRate:
			results.length > 0
				? results.reduce((sum, e) => sum + e.contributionStats.onTimeRate, 0) / results.length
				: 0,
		withArrears: results.filter((e) => e.complianceStatus.hasArrears).length,
		criticalRisk: results.filter((e) => e.complianceStatus.riskRating === 'Critical' || e.complianceStatus.riskRating === 'High').length
	};

	// Column definitions for the data table
	const columns = [
		{ key: 'employerId', label: 'Employer ID' },
		{
			key: 'companyProfile.companyName',
			label: 'Company Name',
			formatter: (value: string, row: Employer) => {
				return `<div><div class="font-medium">${value}</div><div class="text-xs text-gray-500">${row.companyProfile.industryClassification.sector}</div></div>`;
			}
		},
		{
			key: 'companyProfile.businessAddress.state',
			label: 'State',
			formatter: (value: string, row: Employer) => {
				return `<div><div>${value}</div><div class="text-xs text-gray-500">${row.companyProfile.businessAddress.city}</div></div>`;
			}
		},
		{
			key: 'memberSummary.totalMembers',
			label: 'Members',
			formatter: (value: number, row: Employer) => {
				return `<div><div class="font-medium">${value.toLocaleString()}</div><div class="text-xs text-gray-500">${row.companyProfile.companySize}</div></div>`;
			}
		},
		{
			key: 'contributionStats.onTimeRate',
			label: 'On-Time Rate',
			formatter: (value: number) => {
				const percentage = (value * 100).toFixed(1);
				const badgeClass =
					value >= 0.9 ? 'badge-success' : value >= 0.7 ? 'badge-warning' : 'badge-danger';
				return `<span class="badge ${badgeClass}">${percentage}%</span>`;
			}
		},
		{
			key: 'complianceStatus.riskRating',
			label: 'Risk Rating',
			formatter: (value: string) => {
				const badgeClass =
					value === 'Low'
						? 'badge-success'
						: value === 'Medium'
							? 'badge-info'
							: value === 'High'
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

			const response = await searchEmployers(
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
			error = err.message || 'Failed to search employers';
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

	function handleRowClick(employer: Employer) {
		goto(`/employers/${employer.employerId}`);
	}

	function handleNext() {
		currentPage++;
		performSearch(false);
	}

	function handlePrevious() {
		if (currentPage > 1) {
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
	<title>Employer Search - PensionFund Officer Dashboard</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Header -->
	<div>
		<h1 class="text-3xl font-bold text-gray-900">Employer Search</h1>
		<p class="mt-2 text-sm text-gray-600">
			Search and monitor employer compliance, contribution submissions, and workforce statistics.
		</p>
	</div>

	<!-- Search Bar -->
	<SearchBar
		placeholder="Search by company name, Employer ID, or registration number..."
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
			<!-- Total Employers -->
			<div class="card bg-gradient-to-br from-purple-50 to-white border border-purple-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Results</p>
						<p class="text-2xl font-bold text-purple-700">{stats.total.toLocaleString()}</p>
					</div>
					<div class="p-2 bg-purple-600 rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

			<!-- Average On-Time Rate -->
			<div class="card bg-gradient-to-br from-green-50 to-white border border-green-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">Avg On-Time Rate</p>
						<p class="text-2xl font-bold text-green-700">
							{(stats.averageOnTimeRate * 100).toFixed(1)}%
						</p>
					</div>
					<div class="p-2 bg-green-600 rounded-lg">
						<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
					</div>
				</div>
			</div>

			<!-- With Arrears -->
			<div class="card bg-gradient-to-br from-orange-50 to-white border border-orange-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">With Arrears</p>
						<p class="text-2xl font-bold text-orange-700">{stats.withArrears.toLocaleString()}</p>
						<p class="text-xs text-gray-500 mt-1">
							{stats.total > 0 ? ((stats.withArrears / stats.total) * 100).toFixed(1) : '0.0'}%
						</p>
					</div>
					<div class="p-2 bg-orange-600 rounded-lg">
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

			<!-- High/Critical Risk -->
			<div class="card bg-gradient-to-br from-red-50 to-white border border-red-100">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-gray-600">High/Critical Risk</p>
						<p class="text-2xl font-bold text-red-700">{stats.criticalRisk.toLocaleString()}</p>
						<p class="text-xs text-gray-500 mt-1">
							{stats.total > 0 ? ((stats.criticalRisk / stats.total) * 100).toFixed(1) : '0.0'}%
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
