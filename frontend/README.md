# Pension Fund Officer Dashboard - Frontend (SvelteKit)

Modern, responsive frontend for the PensionFund Officer Dashboard using SvelteKit and Tailwind CSS.

## Quick Start

### 1. Initialize SvelteKit Project

```bash
cd frontend
npm create svelte@latest .
# Choose:
# - Skeleton project
# - TypeScript: Yes
# - ESLint: Yes
# - Prettier: Yes
# - Playwright: No (optional)
# - Vitest: No (optional)

npm install
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install

# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# HTTP client
npm install axios

# Charts
npm install chart.js

# Date utilities
npm install date-fns
```

### 3. Configure Tailwind CSS

**`tailwind.config.js`:**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'navy': {
          DEFAULT: '#1E3A8A',
          50: '#EEF2FF',
          100: '#E0E7FF',
          200: '#C7D2FE',
          300: '#A5B4FC',
          400: '#818CF8',
          500: '#6366F1',
          600: '#4F46E5',
          700: '#4338CA',
          800: '#3730A3',
          900: '#1E3A8A',
        },
        'sky': {
          DEFAULT: '#0EA5E9',
          50: '#F0F9FF',
          100: '#E0F2FE',
          200: '#BAE6FD',
          300: '#7DD3FC',
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1',
          800: '#075985',
          900: '#0C4A6E',
        },
        'gold': {
          DEFAULT: '#F59E0B',
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
      },
    },
  },
  plugins: [],
}
```

**`src/app.css`:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
body {
  @apply bg-gray-50 text-gray-900;
}

.btn-primary {
  @apply px-4 py-2 bg-navy text-white rounded-lg hover:bg-navy-800 transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-white text-navy border border-navy rounded-lg hover:bg-navy-50 transition-colors;
}

.card {
  @apply bg-white rounded-lg shadow-md p-6;
}

.badge-success {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800;
}

.badge-warning {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800;
}

.badge-danger {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800;
}
```

### 4. Create API Client

**`src/lib/api/client.ts`:**

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token here if needed
    // const token = localStorage.getItem('auth_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
```

**`src/lib/api/members.ts`:**

```typescript
import { apiClient } from './client';

export interface MemberSearchParams {
  searchText?: string;
  accountStatus?: string[];
  region?: string[];
  generation?: string[];
  jobCategory?: string[];
  riskScore?: string[];
  employmentStatus?: string[];
  minBalance?: number;
  maxBalance?: number;
  limit?: number;
  cursor?: string;
  direction?: 'next' | 'prev';
  useFacets?: boolean;
}

export const membersApi = {
  search: async (params: MemberSearchParams) => {
    const response = await apiClient.get('/members/search', { params });
    return response.data;
  },

  vectorSearch: async (query: string, filters?: any, limit = 20) => {
    const response = await apiClient.post('/members/search/vector', {
      query,
      filters,
      limit,
    });
    return response.data;
  },

  getById: async (memberId: string) => {
    const response = await apiClient.get(`/members/${memberId}`);
    return response.data;
  },

  getContributions: async (memberId: string, limit = 20, offset = 0) => {
    const response = await apiClient.get(`/members/${memberId}/contributions`, {
      params: { limit, offset },
    });
    return response.data;
  },

  getEmployers: async (memberId: string) => {
    const response = await apiClient.get(`/members/${memberId}/employers`);
    return response.data;
  },

  getWithdrawals: async (memberId: string) => {
    const response = await apiClient.get(`/members/${memberId}/withdrawals`);
    return response.data;
  },
};
```

**`src/lib/api/employers.ts`:**

```typescript
import { apiClient } from './client';

export interface EmployerSearchParams {
  searchText?: string;
  accountStatus?: string[];
  sector?: string[];
  companySize?: string[];
  state?: string[];
  accountType?: string[];
  riskRating?: string[];
  hasArrears?: boolean;
  hasLegalCases?: boolean;
  productTags?: string[];
  limit?: number;
  cursor?: string;
  direction?: 'next' | 'prev';
  useFacets?: boolean;
}

