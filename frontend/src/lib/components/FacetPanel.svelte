<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let facets: Array<{
		field: string;
		label: string;
		buckets: Array<{ value: string; count: number }>;
	}> = [];

	export let selectedFilters: Record<string, string[]> = {};

	const dispatch = createEventDispatcher();

	function toggleFilter(field: string, value: string) {
		const currentFilters = selectedFilters[field] || [];
		let newFilters: string[];

		if (currentFilters.includes(value)) {
			newFilters = currentFilters.filter((v) => v !== value);
		} else {
			newFilters = [...currentFilters, value];
		}

		dispatch('filterChange', {
			field,
			values: newFilters
		});
	}

	function clearFilters() {
		dispatch('clearFilters');
	}

	function isSelected(field: string, value: string): boolean {
		return (selectedFilters[field] || []).includes(value);
	}

	function hasActiveFilters(): boolean {
		return Object.values(selectedFilters).some((filters) => filters.length > 0);
	}
</script>

<div class="card">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold text-gray-900">Filters</h3>
		{#if hasActiveFilters()}
			<button on:click={clearFilters} class="text-sm text-PensionFund-blue hover:text-PensionFund-navy">
				Clear All
			</button>
		{/if}
	</div>

	{#if facets.length === 0}
		<p class="text-sm text-gray-500">No filters available</p>
	{:else}
		<div class="space-y-6">
			{#each facets as facet}
				<div class="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
					<h4 class="text-sm font-medium text-gray-900 mb-2">{facet.label}</h4>
					<div class="space-y-2 max-h-64 overflow-y-auto">
						{#each facet.buckets as bucket}
							<label class="flex items-center cursor-pointer hover:bg-gray-50 p-1 rounded">
								<input
									type="checkbox"
									checked={isSelected(facet.field, bucket.value)}
									on:change={() => toggleFilter(facet.field, bucket.value)}
									class="w-4 h-4 text-PensionFund-blue border-gray-300 rounded focus:ring-PensionFund-blue"
								/>
								<span class="ml-2 text-sm text-gray-700 flex-1">{bucket.value || 'N/A'}</span>
								<span class="text-xs text-gray-500">({bucket.count.toLocaleString()})</span>
							</label>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
