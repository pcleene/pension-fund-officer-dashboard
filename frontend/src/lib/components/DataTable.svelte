<script lang="ts">
	export let columns: Array<{
		key: string;
		label: string;
		formatter?: (value: any, row: any) => string;
	}> = [];

	export let data: any[] = [];
	export let loading: boolean = false;
	export let onRowClick: ((row: any) => void) | undefined = undefined;

	function formatValue(column: any, row: any): string {
		const value = getNestedValue(row, column.key);
		if (column.formatter) {
			return column.formatter(value, row);
		}
		return value?.toString() || '-';
	}

	function getNestedValue(obj: any, path: string): any {
		return path.split('.').reduce((current, part) => current?.[part], obj);
	}
</script>

<div class="card overflow-hidden p-0">
	<div class="overflow-x-auto">
		<table class="min-w-full divide-y divide-gray-200">
			<thead class="bg-gray-50">
				<tr>
					{#each columns as column}
						<th
							scope="col"
							class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
						>
							{column.label}
						</th>
					{/each}
				</tr>
			</thead>
			<tbody class="bg-white divide-y divide-gray-200">
				{#if loading}
					<tr>
						<td colspan={columns.length} class="px-6 py-8 text-center text-gray-500">
							<div class="flex justify-center items-center">
								<svg class="animate-spin h-8 w-8 text-PensionFund-blue" fill="none" viewBox="0 0 24 24">
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									/>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									/>
								</svg>
								<span class="ml-2">Loading...</span>
							</div>
						</td>
					</tr>
				{:else if data.length === 0}
					<tr>
						<td colspan={columns.length} class="px-6 py-8 text-center text-gray-500">
							No results found
						</td>
					</tr>
				{:else}
					{#each data as row, i (i)}
						<tr
							class={onRowClick ? 'hover:bg-gray-50 cursor-pointer' : ''}
							on:click={() => onRowClick?.(row)}
						>
							{#each columns as column}
								<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
									{@html formatValue(column, row)}
								</td>
							{/each}
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</div>