export const employersApi = {
  search: async (params: EmployerSearchParams) => {
    const response = await apiClient.get('/employers/search', { params });
    return response.data;
  },

  vectorSearch: async (query: string, filters?: any, limit = 20) => {
    const response = await apiClient.post('/employers/search/vector', {
      query,
      filters,
      limit,
    });
    return response.data;
  },

  getById: async (employerId: string) => {
    const response = await apiClient.get(`/employers/${employerId}`);
    return response.data;
  },

  getSubmissions: async (employerId: string, limit = 20, offset = 0) => {
    const response = await apiClient.get(`/employers/${employerId}/submissions`, {
      params: { limit, offset },
    });
    return response.data;
  },

  getMembers: async (employerId: string, limit = 50, offset = 0) => {
    const response = await apiClient.get(`/employers/${employerId}/members`, {
      params: { limit, offset },
    });
    return response.data;
  },

  getCompliance: async (employerId: string) => {
    const response = await apiClient.get(`/employers/${employerId}/compliance`);
    return response.data;
  },
};
```

**`src/lib/api/dashboard.ts`:**

```typescript
import { apiClient } from './client';

export const dashboardApi = {
  getMemberStats: async () => {
    const response = await apiClient.get('/dashboard/members/stats');
    return response.data;
  },

  getEmployerStats: async () => {
    const response = await apiClient.get('/dashboard/employers/stats');
    return response.data;
  },

  refreshViews: async (views: string[] = ['all']) => {
    const response = await apiClient.post('/dashboard/refresh', { views });
    return response.data;
  },
};
```

### 5. Key Components

#### `src/lib/components/SearchBar.svelte`

```svelte
<script lang="ts">
  export let searchText = '';
  export let onSearch: (text: string) => void;
  export let onVectorSearch: (text: string) => void;
  export let searchMode: 'text' | 'vector' = 'text';

  let localSearchText = searchText;

  function handleSearch() {
    if (searchMode === 'text') {
      onSearch(localSearchText);
    } else {
      onVectorSearch(localSearchText);
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      handleSearch();
    }
  }
</script>

<div class="search-bar card">
  <div class="flex gap-4">
    <!-- Search Mode Toggle -->
    <div class="flex gap-2">
      <button
        class="btn-toggle {searchMode === 'text' ? 'active' : ''}"
        on:click={() => (searchMode = 'text')}
      >
        Text Search
      </button>
      <button
        class="btn-toggle {searchMode === 'vector' ? 'active' : ''}"
        on:click={() => (searchMode = 'vector')}
      >
        AI Search
      </button>
    </div>

    <!-- Search Input -->
    <div class="flex-1">
      <input
        type="text"
        bind:value={localSearchText}
        on:keypress={handleKeyPress}
        placeholder={searchMode === 'text'
          ? 'Search by name, ID, or IC number...'
          : 'Ask in natural language (e.g., "members with gaps in Kuala Lumpur")'}
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-navy"
      />
    </div>

    <!-- Search Button -->
    <button class="btn-primary" on:click={handleSearch}>
      Search
    </button>
  </div>
</div>

<style>
  .btn-toggle {
    @apply px-4 py-2 border border-gray-300 rounded-lg transition-colors;
  }

  .btn-toggle.active {
    @apply bg-navy text-white border-navy;
  }

  .btn-toggle:not(.active) {
    @apply bg-white text-gray-700 hover:bg-gray-50;
  }
</style>
```

#### `src/lib/components/DataTable.svelte`

```svelte
<script lang="ts">
  export let columns: Array<{ key: string; label: string; format?: (value: any) => string }>;
  export let data: Array<any>;
  export let onRowClick: (row: any) => void = () => {};

  function getValue(row: any, key: string) {
    return key.split('.').reduce((obj, k) => obj?.[k], row);
  }
</script>

