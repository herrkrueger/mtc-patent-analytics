<script>
	import "../app.css";
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { onCLS, onFCP, onINP, onLCP, onTTFB } from 'web-vitals';

	/**
	 * @typedef {Object} Props
	 * @property {import('./$types').LayoutServerData} data
	 * @property {import('svelte').Snippet} [children]
	 */

	/** @type {Props} */
	let { data, children } = $props();

	$effect(() => {
		if (browser && data?.analyticsId) {
			// Initialize web vitals
			onCLS(console.log);
			onFCP(console.log);
			onINP(console.log);
			onLCP(console.log);
			onTTFB(console.log);
		}
	});
</script>
	
<div class="app">
	

	<main>
		{@render children?.()}
	</main>

	<footer>
		
	</footer>
</div>

<style>
	
</style>
