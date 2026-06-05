<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let placeholder: string = 'Search...';
	export let value: string = '';
	export let loading: boolean = false;

	const dispatch = createEventDispatcher();

	function handleSearch() {
		dispatch('search', value);
	}

	function handleClear() {
		value = '';
		dispatch('clear');
	}
</script>

<div class="w-full">
	<div class="relative">
		<div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
			<svg
				class="w-5 h-5 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				/>
			</svg>
		</div>
		<input
			type="text"
			bind:value
			on:keydown={(e) => e.key === 'Enter' && handleSearch()}
			{placeholder}
			class="input-field pl-10 pr-20"
			disabled={loading}
		/>
		<div class="absolute inset-y-0 right-0 flex items-center pr-2 gap-1">
			{#if value}
				<button
					type="button"
					on:click={handleClear}
					class="p-1.5 text-gray-400 hover:text-gray-600 rounded"
					disabled={loading}
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			{/if}
			<button
				type="button"
				on:click={handleSearch}
				class="btn-primary py-1.5 px-3"
				disabled={loading}
			>
				{loading ? 'Searching...' : 'Search'}
			</button>
		</div>
	</div>
</div>