<div class="overflow-x-auto">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        {#each columns as column}
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            {column.label}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      {#each data as row}
        <tr class="hover:bg-gray-50 cursor-pointer" on:click={() => onRowClick(row)}>
          {#each columns as column}
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {#if column.format}
                {column.format(getValue(row, column.key))}
              {:else}
                {getValue(row, column.key) || '-'}
              {/if}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>

{#if data.length === 0}
  <div class="text-center py-12">
    <p class="text-gray-500">No data found</p>
  </div>
{/if}
```

#### `src/lib/components/FacetPanel.svelte`

```svelte
<script lang="ts">
  export let facets: Array<{
    field: string;
    fieldKey: string;
    buckets: Array<{ value: string; count: number }>;
  }>;
  export let selectedFilters: Record<string, string[]> = {};
  export let onFilterChange: (filters: Record<string, string[]>) => void;

  function toggleFilter(fieldKey: string, value: string) {
    if (!selectedFilters[fieldKey]) {
      selectedFilters[fieldKey] = [];
    }

    const index = selectedFilters[fieldKey].indexOf(value);
    if (index > -1) {
      selectedFilters[fieldKey].splice(index, 1);
    } else {
      selectedFilters[fieldKey].push(value);
    }

    // Clean up empty arrays
    if (selectedFilters[fieldKey].length === 0) {
      delete selectedFilters[fieldKey];
    }

    selectedFilters = selectedFilters;
    onFilterChange(selectedFilters);
  }

  function clearFilters() {
    selectedFilters = {};
    onFilterChange(selectedFilters);
  }
</script>

<div class="facet-panel bg-white border-r border-gray-200 p-4 overflow-y-auto h-screen">
  <div class="flex justify-between items-center mb-4">
    <h3 class="font-semibold text-gray-900">Filters</h3>
    <button class="text-sm text-navy hover:underline" on:click={clearFilters}>
      Clear All
    </button>
  </div>

  {#each facets as facet}
    <div class="facet-group mb-6">
      <h4 class="font-medium text-sm text-gray-700 mb-2">{facet.field}</h4>

      {#each facet.buckets as bucket}
        <label class="flex items-center gap-2 py-1 cursor-pointer hover:bg-gray-50 px-2 rounded">
          <input
            type="checkbox"
            checked={selectedFilters[facet.fieldKey]?.includes(bucket.value)}
            on:change={() => toggleFilter(facet.fieldKey, bucket.value)}
            class="rounded text-navy focus:ring-navy"
          />
          <span class="text-sm text-gray-700 flex-1">{bucket.value}</span>
          <span class="text-xs text-gray-500">({bucket.count})</span>
        </label>
      {/each}
    </div>
  {/each}
</div>
```

### 6. Page Routes

#### `src/routes/+layout.svelte`

```svelte
<script lang="ts">
  import '../app.css';
  import { page } from '$app/stores';
</script>

<div class="min-h-screen flex flex-col">
  <!-- Header -->
  <header class="bg-navy text-white shadow-lg">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold">PensionFund PensionFund Officer Dashboard</h1>
        <nav class="flex gap-6">
          <a href="/members" class="hover:text-gold transition-colors" class:active={$page.url.pathname.startsWith('/members')}>
            Members
          </a>
          <a href="/employers" class="hover:text-gold transition-colors" class:active={$page.url.pathname.startsWith('/employers')}>
            Employers
          </a>
        </nav>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex-1">
    <slot />
  </main>

  <!-- Footer -->
  <footer class="bg-gray-800 text-white py-4">
    <div class="container mx-auto px-4 text-center text-sm">
      &copy; 2025 PensionFund Malaysia. All rights reserved.
    </div>
  </footer>
</div>

<style>
  a.active {
    @apply text-gold border-b-2 border-gold pb-1;
  }
</style>
```

#### `src/routes/members/+page.svelte`

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import SearchBar from '$lib/components/SearchBar.svelte';
  import FacetPanel from '$lib/components/FacetPanel.svelte';
  import DataTable from '$lib/components/DataTable.svelte';
  import { membersApi } from '$lib/api/members';
  import { dashboardApi } from '$lib/api/dashboard';
  import { goto } from '$app/navigation';

  let searchText = '';
  let searchMode: 'text' | 'vector' = 'text';
  let members = [];
  let facets = [];
  let selectedFilters = {};
  let pagination = null;
  let loading = false;
  let dashboardStats = null;

  const columns = [
    { key: 'memberId', label: 'Member ID' },
    { key: 'personalInfo.fullName', label: 'Full Name' },
    { key: 'personalInfo.region', label: 'Region' },
    { key: 'employmentProfile.currentEmployer.employerName', label: 'Employer' },
    { key: 'accountInfo.accountStatus', label: 'Status' },
    {
      key: 'accountInfo.totalBalance',
      label: 'Total Balance',
      format: (val) => `RM ${val?.toLocaleString() || '0'}`
    },
    { key: 'complianceFlags.riskScore', label: 'Risk' }
  ];

  onMount(async () => {
    await loadDashboardStats();
    await searchMembers();
  });

  async function loadDashboardStats() {
    try {
      dashboardStats = await dashboardApi.getMemberStats();
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  }

  async function searchMembers() {
    loading = true;
    try {
      const result = await membersApi.search({
        searchText,
        ...selectedFilters,
        useFacets: true
      });

      members = result.results;
      facets = result.facets || [];
      pagination = result.pagination;
    } catch (error) {
      console.error('Error searching members:', error);
    } finally {
      loading = false;
    }
  }

  async function vectorSearchMembers(query: string) {
    loading = true;
    try {
      const result = await membersApi.vectorSearch(query, selectedFilters);
      members = result.results;
      pagination = result.pagination;
    } catch (error) {
      console.error('Error in vector search:', error);
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filters: Record<string, string[]>) {
    selectedFilters = filters;
    searchMembers();
  }

  function handleRowClick(member: any) {
    goto(`/members/${member.memberId}`);
  }
</script>

<div class="flex">
  <!-- Left Sidebar - Facets -->
  <div class="w-64">
    <FacetPanel {facets} {selectedFilters} onFilterChange={handleFilterChange} />
  </div>

  <!-- Main Content -->
  <div class="flex-1 p-6">
    <!-- Dashboard Stats -->
    {#if dashboardStats}
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="card">
          <p class="text-sm text-gray-600">Total Members</p>
          <p class="text-3xl font-bold text-navy">
            {dashboardStats.demographics?.recordCount?.toLocaleString() || '0'}
          </p>
        </div>
        <!-- Add more stat cards -->
      </div>
    {/if}

    <!-- Search Bar -->
    <SearchBar
      {searchText}
      {searchMode}
      onSearch={searchMembers}
      onVectorSearch={vectorSearchMembers}
    />

    <!-- Results Table -->
    <div class="mt-6 card">
      {#if loading}
        <div class="text-center py-12">
          <p class="text-gray-500">Loading...</p>
        </div>
      {:else}
        <DataTable {columns} data={members} onRowClick={handleRowClick} />
      {/if}

      <!-- Pagination -->
      {#if pagination}
        <div class="flex justify-between items-center mt-4 pt-4 border-t">
          <p class="text-sm text-gray-600">
            Showing {pagination.currentPageSize} results
          </p>
          <div class="flex gap-2">
            <button class="btn-secondary" disabled={!pagination.prevCursor}>
              Previous
            </button>
            <button class="btn-secondary" disabled={!pagination.hasMore}>
              Next
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
```

### 7. Environment Variables

**`.env.example`:**

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 8. Run Development Server

```bash
npm run dev
```

Visit: http://localhost:5173

## Production Build

```bash
npm run build
npm run preview
```

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Other Platforms

- Netlify
- Railway
- AWS Amplify
- Cloudflare Pages

## Next Steps

1. Complete the employer pages following the same pattern as members
2. Add member and employer detail pages
3. Implement charts using Chart.js
4. Add loading states and error handling
5. Implement authentication (if needed)
6. Add responsive design for mobile
7. Optimize performance (lazy loading, code splitting)

## Resources

- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
