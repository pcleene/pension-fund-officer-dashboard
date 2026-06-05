<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let hasMore: boolean = false;
	export let totalCount: number | undefined = undefined;
	export let currentPage: number = 1;
	export let loading: boolean = false;

	const dispatch = createEventDispatcher();

	function handleNext() {
		if (hasMore && !loading) {
			dispatch('next');
		}
	}

	function handlePrevious() {
		if (currentPage > 1 && !loading) {
			dispatch('previous');
		}
	}
</script>

<div class="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6">
	<div class="flex flex-1 justify-between sm:hidden">
		<button
			on:click={handlePrevious}
			disabled={currentPage === 1 || loading}
			class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
		>
			Previous
		</button>
		<button
			on:click={handleNext}
			disabled={!hasMore || loading}
			class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
		>
			Next
		</button>
	</div>
	<div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
		<div>
			<p class="text-sm text-gray-700">
				Page <span class="font-medium">{currentPage}</span>
				{#if totalCount !== undefined}
					<span class="text-gray-500">
						of approximately <span class="font-medium">{Math.ceil(totalCount / 20)}</span> pages
					</span>
				{/if}
			</p>
		</div>
		<div>
			<nav class="inline-flex gap-2" aria-label="Pagination">
				<button
					on:click={handlePrevious}
					disabled={currentPage === 1 || loading}
					class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Previous
				</button>
				<button
					on:click={handleNext}
					disabled={!hasMore || loading}
					class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Next
				</button>
			</nav>
		</div>
	</div>
</div>
