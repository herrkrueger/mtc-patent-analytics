<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	// Reactive statement to get current route
	let currentRoute = $derived($page.url.pathname);

	const routes = [
		{ path: '/', label: 'Tree View', icon: '🌳' },
		{ path: '/sankey', label: 'Sankey Flow', icon: '📊' }
	];

	async function navigateTo(path: string) {
		await goto(path);
	}
</script>

<nav 
	class="navigation" 
	role="navigation" 
	aria-label="Visualization type navigation"
>
	<div class="nav-container">
		<h2 class="nav-title">IPC Explorer</h2>
		<div class="nav-buttons">
			{#each routes as route}
				<button
					class="nav-button {currentRoute === route.path ? 'active' : ''}"
					onclick={() => navigateTo(route.path)}
					aria-current={currentRoute === route.path ? 'page' : undefined}
				>
					<span class="nav-icon" aria-hidden="true">{route.icon}</span>
					<span class="nav-label">{route.label}</span>
				</button>
			{/each}
		</div>
	</div>
</nav>

<style>
	.navigation {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		background: rgba(0, 0, 0, 0.9);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
		padding: 0;
	}

	.nav-container {
		display: flex;
		align-items: center;
		justify-content: space-between;
		max-width: 1200px;
		margin: 0 auto;
		padding: 12px 20px;
	}

	.nav-title {
		color: white;
		font-size: 1.2rem;
		font-weight: 700;
		margin: 0;
		letter-spacing: -0.025em;
	}

	.nav-buttons {
		display: flex;
		gap: 8px;
	}

	.nav-button {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 16px;
		background: transparent;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 8px;
		color: rgba(255, 255, 255, 0.8);
		font-size: 0.9rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		text-decoration: none;
	}

	.nav-button:hover {
		background: rgba(255, 255, 255, 0.1);
		border-color: rgba(255, 255, 255, 0.3);
		color: white;
		transform: translateY(-1px);
	}

	.nav-button.active {
		background: rgba(72, 144, 226, 0.2);
		border-color: #4A90E2;
		color: white;
		box-shadow: 0 0 20px rgba(72, 144, 226, 0.3);
	}

	.nav-button:focus-visible {
		outline: 2px solid #4A90E2;
		outline-offset: 2px;
	}

	.nav-icon {
		font-size: 1.1rem;
		line-height: 1;
	}

	.nav-label {
		font-family: 'Inter', sans-serif;
	}

	@media (max-width: 768px) {
		.nav-container {
			padding: 10px 16px;
		}

		.nav-title {
			font-size: 1rem;
		}

		.nav-button {
			padding: 6px 12px;
			font-size: 0.8rem;
		}

		.nav-buttons {
			gap: 6px;
		}

		.nav-label {
			display: none;
		}
	}

	@media (max-width: 480px) {
		.nav-container {
			padding: 8px 12px;
		}

		.nav-button {
			padding: 6px 10px;
		}
	}
</style> 