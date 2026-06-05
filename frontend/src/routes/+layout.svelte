<script lang="ts">
	import '../app.css';

	let currentPath = '';

	// Simple navigation tracking
	if (typeof window !== 'undefined') {
		currentPath = window.location.pathname;
	}
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-PensionFund-blue shadow-lg">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center py-4">
				<div class="flex items-center space-x-4">
					<div class="flex-shrink-0">
						<h1 class="text-2xl font-bold text-white">PensionFund Officer Dashboard</h1>
					</div>
				</div>
				<nav class="flex space-x-4">
					<a
						href="/"
						class="text-white hover:bg-PensionFund-navy px-3 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Home
					</a>
					<a
						href="/members"
						class="text-white hover:bg-PensionFund-navy px-3 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Members
					</a>
					<a
						href="/employers"
						class="text-white hover:bg-PensionFund-navy px-3 py-2 rounded-md text-sm font-medium transition-colors"
					>
						Employers
					</a>
				</nav>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<slot />
	</main>

	<!-- Footer -->
	<footer class="bg-white border-t border-gray-200 mt-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<p class="text-center text-sm text-gray-500">
				© 2024 PensionFund. Internal Use Only.
			</p>
		</div>
	</footer>
</div>
