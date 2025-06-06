<script lang="ts">
	import { run } from 'svelte/legacy';

	import * as d3 from 'd3';
	import { fade } from 'svelte/transition';
	import Loader from '../../component/ipcTree/Loader.svelte';
	import FilterMenu from '../../component/ipcTree/FilterMenu.svelte';
	import Footer from '../../component/ipcTree/Footer.svelte';
	import { searchedSymbol, zoomStore } from '$lib/stores';
	import { onMount } from 'svelte';
	// $: console.log('zoomStore', zoomStore);
	// $: console.log("searchedSymbol", searchedSymbol)

	let matchedNode;
	let ipcClassA = $state(), ipcClassB = $state(), ipcClassC = $state(), ipcClassD = $state(), ipcClassE = $state(), ipcClassF = $state(), ipcClassG = $state(), ipcClassH = $state();
	let cpcClassA = $state(), cpcClassB = $state(), cpcClassC = $state(), cpcClassD = $state(), cpcClassE = $state(), cpcClassF = $state(), cpcClassG = $state(), cpcClassH = $state();

	onMount(async () => {
		isLoading = true;
		await fetchJSONFiles();
	});

	async function fetchJSONFiles() {
		isLoading = true;

		const ipcPromises = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((cls) =>
			fetch(`/ipccpc/ipc_class_${cls.toLowerCase()}.json`).then((res) => res.json())
		);

		const cpcPromises = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map((cls) =>
			fetch(`/ipccpc/cpc_class_${cls.toLowerCase()}.json`).then((res) => res.json())
		);

		[
			ipcClassA,
			ipcClassB,
			ipcClassC,
			ipcClassD,
			ipcClassE,
			ipcClassF,
			ipcClassG,
			ipcClassH,
			cpcClassA,
			cpcClassB,
			cpcClassC,
			cpcClassD,
			cpcClassE,
			cpcClassF,
			cpcClassG,
			cpcClassH
		] = await Promise.all([...ipcPromises, ...cpcPromises]);
	}

	// const data = ipcData;
	// console.dir(data.children[7]);
	// console.log('ipcClassA', ipcClassA);
	let svg: SVGSVGElement | undefined = $state();
	let innerWidth: number | undefined = $state();
	let innerHeight: number | undefined = $state();
	let width = $state(400);
	let height = $state(400);
	let g = $state();
	let selectedSymbols = $state(new Set(['F'])); // Start by selecting only 'F'
	let shouldResetZoom = $state(false);
	let translate;
	let scale;
	let dataMode = $state('ipc'); // either 'ipc' or 'cpc'

	let isLoading = $state(true);

	// const ticks = 30;
	const symbolToTitleMapping = {
		A: 'Human necessities.',
		B: 'Performing operations; transporting.',
		C: 'Chemistry; metallurgy.',
		D: 'Textiles; paper.',
		E: 'Fixed constructions.',
		F: 'Mechanical engineering; lighting; heating; weapons; blasting.',
		G: 'Physics.',
		H: 'Electricity.'
	};

	const symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

	let MAX_DEPTH = $state(4);


	function reshapeData(ipcClassArray, depth = 1) {
		isLoading = true;
		if (depth >= MAX_DEPTH) return [];

		return ipcClassArray.map((entry) => ({
			symbol: entry.symbol,
			title: entry.title || symbolToTitleMapping[entry.symbol] || 'Unknown',
			children: entry.children ? reshapeData(entry.children, depth + 1) : []
		}));
	}

	let data = $state({
		title: 'IPC Section Start',
		symbol: 'Node Zero',
		children: []
	});

	// $: console.log('data', data);

	function toggleSymbol(symbol) {
		console.log('toggleSymbol', symbol);
		isLoading = true;
		console.log('toggleSymbol', symbol);

		const existingChild = data.children.find((child) => child.symbol === symbol);

		if (existingChild) {
			// If the symbol is already selected, remove it from the children of data
			data = {
				...data,
				children: data.children.filter((child) => child.symbol !== symbol)
			};
			selectedSymbols.delete(symbol);
			selectedSymbols = selectedSymbols;
		} else {
			// If the symbol is not yet selected, add it to the children of data
			let newChild = {
				symbol: symbol,
				title: 'Some Default Title', // Update this accordingly
				children: reshapeData(symbolDataMap[symbol].children)
			};

			data = {
				...data,
				children: [...data.children, newChild]
			};

			selectedSymbols.add(symbol);
			selectedSymbols = selectedSymbols;
			$zoomStore = 'reset';
		}
	}

	const uniqueSymbols = Object.values(data.children).map((d) => d.symbol);

	const vibrantColors = [
		'#e6194b', // red
		'#3cb44b', // green
		'#0082c8', // blue
		'#f58231', // orange
		'#f032e6', // magenta
		'#46f0f0', // cyan
		'#d2f53c', // lime
		'#ff69b4', // hot pink
		'#ffa500', // bright orange
		'#20d9d9', // bright turquoise
		'#f5d142', // bright yellow
		'#e6beff', // lavender (soft but still visible)
		'#aaffc3', // mint (soft but still visible)
		'#ffd8b1' // coral (soft but still visible)
	];

	function getTreeBounds(nodes) {
		let xMin = Infinity;
		let xMax = -Infinity;
		let yMin = Infinity;
		let yMax = -Infinity;

		nodes.forEach((d) => {
			if (d.x < xMin) xMin = d.x;
			if (d.x > xMax) xMax = d.x;
			if (d.y < yMin) yMin = d.y;
			if (d.y > yMax) yMax = d.y;
		});

		return { xMin, xMax, yMin, yMax };
	}
	let buttonSymbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
	const colorScale = d3.scaleOrdinal().domain(symbols).range(vibrantColors); // or any other color scheme

	// $: console.log('Reactive Statement:', svg, g);

	function handleSearch(event) {
		const searchTerm = event.detail;
		searchAndHighlight(searchTerm);
	}
	// $: console.log('isLoading', isLoading);
	// $: console.log('shouldResetZoom', shouldResetZoom);
	// Reactive statement to auto-update when `width` changes.

	run(() => {
		if (innerWidth && innerHeight) {
			width = innerWidth;
			height = innerHeight;
			// console.log('width', width);
			// console.log('height', height);
		}
	});
	let symbolDataMap =
		$derived(dataMode === 'ipc'
			? {
					A: ipcClassA,
					B: ipcClassB,
					C: ipcClassC,
					D: ipcClassD,
					E: ipcClassE,
					F: ipcClassF,
					G: ipcClassG,
					H: ipcClassH
			  }
			: {
					A: cpcClassA,
					B: cpcClassB,
					C: cpcClassC,
					D: cpcClassD,
					E: cpcClassE,
					F: cpcClassF,
					G: cpcClassG,
					H: cpcClassH
			  });
	run(() => {
		isLoading = true;
		setTimeout(() => {
			console.log('MAX_DEPTH', MAX_DEPTH);
			if (ipcClassF) {
				data.children = Array.from(selectedSymbols).map((symbol) => ({
					symbol: symbol,
					title: symbolToTitleMapping[symbol] || 'Unknown',
					children: reshapeData(symbolDataMap[symbol].children || ipcClassF)
				}));
			}
		}, 300); // 500 ms or 0.5 second delay
	});
	run(() => {
		console.log('datamodel', dataMode);
	});
	///////////////////////////////////////////////////////////////////////////////////
	run(() => {
		if (data.children.length > 0 && svg !== null) {
			const svgSelection = d3.select(svg);
			svgSelection.selectAll('*').remove();

			let g = svgSelection.append('g').attr('class', 'main-group');

			function zoomed(event) {
				const { transform } = event;
				g.attr('transform', `translate(${transform.x},${transform.y}) scale(${transform.k})`);
			}

			const zoom = d3.zoom().scaleExtent([0.02, 50]).on('zoom', zoomed);

			svgSelection.call(zoom);

			const radius = Math.min(width, height);
			const root = d3.hierarchy(data);
			root.eachBefore((node) => {
				if (node.depth === 0) {
					node.data.masterColor = '#fff'; // root color
				} else {
					node.data.masterColor =
						node.parent.data.masterColor || colorScale(node.parent.data.symbol);
				}
			});

			const treeLayout = d3.tree().size([2 * Math.PI, radius]);
			const yMultiplier = 9; // Increase this for more space between nodes
			root.each((d) => {
				d.y = d.depth * yMultiplier;
			});
			treeLayout(root);

			const linkGenerator = d3
				.linkRadial()
				.angle((d) => d.x)
				.radius((d) => d.y);

			g.selectAll('.link')
				.data(root.links())
				.enter()
				.append('path')
				.attr('class', 'link')
				.attr('d', linkGenerator)
				.attr('stroke', function (d) {
					return d.source ? d.source.data.masterColor : '#fff';
				})

				.attr('stroke-width', 0.5)
				.attr('transform', `translate(${width / 2}, ${height / 2})`);
			console.log(data);

			// For nodes
			g.selectAll('.node')
				.data(root.descendants())
				.enter()
				.append('circle')
				.attr('class', 'node')

				.attr('fill', (d) => {
					if (d.data && d.data.id) {
						return colorScale(d.data.id);
					}
					return '#fff'; // Replace 'defaultColor' with an actual color
				})
				.attr('transform', `translate(${width / 2}, ${height / 2})`)
				.attr('r', 5);
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>IPC Tree Explorer</title>
	<meta name="og:title" content="IPC Tree Explorer" />
	<meta name="og:description" content="Explore the IPC Tree" />
	<meta name="og:image" content="https://ipc.patscenar.io/og_image.png" />
	<!-- Chrome, Firefox OS and Opera -->
	<meta name="theme-color" content="#000000" />
	<!-- Windows Phone -->
	<meta name="msapplication-navbutton-color" content="#000000" />
	<!-- iOS Safari -->
	<meta name="apple-mobile-web-app-status-bar-style" content="#000000" />
</svelte:head>

<!-- isLoading Div -->
{#if isLoading === true}
	<Loader {isLoading} />
{/if}
<!-- Add Filtering Controls -->
<!-- Add Filtering Controls -->

<div
	in:fade={{ duration: 500 }}
	class="chart-container"
	bind:clientWidth={innerWidth}
	bind:clientHeight={innerHeight}
>
	{#if innerWidth && innerHeight}
		<svg
			transition:fade={{ duration: 500, delay: 200 }}
			bind:this={svg}
			width="100%"
			height="100%"
			viewBox={`0 0 ${width} ${height}`}
		>
			<g class="main-group" bind:this={g}>
				<defs>
					<filter id="whiteOutline" x="-20%" y="-20%" width="240%" height="140%">
						<feMorphology in="SourceAlpha" result="expanded" operator="dilate" radius="8" />
						<feFlood flood-color="white" result="color" />
						<feComposite in="color" in2="expanded" operator="in" />
						<feComposite in="SourceGraphic" />
					</filter>
				</defs>
				<!-- rest of the visualization elements (circles, lines, etc.) -->
			</g>
		</svg>
	{/if}
	<!-- Filters -->
	<FilterMenu
		{selectedSymbols}
		{data}
		{toggleSymbol}
		bind:shouldResetZoom
		{buttonSymbols}
		bind:MAX_DEPTH
		on:search={handleSearch}
		bind:dataMode
	/>
	<Footer {data} />
</div>

<style>
	:global(body) {
		background-color: #000;
		overflow: hidden;
	}

	.chart-container {
		width: 100vw;
		height: 100dvh;
		min-height: -webkit-fill-available;
		background-color: #000;
		display: block;
		overflow: hidden;
		box-sizing: border-box;
		position: relative;
	}
	svg {
		width: 100%;
		height: 100%;
	}

	/* .loading-blur {
		backdrop-filter: blur(5px);
	} */

	:global(.tooltip) {
		position: absolute;
		text-align: left;
		padding: 8px;
		background: #ffffff;
		border: 1px solid #ccc;
		border-radius: 4px;
		pointer-events: none;
		opacity: 0; /* starts out hidden */
		transition: opacity 0.3s;
		z-index: 100000;
		max-width: 300px;
		word-wrap: break-word;
		white-space: normal;
		font-size: 0.8em;
	}
	@media (max-width: 600px) {
		:global(.tooltip) {
			position: absolute;
			text-align: left;
			padding: 4px;
			background: #ffffff;
			border: 1px solid #ccc;
			border-radius: 2px;
			pointer-events: none;
			opacity: 0; /* starts out hidden */
			transition: opacity 0.3s;
			z-index: 100000;
			max-width: 200px;
			word-wrap: break-word;
			white-space: normal;
			font-size: 0.6em;
		}
	}

	:global(.tooltipsymbol) {
		background-color: #d7d565;
		font-style: italic;
	}

	:global(body:after) {
		content: 'beta';
		position: fixed;
		width: 80px;
		height: 25px;
		background: #890c58;
		bottom: 7px;
		left: -20px;
		text-align: center;
		font-size: 13px;
		font-family: sans-serif;
		text-transform: uppercase;
		font-weight: bold;
		color: #fff;
		line-height: 27px;
		transform: rotate(45deg);
	}
	:global(.tooltip ul) {
		list-style-type: none; /* Remove default bullet points */
		padding-left: 1em; /* Add some spacing to the left to make room for custom bullet */
	}

	:global(.tooltip ul li::before) {
		content: '→'; /* Use an arrow as the bullet point */
		margin-right: 10px; /* Add a space after the arrow */
	}
</style>
