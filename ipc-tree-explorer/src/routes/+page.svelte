<script lang="ts">
	import * as d3 from 'd3';
	import { fade } from 'svelte/transition';
	import Loader from '../component/ipcTree/Loader.svelte';
	import FilterMenu from '../component/ipcTree/FilterMenu.svelte';
	import Footer from '../component/ipcTree/Footer.svelte';
	import Navigation from '../component/ipcTree/Navigation.svelte';
	import { searchedSymbol, zoomStore } from '$lib/stores';
	import { onMount } from 'svelte';

	// Type definitions for better TypeScript support
	interface IPCNode {
		symbol: string;
		title: string | { _text?: string; $text?: string; [key: string]: any };
		children?: IPCNode[];
	}

	interface DataStructure {
		title: string;
		symbol: string;
		children: IPCNode[];
	}

	type D3Node = {
		x: number;
		y: number;
		depth: number;
		id: string;
		data: IPCNode;
		parent?: D3Node;
		children?: D3Node[];
		ancestors: () => D3Node[];
	};

	interface D3Link {
		source: D3Node;
		target: D3Node;
	}

	// State variables with proper typing
	let matchedNode: D3Node | undefined;
	let ipcClassA: IPCNode | null = $state(null);
	let ipcClassB: IPCNode | null = $state(null);
	let ipcClassC: IPCNode | null = $state(null);
	let ipcClassD: IPCNode | null = $state(null);
	let ipcClassE: IPCNode | null = $state(null);
	let ipcClassF: IPCNode | null = $state(null);
	let ipcClassG: IPCNode | null = $state(null);
	let ipcClassH: IPCNode | null = $state(null);

	let cpcClassA: IPCNode | null = $state(null);
	let cpcClassB: IPCNode | null = $state(null);
	let cpcClassC: IPCNode | null = $state(null);
	let cpcClassD: IPCNode | null = $state(null);
	let cpcClassE: IPCNode | null = $state(null);
	let cpcClassF: IPCNode | null = $state(null);
	let cpcClassG: IPCNode | null = $state(null);
	let cpcClassH: IPCNode | null = $state(null);

	let svg: SVGSVGElement | undefined = $state();
	let innerWidth: number | undefined = $state();
	let innerHeight: number | undefined = $state();
	let width = $state(400);
	let height = $state(400);
	let g: SVGGElement | undefined = $state();
	let selectedSymbols = $state(new Set(['F']));
	let shouldResetZoom = $state(false);
	let translate: [number, number] | undefined;
	let scale: number | undefined;
	let dataMode: 'ipc' | 'cpc' = $state('ipc');
	let isLoading = $state(true);

	// Performance: Memoized data fetching
	let dataCache = new Map<string, IPCNode>();

	// Add after the existing state variables:
	let currentZoomLevel = 1;
	let renderDebounceTimer: ReturnType<typeof setTimeout> | null = null;

	// Add to module-level state variables (after other let declarations):
	let hasInitializedZoom = false;

	// Performance: Optimized memoization with WeakMap for better memory management
	let reshapeDataMemo = $state(new WeakMap<IPCNode[], IPCNode[]>());
	let memoKeyCache = new Map<string, IPCNode[]>();
	let debounceTimer: ReturnType<typeof setTimeout> | null = null;

	// Performance: Virtual rendering for large datasets
	let visibleNodeCache = new Map<string, boolean>();
	let lastRenderNodeCount = 0;

	// Performance: Replace expensive reactive statement with optimized version
	let lastDataSignature = $state('');
	let lastRenderTime = $state(0);
	const MIN_RENDER_INTERVAL = 100; // Minimum time between renders

	function getDataSignature(): string {
		return `${data.children.length}_${selectedSymbols.size}_${MAX_DEPTH}_${dataMode}_${innerWidth}_${innerHeight}`;
	}

	onMount(async () => {
		isLoading = true;
		await fetchJSONFiles();
		
		// Initialize with default F section after data is loaded
		if (selectedSymbols.has('F') && data.children.length === 0) {
			toggleSymbol('F');
		}
		
		isLoading = false;
	});

	async function fetchJSONFiles(): Promise<void> {
		isLoading = true;

		try {
			// Performance: Use Promise.allSettled for better error handling
			const ipcPromises = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map(async (cls) => {
				const cacheKey = `ipc_${cls}`;
				if (dataCache.has(cacheKey)) {
					return dataCache.get(cacheKey)!;
				}
				const response = await fetch(`/ipccpc/ipc_class_${cls.toLowerCase()}.json`);
				if (!response.ok) throw new Error(`Failed to fetch ${cls}: ${response.status}`);
				const data = await response.json();
				dataCache.set(cacheKey, data);
				return data;
			});

			const cpcPromises = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map(async (cls) => {
				const cacheKey = `cpc_${cls}`;
				if (dataCache.has(cacheKey)) {
					return dataCache.get(cacheKey)!;
				}
				const response = await fetch(`/ipccpc/cpc_class_${cls.toLowerCase()}.json`);
				if (!response.ok) throw new Error(`Failed to fetch ${cls}: ${response.status}`);
				const data = await response.json();
				dataCache.set(cacheKey, data);
				return data;
			});

		const results = await Promise.allSettled([...ipcPromises, ...cpcPromises]);
		
		// Handle both successful and failed requests
		const successfulResults = results
			.filter((result): result is PromiseFulfilledResult<IPCNode> => result.status === 'fulfilled')
			.map(result => result.value);

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
		] = successfulResults;
		} catch (error) {
			console.error('Error fetching JSON files:', error);
		}
	}


	const symbolToTitleMapping: Record<string, string> = {
		A: 'Human necessities.',
		B: 'Performing operations; transporting.',
		C: 'Chemistry; metallurgy.',
		D: 'Textiles; paper.',
		E: 'Fixed constructions.',
		F: 'Mechanical engineering; lighting; heating; weapons; blasting.',
		G: 'Physics.',
		H: 'Electricity.'
	};

	const symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] as const;
	

	let MAX_DEPTH = $state(4);



	// Performance: Highly optimized reshapeData with better memoization
	function reshapeData(ipcClassArray: IPCNode[], depth = 1): IPCNode[] {
		// Use array reference as WeakMap key for better performance
		if (reshapeDataMemo.has(ipcClassArray)) {
			return reshapeDataMemo.get(ipcClassArray)!;
		}

		// Fallback to string-based cache for complex scenarios
		const memoKey = `${depth}_${MAX_DEPTH}_${ipcClassArray.length}`;
		if (memoKeyCache.has(memoKey)) {
			return memoKeyCache.get(memoKey)!;
		}

		if (depth >= MAX_DEPTH) return [];

		const result = ipcClassArray.map((entry) => ({
			symbol: entry.symbol,
			title: entry.title || symbolToTitleMapping[entry.symbol] || 'Unknown',
			children: entry.children ? reshapeData(entry.children, depth + 1) : []
		}));

		// Store in both caches
		reshapeDataMemo.set(ipcClassArray, result);
		memoKeyCache.set(memoKey, result);
		
		// Performance: Limit cache size to prevent memory leaks
		if (memoKeyCache.size > 100) {
			const firstKey = memoKeyCache.keys().next().value;
			if (firstKey !== undefined) {
				memoKeyCache.delete(firstKey);
			}
		}

		return result;
	}

	// Handle zoom store subscription
	$effect(() => {
		if ($zoomStore === 'reset') {
			shouldResetZoom = true;
			$zoomStore = '';
		}
	});
	
	// Auto-update when dimensions change
	$effect(() => {
		if (innerWidth && innerHeight) {
			width = innerWidth;
			height = innerHeight;
		}
	});
	
	let symbolDataMap = $derived(dataMode === 'ipc'
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

	// Use derived state for data instead of mutating it in effects
	let data = $derived({
		title: 'IPC Section Start',
		symbol: 'Node Zero',
		children: Array.from(selectedSymbols).map((symbol) => {
			const symbolData = symbolDataMap[symbol as keyof typeof symbolDataMap];
			return {
				symbol: symbol,
				title: symbolToTitleMapping[symbol] || 'Unknown',
				children: reshapeData(symbolData?.children || [])
			};
		})
	});

	// Simple effect for cache clearing when MAX_DEPTH changes  
	$effect(() => {
		if (typeof window !== 'undefined' && MAX_DEPTH) {
			console.log('MAX_DEPTH changed to:', MAX_DEPTH);
			// Clear memoization caches since they contain depth-dependent results
			reshapeDataMemo = new WeakMap<IPCNode[], IPCNode[]>();
			memoKeyCache.clear();
			visibleNodeCache.clear();
		}
	});
			  
	// Separate effect only for rendering, triggered by data changes
	$effect(() => {
		if (typeof window !== 'undefined' && data.children.length > 0 && svg !== null && innerWidth && innerHeight) {
			const currentSignature = getDataSignature();
			const now = Date.now();
			
			// Only render if data actually changed and enough time has passed
			if (currentSignature !== lastDataSignature && (now - lastRenderTime) > MIN_RENDER_INTERVAL) {
				lastDataSignature = currentSignature;
				lastRenderTime = now;
				
				console.log('Render triggered');
				
				// Use requestAnimationFrame for rendering
				requestAnimationFrame(() => renderVisualization());
			}
		}
	});

	function toggleSymbol(symbol: string): void {
		console.log('toggleSymbol', symbol);
		isLoading = true;

		if (selectedSymbols.has(symbol)) {
			// Remove symbol
			selectedSymbols.delete(symbol);
			selectedSymbols = new Set(selectedSymbols);
		} else {
			// Add symbol
			selectedSymbols.add(symbol);
			selectedSymbols = new Set(selectedSymbols);
			$zoomStore = 'reset';
		}
		
		// Allow the DOM to update, then set loading to false
		setTimeout(() => {
			isLoading = false;
		}, 100);
	}

	const uniqueSymbols = Object.values(data.children).map((d) => d.symbol);

	// Performance: More efficient color generation
	const vibrantColors = [
		'#e6194b', '#3cb44b', '#0082c8', '#f58231', '#f032e6', '#46f0f0', 
		'#d2f53c', '#ff69b4', '#ffa500', '#20d9d9', '#f5d142', '#e6beff', 
		'#aaffc3', '#ffd8b1'
	];

	const colorScale = d3.scaleOrdinal<string>().domain(symbols).range(vibrantColors);

	function getTreeBounds(nodes: D3Node[]): { xMin: number; xMax: number; yMin: number; yMax: number } {
		let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;

		nodes.forEach((d) => {
			if (d.x < xMin) xMin = d.x;
			if (d.x > xMax) xMax = d.x;
			if (d.y < yMin) yMin = d.y;
			if (d.y > yMax) yMax = d.y;
		});

		return { xMin, xMax, yMin, yMax };
	}

	let buttonSymbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

	function handleSearch(event: CustomEvent<string>): void {
		const searchTerm = event.detail;
		searchAndHighlight(searchTerm);
	}

	function searchAndHighlight(searchTerm: string): void {
		// Implementation for search functionality
		console.log('Searching for:', searchTerm);
		if (searchTerm) {
			$searchedSymbol = searchTerm.toUpperCase();
		}
	}


	// Performance: Optimized node visibility check with caching
	function shouldShowNode(node: any, zoomLevel: number): boolean {
		const nodeId = node.data?.id || `fallback_${node.depth}_${node.data?.symbol || 'unknown'}`;
		const nodeKey = `${nodeId}_${zoomLevel.toFixed(2)}_${MAX_DEPTH}`;
		
		if (visibleNodeCache.has(nodeKey)) {
			return visibleNodeCache.get(nodeKey)!;
		}
		
		// Simply use MAX_DEPTH without any hardcoded limits
		let isVisible = node.depth <= MAX_DEPTH;
		
		// Note: Removed the problematic performance optimization that was inconsistently 
		// hiding nodes based on zoom level and node count, causing MAX_DEPTH 6 to show 
		// fewer nodes than MAX_DEPTH 5
		
		visibleNodeCache.set(nodeKey, isVisible);
		
		// Performance: Limit cache size
		if (visibleNodeCache.size > 1000) {
			const firstKey = visibleNodeCache.keys().next().value;
			if (firstKey !== undefined) {
				visibleNodeCache.delete(firstKey);
			}
		}
		
		return isVisible;
	}

	function renderVisualization(): void {
		// Only run rendering in browser environment
		if (typeof window === 'undefined') return;
		
		// Clear any pending render
		if (renderDebounceTimer) {
			clearTimeout(renderDebounceTimer);
		}
		
		renderDebounceTimer = setTimeout(() => {
			performRender();
		}, 50);
	}

	// Performance: Optimized render function with progressive rendering
	function performRender(): void {
		// Only run rendering in browser environment
		if (typeof window === 'undefined') return;
		
		const svgSelection = d3.select(svg);
		const startTime = typeof performance !== 'undefined' ? performance.now() : Date.now();

		// Performance: Clear only what's necessary instead of everything
		svgSelection.selectAll('.main-group > *').remove();
		
		// Set up click handler for background
		svgSelection.on('click', () => {
			resetOpacity();
		});

		// Create hierarchy
		const root = d3.hierarchy(data);
		
		// Improved radial tree layout for better outer circle distribution
		const radius = Math.min(innerWidth, innerHeight) / 2 - 100;
		const tree = d3.tree<IPCNode>()
			.size([2 * Math.PI, radius])
			.separation((a: any, b: any) => {
				// Better separation for outer nodes
				if (a.parent === b.parent) {
					// More space between siblings at deeper levels
					return Math.max(0.8, 1.0 / Math.max(1, a.depth - 1));
				}
				// More space between different branches
				return Math.max(1.5, 2.0 / Math.max(1, a.depth - 1));
			});
		
		tree(root);
		
		// Convert to radial coordinates with better distribution
		root.each((d: any) => {
			const angle = d.x;
			// Spread outer nodes more by using a non-linear radius scaling
			let r = d.y;
			if (d.depth > 2) {
				// Exponential scaling for deeper levels to spread them out more
				const depthFactor = Math.pow(1.4, d.depth - 2);
				r = d.y * depthFactor;
			}
			
			d.x = r * Math.cos(angle - Math.PI / 2);
			d.y = r * Math.sin(angle - Math.PI / 2);
			
			// Simple stable ID with proper fallback
			if (!d.data.id) {
				d.data.id = `${d.data.symbol || 'unknown'}_${d.depth}_${d.parent?.data?.symbol || 'root'}`;
			}
		});
		
		const allNodes = root.descendants() as D3Node[];
		const allLinks = root.links();
		lastRenderNodeCount = allNodes.length;
		
		// Clear visibility cache when node count changes significantly
		if (Math.abs(lastRenderNodeCount - (visibleNodeCache.size / 10)) > 1000) {
			visibleNodeCache.clear();
		}
		
		// Performance: Progressive rendering for large datasets
		const BATCH_SIZE = 500; // Render nodes in batches
		const isLargeDataset = allNodes.length > 2000;
		
		// Filter visible nodes and links based on zoom and collapse state
		const visibleNodes = allNodes.filter(node => shouldShowNode(node, currentZoomLevel));
		const visibleLinks = allLinks.filter((link: any) => 
			shouldShowNode(link.source, currentZoomLevel) && 
			shouldShowNode(link.target, currentZoomLevel)
		);
		
		console.log(`Rendering ${visibleNodes.length}/${allNodes.length} nodes, ${visibleLinks.length} links`);
		
		// Create main group centered
		const mainGroup = svgSelection.select('.main-group').empty() 
			? svgSelection.append('g').attr('class', 'main-group')
			: svgSelection.select('.main-group');
		
		mainGroup.attr('transform', `translate(${innerWidth / 2}, ${innerHeight / 2})`);
		
		// Performance: Progressive rendering function
		function renderBatch(items: any[], startIndex: number, renderFn: (item: any) => void) {
			if (!isLargeDataset) {
				// Render all at once for small datasets
				items.forEach(renderFn);
				return;
			}
			
			const endIndex = Math.min(startIndex + BATCH_SIZE, items.length);
			for (let i = startIndex; i < endIndex; i++) {
				renderFn(items[i]);
			}
			
			if (endIndex < items.length) {
				// Use requestIdleCallback if available, otherwise requestAnimationFrame (browser only)
				if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
					requestIdleCallback(() => renderBatch(items, endIndex, renderFn));
				} else if (typeof window !== 'undefined') {
					requestAnimationFrame(() => renderBatch(items, endIndex, renderFn));
				}
			}
		}
		
		// Helper function to determine the root section symbol for any node
		function getRootSectionSymbol(node: any): string {
			// Walk up the tree to find the root section (depth 1)
			let current = node;
			while (current && current.depth > 1 && current.parent) {
				current = current.parent;
			}
			// If we're at depth 1, this is the root section
			if (current && current.depth === 1) {
				return current.data.symbol[0]; // Get the first character (A, B, C, etc.)
			}
			// If we're at depth 0 (root), return a default
			if (current && current.depth === 0) {
				return 'ROOT';
			}
			// Fallback - extract from symbol
			return node.data?.symbol?.[0] || 'A';
		}
		
		// Draw links with progressive rendering
		const linksGroup = mainGroup.append('g').attr('class', 'links');
		
		function renderLink(d: any) {
			linksGroup.append('path')
				.datum(d)
				.attr('d', () => {
					const source = { x: d.source.x, y: d.source.y };
					const target = { x: d.target.x, y: d.target.y };
					
					// Simple curved path
					const dx = target.x - source.x;
					const dy = target.y - source.y;
					const dr = Math.sqrt(dx * dx + dy * dy) * 0.8;
					
					return `M${source.x},${source.y}A${dr},${dr} 0 0,1 ${target.x},${target.y}`;
				})
				.attr('fill', 'none')
				.attr('stroke', () => {
					if (d.source.depth === 0) return '#ffe082';
					// Use consistent color based on root section
					const rootSymbol = getRootSectionSymbol(d.source);
					const baseColor = colorScale(rootSymbol);
					return d3.color(baseColor)?.darker(0.3).toString() || '#666';
				})
				.attr('stroke-width', () => {
					if (d.source.depth === 0) return 3;
					if (d.source.depth === 1) return 2;
					return Math.max(0.5, 2 - d.source.depth * 0.3);
				})
				.attr('opacity', () => Math.max(0.4, 0.8 - d.source.depth * 0.1));
		}
		
		renderBatch(visibleLinks, 0, renderLink);
		
		// Create tooltip with proper styling - reuse existing if possible
		const tooltip = d3.select('body')
			.selectAll('.tree-tooltip')
			.data([null])
			.join('div')
			.attr('class', 'tree-tooltip')
			.style('position', 'absolute')
			.style('background', '#23233aee')
			.style('border', '1.5px solid #ffe082')
			.style('color', '#ffe082')
			.style('font-family', "'EB Garamond', 'Georgia', serif")
			.style('font-size', '14px')
			.style('padding', '8px 12px')
			.style('border-radius', '6px')
			.style('box-shadow', '0 4px 12px rgba(0,0,0,0.3)')
			.style('pointer-events', 'none')
			.style('z-index', '1000')
			.style('max-width', '300px')
			.style('opacity', 0);
		
		// Draw nodes with progressive rendering
		const nodeGroup = mainGroup.append('g').attr('class', 'nodes');
		
		function renderNode(d: any) {
			const nodeId = d.data?.id || `fallback_${d.depth}_${d.data?.symbol || 'unknown'}`;
			
			const nodeSelection = nodeGroup.append('g')
				.datum(d)
				.attr('class', 'node-group')
				.attr('transform', `translate(${d.x},${d.y})`)
				.attr('id', nodeId)
				.attr('tabindex', '0')
				.attr('role', 'button')
				.attr('aria-label', `Node ${d.data.symbol}: ${extractTitle(d.data.title)}`)
				.style('cursor', 'pointer');
		
			// Add node circles with size based on depth and zoom
			nodeSelection.append('circle')
				.attr('class', 'node-circle')
				.attr('r', () => {
					if (d.depth === 0) return 8;
					if (d.depth === 1) return 12;
					if (d.depth === 2) return 8;
					// Smaller nodes for deeper levels to reduce clutter
					return Math.max(3, 8 - d.depth);
				})
				.attr('fill', () => {
					if (d.depth === 0) return '#ffe082';
					// Use consistent color based on root section for all depths
					const rootSymbol = getRootSectionSymbol(d);
					const baseColor = colorScale(rootSymbol);
					
					// Only slightly adjust opacity/brightness based on depth for subtle distinction
					if (d.depth === 1) {
						return baseColor; // Main section - full color
					} else if (d.depth === 2) {
						// Slightly lighter for subsections
						return d3.color(baseColor)?.brighter(0.2).toString() || baseColor;
					} else {
						// Very slightly lighter for deeper levels
						return d3.color(baseColor)?.brighter(0.4).toString() || baseColor;
					}
				})
				.attr('stroke', '#fff')
				.attr('stroke-width', () => Math.max(1, 3 - d.depth * 0.3));
		
			// Add node labels with better visibility for outer nodes
			nodeSelection.append('text')
				.attr('class', 'node-label')
				.attr('text-anchor', 'middle')
				.attr('dy', '0.3em')
				.attr('font-size', () => {
					if (d.depth === 0) return '10px';
					if (d.depth === 1) return '12px';
					if (d.depth === 2) return '9px';
					// Smaller text for deeper levels
					return Math.max(6, 10 - d.depth) + 'px';
				})
				.attr('font-weight', () => d.depth <= 1 ? 'bold' : 'normal')
				.attr('fill', () => d.depth <= 1 ? '#000' : '#fff')
				.style('paint-order', 'stroke fill')
				.style('stroke', '#181824')
				.style('stroke-width', '2px')
				.style('stroke-linejoin', 'round')
				.text(() => {
					if (d.depth === 0) return '';
					if (d.depth === 1) return d.data.symbol;
					// NO TEXT FOR OUTER CIRCLES - only show labels for depth 1 and 2
					if (d.depth === 2) {
						return d.data.symbol.length <= 6 ? d.data.symbol : d.data.symbol.substr(0, 4) + '..';
					}
					// No text for depth 3 and beyond
					return '';
				});
		
			// Add interaction handlers with performance optimizations
			nodeSelection
				.on('click', (event: MouseEvent) => {
					event.stopPropagation();
					highlightPath(d);
				})
				.on('mouseover', (event: MouseEvent) => {
					showTooltip(event, d, tooltip);
				})
				.on('mouseout', () => {
					hideTooltip(tooltip);
				});
		}
		
		// Progressive node rendering
		renderBatch(visibleNodes, 0, renderNode);
		
		// Helper functions
		function extractTitle(title: string | any): string {
			if (typeof title === 'string') return title;
			if (Array.isArray(title)) {
				// Handle nested arrays like [["STEAM ENGINES"]] or [["text"]]
				if (title.length > 0 && Array.isArray(title[0]) && title[0].length > 0) {
					return title[0][0];
				}
				// Handle simple array like ["text"]
				if (title.length > 0) {
					return title[0];
				}
			}
			if (typeof title === 'object') {
				if (title?._text) return title._text;
				if (title?.$text) return title.$text;
			}
			return 'Unknown Title';
		}
		
		function highlightPath(d: any): void {
			nodeGroup.selectAll('.node-group').attr('opacity', 0.3);
			linksGroup.selectAll('path').attr('opacity', 0.2);
			
			const ancestors = d.ancestors();
			ancestors.forEach((ancestor: any) => {
				const nodeId = ancestor.data?.id || `fallback_${ancestor.depth}_${ancestor.data?.symbol || 'unknown'}`;
				// Use proper selector escaping for IDs with special characters
				const escapedId = nodeId.replace(/[^\w-]/g, '\\$&');
				nodeGroup.select(`#${escapedId}`).attr('opacity', 1);
			});
			
			linksGroup.selectAll('path')
				.filter((l: any) => ancestors.indexOf(l.target) !== -1)
					.attr('opacity', 1);
		}

		function resetOpacity(): void {
			nodeGroup.selectAll('.node-group').attr('opacity', 1);
			linksGroup.selectAll('path').attr('opacity', (d: any) => Math.max(0.3, 0.8 - d.source.depth * 0.1));
		}
		
		function showTooltip(event: MouseEvent, d: any, tooltip: any): void {
			const titleText = extractTitle(d.data.title);
			const childCount = d.children ? d.children.length : 0;
			
			tooltip.style('opacity', 1)
				.html(`
					<div>
						<strong>${d.data.symbol}</strong><br/>
						<div style="font-size: 12px; margin-top: 4px; line-height: 1.3;">
							${titleText}
						</div>
						${childCount > 0 ? `<div style="font-size: 11px; margin-top: 4px; color: #bfae7c;">Children: ${childCount}</div>` : ''}
						<div style="font-size: 10px; margin-top: 4px; color: #888;">
							Depth: ${d.depth} | Click to highlight path
						</div>
					</div>
				`)
				.style('left', `${event.pageX + 15}px`)
				.style('top', `${event.pageY + 10}px`);
		}
		
		function hideTooltip(tooltip: any): void {
			tooltip.style('opacity', 0);
		}
		
		// Calculate DYNAMIC automatic zoom based on tree dimensions and density
		const totalNodes = allNodes.length;
		
		// Calculate the actual tree bounds
		const treeBounds = getTreeBounds(allNodes);
		const treeWidth = treeBounds.xMax - treeBounds.xMin;
		const treeHeight = treeBounds.yMax - treeBounds.yMin;
		
		// Calculate viewport dimensions
		const viewportWidth = innerWidth - 200; // Account for UI margins
		const viewportHeight = innerHeight - 200;
		
		// Start with viewport fitting zoom as baseline
		let baseZoom = Math.min(
			viewportWidth / (treeWidth + 100),
			viewportHeight / (treeHeight + 100)
		);
		
		// ZOOM IN MORE when there are many nodes for better readability!
		let autoZoom = baseZoom; // Start with natural viewport fit
		
		const maxDepth = Math.max(...allNodes.map(n => n.depth));
		const nodesAtOuterDepth = allNodes.filter(n => n.depth === maxDepth).length;
		
		// Only boost zoom for TRULY massive overlap situations
		if (nodesAtOuterDepth > 10000) {
			autoZoom = Math.max(baseZoom, 2.5); // Extreme overlap - many sections at max depth
		} else if (nodesAtOuterDepth > 6000) {
			autoZoom = Math.max(baseZoom, 2.0); // Very high overlap - most sections loaded
		}
		// For anything less than 6000 outer nodes, use natural viewport fit
		
		// No zoom boost based on section count - let natural fit handle it
		const mainSections = allNodes.filter(n => n.depth === 1).length;
		
		// Only boost for extremely high total node counts
		if (totalNodes > 15000) {
			autoZoom = Math.max(autoZoom, 2.0);
		}
		
		// Ensure zoom stays within reasonable bounds
		autoZoom = Math.max(0.3, Math.min(3.0, autoZoom));
		
		// Simple zoom stepping
		if (autoZoom >= 2.3) autoZoom = 2.5;
		else if (autoZoom >= 1.8) autoZoom = 2.0;
		else if (autoZoom >= 1.3) autoZoom = 1.5;
		else if (autoZoom >= 0.9) autoZoom = 1.0;
		else if (autoZoom >= 0.7) autoZoom = 0.8;
		else if (autoZoom >= 0.5) autoZoom = 0.6;
		else autoZoom = 0.4;
		
		console.log(`Dynamic Zoom Calculation (NATURAL FIT PRIORITY):
			Total Nodes: ${totalNodes}
			Tree Dimensions: ${treeWidth.toFixed(0)} x ${treeHeight.toFixed(0)}
			Viewport: ${viewportWidth} x ${viewportHeight}
			Max Depth: ${maxDepth}
			Nodes at outer depth: ${nodesAtOuterDepth} ${nodesAtOuterDepth > 10000 ? '🔴 EXTREME OVERLAP!' : nodesAtOuterDepth > 6000 ? '🟡 High Density' : '🟢 Normal/Medium'}
			Main Sections: ${mainSections}
			Base Viewport Fit: ${baseZoom.toFixed(3)}
			FINAL ZOOM: ${autoZoom}x ${autoZoom > baseZoom ? '🔍 BOOSTED for extreme density' : '👁️ NATURAL VIEWPORT FIT'}
			Logic: Natural fit for normal trees, boost only for extreme overlap (6000+ outer nodes)
		`);
		
		// Set up zoom
		const zoom = d3.zoom<SVGSVGElement, unknown>()
			.scaleExtent([0.05, 10])
			.on('zoom', (event: any) => {
				const transform = event.transform;
				currentZoomLevel = transform.k;
				
				mainGroup.attr('transform', 
					`translate(${innerWidth / 2 + transform.x}, ${innerHeight / 2 + transform.y}) scale(${transform.k})`);
			});

		// Prevent page scrolling when zooming
		svgSelection
			.on('wheel', (event: any) => {
				event.preventDefault();
				event.stopPropagation();
			})
			.call(zoom);

		// Apply DYNAMIC automatic zoom
		const currentTransform = d3.zoomTransform(svgSelection.node() as any);
		
		// Always apply auto-zoom when:
		// 1. Initial load (transform is identity)
		// 2. Significant change in calculated zoom (data changed substantially)
		const isInitialLoad = currentTransform.k === 1 && currentTransform.x === 0 && currentTransform.y === 0;
		const significantChange = Math.abs(currentTransform.k - autoZoom) > 0.15;
		
		if (isInitialLoad || significantChange) {
			// Smooth transition to new zoom level - STAY CENTERED by using translate(0,0)
			svgSelection.transition()
				.duration(800)
				.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(autoZoom));
			currentZoomLevel = autoZoom;
		}

		isLoading = false;
	}

	// Handle search highlighting in a separate effect
	$effect(() => {
		if ($searchedSymbol && typeof window !== 'undefined') {
			console.log('Search highlighting for:', $searchedSymbol);
			// Search highlighting will be handled in the next render cycle
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

<!-- Loading State -->
{#if isLoading === true}
	<Loader {isLoading} />
{/if}

<!-- Navigation -->
<Navigation />

<!-- Enhanced Filter Menu - moved outside fading container -->
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

<!-- Main Chart Container -->
<div
	in:fade={{ duration: 500 }}
	class="chart-container"
	bind:clientWidth={innerWidth}
	bind:clientHeight={innerHeight}
	role="main"
	aria-label="IPC Tree Visualization"
>
	{#if innerWidth && innerHeight}
		<svg
			transition:fade={{ duration: 500, delay: 200 }}
			bind:this={svg}
			width="100%"
			height="100%"
			viewBox={`0 0 ${width} ${height}`}
			role="img"
			aria-label="Interactive patent classification tree diagram"
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
			</g>
		</svg>
	{/if}
	
	<!-- Footer -->
	<Footer {data} />
</div>

<style>
	:global(body) {
		background: radial-gradient(ellipse at center, #181824 0%, #0a0a12 100%);
		background-attachment: fixed;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.chart-container {
		width: 100vw;
		height: 100dvh;
		min-height: -webkit-fill-available;
		background: none;
		display: block;
		overflow: hidden;
		box-sizing: border-box;
		position: relative;
		padding-top: 60px;
		border: 2px solid #23233a;
		box-shadow: 0 0 40px #000a;
	}

	svg {
		width: 100%;
		height: 100%;
		background: none;
	}

	:global(.main-group) {
		filter: drop-shadow(0 0 24px #0008);
	}

	:global(.node-circle) {
		stroke: #fff3;
		stroke-width: 2.5;
		filter: drop-shadow(0 2px 8px #fff2) drop-shadow(0 0 16px #2228);
	}

	:global(.node-label) {
		font-family: 'EB Garamond', 'Georgia', serif;
		font-size: 1.1em;
		font-weight: 600;
		fill: #fff;
		paint-order: stroke fill;
		stroke: #181824cc;
		stroke-width: 3px;
		stroke-linejoin: round;
		text-shadow: 0 1px 8px #000a, 0 0 2px #fff2;
	}

	:global(.section-label) {
		font-family: 'EB Garamond', 'Georgia', serif;
		font-size: 2.8em;
		font-weight: 700;
		fill: #ffe082;
		text-shadow: 0 2px 16px #000a, 0 0 2px #ffe08299;
		pointer-events: none;
		letter-spacing: 0.08em;
	}

	:global(.section-subtitle) {
		font-family: 'EB Garamond', 'Georgia', serif;
		font-size: 1.1em;
		fill: #bfae7c;
		font-style: italic;
		text-shadow: 0 1px 8px #000a;
			pointer-events: none;
	}

	:global(.decorative-corner) {
		opacity: 0.13;
	}

	:global(.tooltip) {
		background: #23233aee;
		border: 1.5px solid #ffe082;
		color: #ffe082;
		font-family: 'EB Garamond', 'Georgia', serif;
	}

	:global(.tooltipsymbol) {
		background-color: #23233a;
		color: #ffe082;
		border: 1px solid #ffe082;
	}

	:global(.loading-pulse) {
		animation: pulse 2s ease-in-out infinite;
	}

	:global(button:focus-visible), :global(circle:focus-visible) {
		outline: 2.5px solid #ffe082;
		outline-offset: 2px;
		stroke: #ffe082;
		stroke-width: 3px;
	}
</style>