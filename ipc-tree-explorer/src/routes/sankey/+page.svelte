<script lang="ts">
	import * as d3 from 'd3';
	import { fade } from 'svelte/transition';
	import Loader from '../../component/ipcTree/Loader.svelte';
	import FilterMenu from '../../component/ipcTree/FilterMenu.svelte';
	import Footer from '../../component/ipcTree/Footer.svelte';
	import Navigation from '../../component/ipcTree/Navigation.svelte';
	import { searchedSymbol, zoomStore } from '$lib/stores';
	import { onMount } from 'svelte';

	// Type definitions
	interface IPCNode {
		symbol: string;
		title: string | { _text?: string; $text?: string; [key: string]: any };
		children?: IPCNode[];
	}

	interface FlowNode {
		id: string;
		name: string;
		symbol: string;
		level: number;
		value: number;
		x: number;
		y: number;
		width: number;
		height: number;
		children: string[];
		rootSection: string;
	}

	interface FlowLink {
		source: string;
		target: string;
		value: number;
		path: string;
	}

	interface FlowData {
		nodes: FlowNode[];
		links: FlowLink[];
	}

	// State variables
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

	let svg: SVGSVGElement = $state();
	let innerWidth: number = $state();
	let innerHeight: number = $state();
	let width = $state(1200);
	let height = $state(800);
	let selectedSymbols = $state(new Set(['F']));
	let shouldResetZoom = $state(false);
	let dataMode: 'ipc' | 'cpc' = $state('ipc');
	let isLoading = $state(true);
	let MAX_DEPTH = $state(5);
	let renderTimeout: ReturnType<typeof setTimeout> | null = $state(null);

	// Performance: Memoized data fetching
	let dataCache = new Map<string, IPCNode>();

	onMount(async () => {
		isLoading = true;
		await fetchJSONFiles();
		// Force a re-render after data is loaded
		setTimeout(() => {
			selectedSymbols = new Set(selectedSymbols);
		}, 100);
	});

	async function fetchJSONFiles(): Promise<void> {
		isLoading = true;

		try {
			const ipcPromises = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'].map(async (cls) => {
				const cacheKey = `ipc_${cls}`;
				if (dataCache.has(cacheKey)) {
					return dataCache.get(cacheKey)!;
				}
				const response = await fetch(`/ipccpc/ipc_class_${cls.toLowerCase()}.json`);
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
				const data = await response.json();
				dataCache.set(cacheKey, data);
				return data;
			});

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
			
			console.log('Data loaded successfully');
			console.log('Sample data check:', {
				ipcClassF: ipcClassF ? 'loaded' : 'missing',
				ipcClassG: ipcClassG ? 'loaded' : 'missing',
				ipcClassH: ipcClassH ? 'loaded' : 'missing'
			});
		} catch (error) {
			console.error('Error fetching JSON files:', error);
		} finally {
			isLoading = false;
		}
	}


	const symbolToTitleMapping: Record<string, string> = {
		A: 'Human necessities',
		B: 'Performing operations; transporting',
		C: 'Chemistry; metallurgy',
		D: 'Textiles; paper',
		E: 'Fixed constructions',
		F: 'Mechanical engineering; lighting; heating; weapons; blasting',
		G: 'Physics',
		H: 'Electricity'
	};

	const symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] as const;
	


	// Convert hierarchical data to Flow format with better spacing
	function convertToFlowData(selectedSymbols: Set<string>): FlowData {
		console.log('Converting flow data for symbols:', Array.from(selectedSymbols));
		console.log('MAX_DEPTH set to:', MAX_DEPTH);
		const nodes: FlowNode[] = [];
		const links: FlowLink[] = [];
		const nodeMap = new Map<string, FlowNode>();
		
		// Check if we have any data to process
		if (selectedSymbols.size === 0) {
			console.log('No symbols selected');
			return { nodes, links };
		}

		// Larger dimensions optimized for many nodes
		const margin = { top: 80, right: 100, bottom: 40, left: 100 };
		const chartWidth = Math.max(2000, width * 2) - margin.left - margin.right;
		const chartHeight = Math.max(1500, height * 1.5) - margin.top - margin.bottom;
		
		// Use actual MAX_DEPTH for level calculation
		const levelWidth = chartWidth / Math.max(1, MAX_DEPTH);
		let nodeCounter = 0;

		// Track nodes by level for positioning
		const nodesByLevel: Record<number, FlowNode[]> = {};

		function addNode(node: IPCNode, parentId: string | null, level: number, rootSectionSymbol?: string): string {
			// Strictly enforce MAX_DEPTH
			if (level >= MAX_DEPTH) {
				console.log(`Skipping node at level ${level} due to MAX_DEPTH ${MAX_DEPTH}`);
				return '';
			}

			const nodeId = `node_${nodeCounter++}`;
			const title = extractTitle(node.title);
			const value = node.children?.length || 1;
			
			if (!nodesByLevel[level]) nodesByLevel[level] = [];
			
			// Track which root section this node belongs to
			const belongsToSection = rootSectionSymbol || (level === 1 ? node.symbol : 'ROOT');
			
			// Create better formatted names based on level
			let displayName: string;
			if (level === 0) {
				displayName = 'Patent Classifications';
			} else if (level === 1) {
				// For main sections, show symbol and full title
				displayName = `${node.symbol}: ${symbolToTitleMapping[node.symbol] || title}`;
			} else if (level === 2) {
				// For classes, show symbol and clean title
				const cleanTitle = title
					.replace(/[^\w\s-;,\.]/g, '') // Remove special chars but keep punctuation
					.replace(/\s+/g, ' ') // Normalize whitespace
					.trim();
				displayName = `${node.symbol}: ${cleanTitle}`;
			} else {
				// For deeper levels, just show the clean title
				const cleanTitle = title
					.replace(/[^\w\s-;,\.]/g, '')
					.replace(/\s+/g, ' ')
					.trim();
				displayName = cleanTitle.length > 50 ? cleanTitle.substring(0, 47) + '...' : cleanTitle;
			}
			
			// Optimized node sizing for many nodes
			const nodeWidth = Math.max(120, Math.min(220, levelWidth * 0.7));
			const nodeHeight = Math.max(30, Math.min(70, Math.log(value + 1) * 15 + 30));
			
			const flowNode: FlowNode = {
				id: nodeId,
				name: displayName,
				symbol: node.symbol,
				level: level,
				value: value,
				x: level * levelWidth + levelWidth / 2,
				y: 0, // Will be calculated later
				width: nodeWidth,
				height: nodeHeight,
				children: [],
				rootSection: belongsToSection // Add root section tracking
			};

			nodes.push(flowNode);
			nodesByLevel[level].push(flowNode);
			nodeMap.set(nodeId, flowNode);
			
			console.log(`Added node at level ${level}: ${displayName} (section: ${belongsToSection})`);

			// Create link from parent
			if (parentId && nodeMap.has(parentId)) {
				const parent = nodeMap.get(parentId)!;
				parent.children.push(nodeId);
				
				links.push({
					source: parentId,
					target: nodeId,
					value: value,
					path: '' // Will be calculated later
				});
			}

			// Process children with better organization for many nodes
			if (node.children && level < MAX_DEPTH - 1) {
				// More reasonable limits that still allow exploration
				let maxChildren: number;
				if (level === 1) maxChildren = 8; // Level 1 → 2: show more main classes
				else if (level === 2) maxChildren = 6; // Level 2 → 3: show subclasses  
				else if (level === 3) maxChildren = 4; // Level 3 → 4: show groups
				else maxChildren = 3; // Level 4+: show subgroups
				
				const childrenToProcess = node.children.slice(0, maxChildren);
				console.log(`Processing ${childrenToProcess.length} children for ${node.symbol} at level ${level} (max allowed: ${maxChildren})`);
				
				childrenToProcess.forEach(child => {
					addNode(child, nodeId, level + 1, belongsToSection);
				});
			}

			return nodeId;
		}

		// Add root node (Level 0)
		const rootNode: FlowNode = {
			id: 'root',
			name: 'Patent Classifications',
			symbol: 'ROOT',
			level: 0,
			value: selectedSymbols.size,
			x: levelWidth / 2,
			y: chartHeight / 2,
			width: 180,
			height: 60,
			children: [],
			rootSection: 'ROOT'
		};
		nodes.push(rootNode);
		nodesByLevel[0] = [rootNode];
		nodeMap.set('root', rootNode);

		// Process selected symbols (Level 1)
		Array.from(selectedSymbols).forEach(symbol => {
			console.log(`Processing symbol ${symbol} at level 1`);
			const symbolData = symbolDataMap[symbol as keyof typeof symbolDataMap];
			
			if (symbolData) {
				// Create the main section node
				const sectionNode: IPCNode = {
					symbol: symbol,
					title: symbolToTitleMapping[symbol],
					children: symbolData.children || []
				};
				
				const sectionId = addNode(sectionNode, 'root', 1, symbol);

				// Process children if they exist and we have depth remaining
				if (symbolData.children && symbolData.children.length > 0 && MAX_DEPTH > 2) {
					console.log(`Processing children for ${symbol}, limiting to 8 children`);
					// Allow more children to show the full classification structure
					symbolData.children.slice(0, 8).forEach(child => {
						addNode(child, sectionId, 2, symbol);
					});
				}
			}
		});

		console.log(`Final result: Generated ${nodes.length} nodes and ${links.length} links`);
		console.log('Nodes by level:', Object.keys(nodesByLevel).map(level => 
			`Level ${level}: ${nodesByLevel[parseInt(level)].length} nodes`
		));

		// Calculate Y positions for each level with optimized spacing for many nodes
		Object.keys(nodesByLevel).forEach(levelStr => {
			const level = parseInt(levelStr);
			const levelNodes = nodesByLevel[level];
			
			// Adjust spacing based on number of nodes in level
			const baseSpacing = 15;
			const spacing = levelNodes.length > 20 ? baseSpacing * 0.7 : 
						   levelNodes.length > 10 ? baseSpacing * 0.85 : baseSpacing;
			
			const totalHeight = levelNodes.reduce((sum, node) => sum + node.height + spacing, -spacing);
			const startY = Math.max(50, (chartHeight - totalHeight) / 2);

			let currentY = startY;
			levelNodes.forEach(node => {
				node.y = currentY + node.height / 2;
				currentY += node.height + spacing;
			});
		});

		// Calculate link paths with better curves
		links.forEach(link => {
			const source = nodeMap.get(link.source);
			const target = nodeMap.get(link.target);
			if (source && target) {
				const x1 = source.x + source.width / 2;
				const y1 = source.y;
				const x2 = target.x - target.width / 2;
				const y2 = target.y;
				const controlOffset = Math.abs(x2 - x1) * 0.4;
				
				link.path = `M${x1},${y1} C${x1 + controlOffset},${y1} ${x2 - controlOffset},${y2} ${x2},${y2}`;
			}
		});

		return { nodes, links };
	}

	function extractTitle(title: string | any): string {
		if (typeof title === 'string') return title;
		if (typeof title === 'object' && title !== null) {
			// Handle nested array format: [["TITLE"]] or [[["TITLE"]]]
			if (Array.isArray(title)) {
				// Recursively drill down through nested arrays
				let current: any = title;
				while (Array.isArray(current) && current.length > 0) {
					current = current[0];
				}
				if (typeof current === 'string') {
					return current;
				}
				// If we have an object at the end, check for common text properties
				if (typeof current === 'object' && current !== null && !Array.isArray(current)) {
					if (current.$text) return current.$text;
					if (current._text) return current._text;
					if (current.text) return current.text;
				}
			}
			
			// Handle various title formats in the IPC data
			if (title._text) return title._text;
			if (title.$text) return title.$text;
			if (title.text) return title.text;
			if (title['#text']) return title['#text'];
			
			// If it's an object with unknown structure, try to find any text value
			const values = Object.values(title);
			for (const value of values) {
				if (typeof value === 'string' && value.trim().length > 0) {
					return value;
				}
			}
		}
		return 'Unknown Title';
	}

	// Better text wrapping function
	function wrapText(text: string, maxWidth: number, fontSize: number): string[] {
		const words = text.split(' ');
		const lines: string[] = [];
		let currentLine = '';
		
		// Approximate character width based on font size
		const charWidth = fontSize * 0.6;
		const maxCharsPerLine = Math.floor(maxWidth / charWidth);
		
		for (const word of words) {
			const testLine = currentLine ? `${currentLine} ${word}` : word;
			
			if (testLine.length <= maxCharsPerLine) {
				currentLine = testLine;
			} else {
				if (currentLine) {
					lines.push(currentLine);
					currentLine = word;
				} else {
					// Word is too long, break it
					lines.push(word.substring(0, maxCharsPerLine));
					currentLine = word.substring(maxCharsPerLine);
				}
			}
		}
		
		if (currentLine) {
			lines.push(currentLine);
		}
		
		return lines;
	}

	function toggleSymbol(symbol: string): void {
		console.log('toggleSymbol called for:', symbol);
		console.log('Current selectedSymbols:', Array.from(selectedSymbols));

		if (selectedSymbols.has(symbol)) {
			// Remove symbol
			console.log('Removing symbol:', symbol);
			selectedSymbols.delete(symbol);
		} else {
			// Add symbol
			console.log('Adding symbol:', symbol);
			selectedSymbols.add(symbol);
		}
		
		// Force reactivity with new Set
		selectedSymbols = new Set(selectedSymbols);
		console.log('Updated selectedSymbols:', Array.from(selectedSymbols));
		
		// Reset zoom if needed
		$zoomStore = 'reset';
	}

	// Color scheme - bright pastels
	const pastelColors = [
		'#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', 
		'#D4BAFF', '#FFBAFF', '#FFC1CC', '#FFE5B4', '#B4E5FF',
		'#E5B4FF', '#FFE5E5', '#E5FFE5', '#E5E5FF'
	];

	const colorScale = d3.scaleOrdinal<string>()
		.domain(symbols)
		.range(pastelColors);

	function getNodeColor(node: FlowNode): string {
		if (node.level === 0) return '#F8F9FA'; // Light gray for root
		
		// Use the root section to determine base color
		const sectionSymbol = node.rootSection;
		const baseColor = d3.color(colorScale(sectionSymbol));
		
		if (baseColor) {
			if (node.level === 1) {
				// Level 1 nodes get the full color
				return baseColor.toString();
			} else {
				// For deeper levels, use a mix of brightness and saturation adjustments
				// to maintain visibility while showing hierarchy
				const hsl = d3.hsl(baseColor);
				
				if (hsl) {
					// Cycle through different variations to maintain contrast
					const levelVariation = (node.level - 2) % 4;
					
					switch (levelVariation) {
						case 0: // Lighter version
							hsl.l = Math.min(0.85, hsl.l + 0.2);
							hsl.s = Math.max(0.3, hsl.s - 0.1);
							break;
						case 1: // Slightly desaturated
							hsl.l = Math.min(0.75, hsl.l + 0.1);
							hsl.s = Math.max(0.4, hsl.s - 0.2);
							break;
						case 2: // More desaturated but still visible
							hsl.l = Math.min(0.8, hsl.l + 0.15);
							hsl.s = Math.max(0.25, hsl.s - 0.3);
							break;
						case 3: // Pastel version with good contrast
							hsl.l = Math.min(0.9, hsl.l + 0.25);
							hsl.s = Math.max(0.2, hsl.s - 0.4);
							break;
					}
					
					return hsl.toString();
				}
			}
		}
		
		return '#E9ECEF'; // Fallback light color
	}

	let buttonSymbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

	function handleSearch(event: CustomEvent<string>): void {
		const searchTerm = event.detail;
		console.log('Searching for:', searchTerm);
		if (searchTerm) {
			$searchedSymbol = searchTerm.toUpperCase();
		}
	}


	function renderFlow(): void {
		console.log('renderFlow called');
		
		const svgSelection = d3.select(svg);
		svgSelection.selectAll('*').remove();

		console.log('renderFlow called with selectedSymbols:', Array.from(selectedSymbols));
		
		const flowData = convertToFlowData(selectedSymbols);
		
		if (flowData.nodes.length === 0) {
			console.log('No nodes generated, skipping render');
			return;
		}

		console.log(`Rendering ${flowData.nodes.length} nodes and ${flowData.links.length} links`);

		try {
			// Much larger margins and dimensions
			const margin = { top: 80, right: 100, bottom: 40, left: 100 };
			const totalWidth = Math.max(2000, width * 2);
			const totalHeight = Math.max(1500, height * 1.5);

			// Set larger viewBox for scrolling
			svg.setAttribute('viewBox', `0 0 ${totalWidth} ${totalHeight}`);

			// Create main group with zoom/pan functionality
			const mainGroup = svgSelection.append('g').attr('class', 'main-group');
			
			// Set up zoom behavior
			const zoom = d3.zoom<SVGSVGElement, unknown>()
				.scaleExtent([0.1, 4])
				.on('zoom', (event: any) => {
					const { transform } = event;
					mainGroup.attr('transform', transform);
				});

			// Apply zoom behavior to SVG
			svgSelection.call(zoom);

			// Create content group
			const g = mainGroup
				.append('g')
				.attr('transform', `translate(${margin.left},${margin.top})`);

			// Create tooltip with better styling for light theme
			const tooltip = d3.select('body')
				.selectAll('.flow-tooltip')
				.data([null])
				.join('div')
				.attr('class', 'flow-tooltip')
				.attr('role', 'tooltip')
				.style('position', 'absolute')
				.style('visibility', 'hidden')
				.style('background', 'rgba(255, 255, 255, 0.95)')
				.style('color', '#333')
				.style('padding', '12px')
				.style('border-radius', '8px')
				.style('font-size', '13px')
				.style('max-width', '300px')
				.style('z-index', '1000')
				.style('box-shadow', '0 4px 20px rgba(0,0,0,0.15)')
				.style('border', '1px solid #ddd');

			// Draw links with better styling
			const links = g.selectAll('.flow-link')
				.data(flowData.links)
				.join('path')
				.attr('class', 'flow-link')
				.attr('d', (d: FlowLink) => d.path)
				.style('fill', 'none')
				.style('stroke', (d: FlowLink) => {
					const sourceNode = flowData.nodes.find(n => n.id === d.source);
					const sourceColor = sourceNode ? getNodeColor(sourceNode) : '#999';
					return d3.color(sourceColor)?.darker(0.3).toString() || '#999';
				})
				.style('stroke-width', (d: FlowLink) => Math.max(3, Math.min(12, d.value + 2)))
				.style('cursor', 'pointer')
				.style('opacity', 0.7)
				.style('transition', 'all 0.3s ease');

			// Draw nodes
			const nodes = g.selectAll('.flow-node')
				.data(flowData.nodes)
				.join('g')
				.attr('class', 'flow-node')
				.attr('transform', (d: FlowNode) => `translate(${d.x - d.width/2},${d.y - d.height/2})`);

			// Helper functions for highlighting
			function highlightConnections(selectedNodeId: string) {
				// Find the selected node
				const selectedNode = flowData.nodes.find(n => n.id === selectedNodeId);
				if (!selectedNode) return;
				
				// Find all nodes in the complete path
				const pathNodeIds = new Set<string>();
				const pathLinks: FlowLink[] = [];
				
				// 1. Find all ancestors (path to root)
				function findAncestors(nodeId: string) {
					pathNodeIds.add(nodeId);
					const incomingLinks = flowData.links.filter(link => link.target === nodeId);
					incomingLinks.forEach(link => {
						pathLinks.push(link);
						findAncestors(link.source); // Recursively find parent
					});
				}
				
				// 2. Find all descendants (complete subtree)
				function findDescendants(nodeId: string) {
					pathNodeIds.add(nodeId);
					const outgoingLinks = flowData.links.filter(link => link.source === nodeId);
					outgoingLinks.forEach(link => {
						pathLinks.push(link);
						findDescendants(link.target); // Recursively find children
					});
				}
				
				// Start from selected node and find complete path
				findAncestors(selectedNodeId);
				findDescendants(selectedNodeId);
				
				console.log(`Complete path includes ${pathNodeIds.size} nodes and ${pathLinks.length} links`);
				
				// Highlight path links with enhanced styling
				links.style('opacity', (d: FlowLink) => 
					pathLinks.includes(d) ? 1.0 : 0.15
				).style('stroke-width', (d: FlowLink) => {
					if (pathLinks.includes(d)) {
						// Make links thicker based on their level in hierarchy
						const sourceNode = flowData.nodes.find(n => n.id === d.source);
						const baseWidth = Math.max(6, Math.min(18, d.value + 6));
						return sourceNode && sourceNode.level <= 2 ? baseWidth + 3 : baseWidth;
					}
					return Math.max(1, Math.min(6, d.value));
				}).classed('highlighted', (d: FlowLink) => 
					pathLinks.includes(d)
				).style('stroke', (d: FlowLink) => {
					if (pathLinks.includes(d)) {
						// Use different colors for different parts of the path
						const sourceNode = flowData.nodes.find(n => n.id === d.source);
						const targetNode = flowData.nodes.find(n => n.id === d.target);
						
						if (sourceNode && targetNode) {
							// Root to selected: Blue gradient
							if (targetNode.id === selectedNodeId) {
								return '#0056b3'; // Darker blue for direct connection to selected
							}
							// Selected to descendants: Green gradient
							if (sourceNode.id === selectedNodeId) {
								return '#28a745'; // Green for outgoing from selected
							}
							// Ancestor path: Blue
							if (sourceNode.level < selectedNode.level) {
								return '#007bff';
							}
							// Descendant path: Green
							if (sourceNode.level >= selectedNode.level) {
								return '#20c997';
							}
						}
						return '#007bff'; // Default blue
					}
					// Non-path links keep original color but dimmed
					const sourceNode = flowData.nodes.find(n => n.id === d.source);
					const sourceColor = sourceNode ? getNodeColor(sourceNode) : '#999';
					return d3.color(sourceColor)?.darker(1.5).toString() || '#ccc';
				});
				
				// Highlight path nodes with different styles based on their role
				nodes.style('opacity', (d: FlowNode) => 
					pathNodeIds.has(d.id) ? 1.0 : 0.25
				).classed('connected', (d: FlowNode) => 
					pathNodeIds.has(d.id) && d.id !== selectedNodeId
				);
				
				// Enhanced glow effects for different node types
				nodes.selectAll('rect').style('filter', (d: FlowNode) => {
					if (d.id === selectedNodeId) {
						return 'drop-shadow(0 0 20px rgba(0,123,255,1.0)) drop-shadow(0 4px 12px rgba(0,0,0,0.3))';
					} else if (pathNodeIds.has(d.id)) {
						// Different glow for ancestors vs descendants
						if (d.level < selectedNode.level) {
							// Ancestor nodes - blue glow
							return 'drop-shadow(0 0 10px rgba(0,123,255,0.6)) drop-shadow(0 2px 6px rgba(0,0,0,0.15))';
						} else if (d.level > selectedNode.level) {
							// Descendant nodes - green glow
							return 'drop-shadow(0 0 10px rgba(40,167,69,0.6)) drop-shadow(0 2px 6px rgba(0,0,0,0.15))';
						} else {
							// Same level nodes - purple glow
							return 'drop-shadow(0 0 10px rgba(108,117,125,0.6)) drop-shadow(0 2px 6px rgba(0,0,0,0.15))';
						}
					}
					return 'drop-shadow(0 1px 3px rgba(0,0,0,0.1))';
				}).style('stroke', (d: FlowNode) => {
					if (d.id === selectedNodeId) {
						return '#0056b3';
					} else if (pathNodeIds.has(d.id)) {
						if (d.level < selectedNode.level) return '#007bff'; // Ancestors: blue
						if (d.level > selectedNode.level) return '#28a745'; // Descendants: green  
						return '#6c757d'; // Same level: gray
					}
					return '#666';
				}).style('stroke-width', (d: FlowNode) => {
					if (d.id === selectedNodeId) return '4px';
					if (pathNodeIds.has(d.id)) return '2.5px';
					return '1px';
				});
				
				// Show detailed path information
				const ancestorCount = Array.from(pathNodeIds).filter(id => {
					const node = flowData.nodes.find(n => n.id === id);
					return node && node.level < selectedNode.level;
				}).length;
				
				const descendantCount = Array.from(pathNodeIds).filter(id => {
					const node = flowData.nodes.find(n => n.id === id);
					return node && node.level > selectedNode.level;
				}).length;
				
				console.log(`Path: ${ancestorCount} ancestors → selected node → ${descendantCount} descendants`);
			}
			
			function resetHighlighting() {
				// Reset all links
				links.style('opacity', 0.7)
					.style('stroke-width', (d: FlowLink) => Math.max(3, Math.min(12, d.value + 2)))
					.classed('highlighted', false)
					.style('stroke', (d: FlowLink) => {
						const sourceNode = flowData.nodes.find(n => n.id === d.source);
						const sourceColor = sourceNode ? getNodeColor(sourceNode) : '#999';
						return d3.color(sourceColor)?.darker(0.3).toString() || '#999';
					});
				
				// Reset all nodes
				nodes.style('opacity', 1.0)
					.classed('connected', false);
				
				// Reset filters and borders
				nodes.selectAll('rect')
					.style('filter', 'drop-shadow(0 2px 6px rgba(0,0,0,0.15))')
					.style('stroke', '#666')
					.style('stroke-width', '1.5px');
				
				console.log('Complete path highlighting reset');
			}

			// Node rectangles with better styling and click handling
			nodes.append('rect')
				.attr('width', (d: FlowNode) => d.width)
				.attr('height', (d: FlowNode) => d.height)
				.style('fill', (d: FlowNode) => getNodeColor(d))
				.style('stroke', '#666')
				.style('stroke-width', 1.5)
				.style('rx', 8)
				.style('cursor', 'pointer')
				.style('filter', 'drop-shadow(0 2px 6px rgba(0,0,0,0.15))')
				.style('transition', 'all 0.3s ease')
				.on('mouseover', (event: MouseEvent, d: FlowNode) => {
					const element = event.currentTarget as SVGRectElement;
					if (!d3.select(element).classed('selected')) {
						d3.select(element).style('opacity', 0.8).style('transform', 'scale(1.02)');
					}
					tooltip
						.style('visibility', 'visible')
						.html(`
							<strong>Symbol:</strong> ${d.symbol}<br/>
							<strong>Level:</strong> ${d.level}<br/>
							<strong>Children:</strong> ${d.children.length}<br/>
							<strong>Full Name:</strong> ${d.name}<br/>
							<em>Click to highlight connections</em>
						`);
				})
				.on('mousemove', (event: MouseEvent) => {
					tooltip
						.style('top', (event.pageY - 10) + 'px')
						.style('left', (event.pageX + 10) + 'px');
				})
				.on('mouseout', (event: MouseEvent, d: FlowNode) => {
					const element = event.currentTarget as SVGRectElement;
					if (!d3.select(element).classed('selected')) {
						d3.select(element).style('opacity', 1).style('transform', 'scale(1)');
					}
					tooltip.style('visibility', 'hidden');
				})
				.on('click', (event: MouseEvent, d: FlowNode) => {
					event.stopPropagation();
					console.log('Clicked node:', d);
					
					// Remove previous selection
					nodes.selectAll('rect').classed('selected', false);
					
					// Add selection to current node
					d3.select(event.currentTarget as SVGRectElement).classed('selected', true);
					
					// Highlight connections
					highlightConnections(d.id);
				});

			// Add click handler to reset highlighting when clicking on background
			g.on('click', () => {
				console.log('Clicked background, resetting highlights');
				nodes.selectAll('rect').classed('selected', false);
				resetHighlighting();
			});

			// Node labels with text wrapping
			nodes.each(function(this: SVGGElement, d: FlowNode) {
				const nodeGroup = d3.select(this);
				const fontSize = Math.min(14, Math.max(10, d.height / 5));
				const textLines = wrapText(d.name, d.width - 16, fontSize);
				
				// Calculate line height and starting position
				const lineHeight = fontSize + 2;
				const totalTextHeight = textLines.length * lineHeight;
				const startY = d.height / 2 - totalTextHeight / 2 + fontSize / 2;
				
				textLines.forEach((line, index) => {
					nodeGroup.append('text')
						.attr('x', d.width / 2)
						.attr('y', startY + (index * lineHeight))
						.attr('text-anchor', 'middle')
						.style('font-family', 'Inter, sans-serif')
						.style('font-size', fontSize + 'px')
						.style('font-weight', d.level <= 1 ? 'bold' : 'normal')
						.style('fill', '#333') // Dark text for light background
						.style('pointer-events', 'none')
						.text(line);
				});
			});

			// Add title with dark text
			svgSelection.append('text')
				.attr('x', totalWidth / 2)
				.attr('y', 40)
				.attr('text-anchor', 'middle')
				.style('font-family', 'Inter, sans-serif')
				.style('font-size', '24px')
				.style('font-weight', 'bold')
				.style('fill', '#333')
				.text(`${dataMode.toUpperCase()} Patent Classification Flow (Depth: ${MAX_DEPTH})`);

			// Initial zoom to fit content
			const bbox = g.node()?.getBBox();
			if (bbox) {
				const scale = 0.9 * Math.min(
					(totalWidth - margin.left - margin.right) / bbox.width,
					(totalHeight - margin.top - margin.bottom) / bbox.height
				);
				const translateX = (totalWidth - bbox.width * scale) / 2 - bbox.x * scale;
				const translateY = (totalHeight - bbox.height * scale) / 2 - bbox.y * scale;
				
				svgSelection.call(
					zoom.transform,
					d3.zoomIdentity.translate(translateX, translateY).scale(scale)
				);
			}

			console.log('Render completed successfully');
		} catch (error) {
			console.error('Error during rendering:', error);
		}
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
			width = Math.max(1400, innerWidth);
			height = Math.max(1000, innerHeight);
		}
	});
	
	let symbolDataMap = $derived(dataMode === 'ipc'
		? {
				A: ipcClassA, B: ipcClassB, C: ipcClassC, D: ipcClassD,
				E: ipcClassE, F: ipcClassF, G: ipcClassG, H: ipcClassH
		  }
		: {
				A: cpcClassA, B: cpcClassB, C: cpcClassC, D: cpcClassD,
				E: cpcClassE, F: cpcClassF, G: cpcClassG, H: cpcClassH
		  });
		  
	// Fix the main data object for better compatibility
	let data = $derived({
		title: 'IPC Section Start',
		symbol: 'Node Zero',
		children: Array.from(selectedSymbols).map((symbol) => {
			const symbolData = symbolDataMap[symbol as keyof typeof symbolDataMap];
			return {
				symbol: symbol,
				title: symbolToTitleMapping[symbol] || 'Unknown',
				children: symbolData?.children || []
			};
		})
	});
	
	// Simple reactive visualization logic without loading state dependency
	$effect(() => {
		// Clear any existing timeout
		if (renderTimeout) {
			clearTimeout(renderTimeout);
		}
		
		if (selectedSymbols.size > 0 && svg && innerWidth && innerHeight && MAX_DEPTH) {
			console.log('Scheduling render for symbols:', Array.from(selectedSymbols), 'depth:', MAX_DEPTH);
			
			// Debounce the rendering to prevent rapid updates
			renderTimeout = setTimeout(() => {
				console.log('Executing debounced render');
				requestAnimationFrame(() => {
					renderFlow();
				});
			}, 150);
		} else if (selectedSymbols.size === 0 && svg) {
			// Handle empty selection case immediately
			console.log('No symbols selected, clearing visualization');
			const svgSelection = d3.select(svg);
			svgSelection.selectAll('*').remove();
			
			// Add a message for empty state
			svgSelection.append('text')
				.attr('x', width / 2)
				.attr('y', height / 2)
				.attr('text-anchor', 'middle')
				.style('font-family', 'Inter, sans-serif')
				.style('font-size', '18px')
				.style('fill', '#666')
				.text('Select symbols from the filter menu to view the flow diagram');
		}
	});
	
	// Debug reactive statement to check data loading
	$effect(() => {
		console.log('Selected symbols:', Array.from(selectedSymbols));
		console.log('Symbol data map status:', {
			F: symbolDataMap.F ? 'loaded' : 'not loaded',
			G: symbolDataMap.G ? 'loaded' : 'not loaded', 
			H: symbolDataMap.H ? 'loaded' : 'not loaded'
		});
		console.log('MAX_DEPTH:', MAX_DEPTH);
	});
</script>

<svelte:head>
	<title>IPC Sankey Explorer</title>
	<meta name="og:title" content="IPC Sankey Explorer" />
	<meta name="og:description" content="Explore the IPC Tree with Sankey Diagrams" />
	<meta name="og:image" content="https://ipc.patscenar.io/og_image.png" />
	<meta name="theme-color" content="#000000" />
	<meta name="msapplication-navbutton-color" content="#000000" />
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
	aria-label="IPC Flow Visualization"
>
	<!-- Zoom Instructions -->
	<div class="zoom-instructions">
		🖱️ Drag to pan<br/>
		🔍 Scroll to zoom<br/>
		📱 Pinch to zoom
	</div>

	{#if innerWidth && innerHeight}
		<svg
			transition:fade={{ duration: 500, delay: 200 }}
			bind:this={svg}
			width="100%"
			height="100%"
			viewBox={`0 0 ${width} ${height}`}
			role="img"
			aria-label="Interactive patent classification flow diagram"
		/>
	{/if}
	
	<!-- Footer -->
	<Footer {data} />
</div>

<style>
	:global(body) {
		background-color: #f8f9fa;
		overflow: hidden;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.chart-container {
		width: 100vw;
		height: 100dvh;
		min-height: -webkit-fill-available;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
		display: block;
		overflow: auto; /* Enable scrolling */
		box-sizing: border-box;
		position: relative;
		padding-top: 60px; /* Account for navigation */
	}

	svg {
		min-width: 1400px; /* Ensure minimum width for horizontal scrolling */
		min-height: 1000px; /* Ensure minimum height for vertical scrolling */
		width: 100%;
		height: 100%;
		display: block; /* Remove inline spacing */
		cursor: grab;
	}

	svg:active {
		cursor: grabbing;
	}

	:global(.flow-tooltip) {
		pointer-events: none !important;
		font-family: 'Inter', sans-serif;
		line-height: 1.4;
		backdrop-filter: blur(10px);
		border: 1px solid #e0e0e0 !important;
		background: rgba(255, 255, 255, 0.95) !important;
		color: #333 !important;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
	}

	:global(.flow-link) {
		transition: all 0.2s ease;
	}

	:global(.flow-link:hover) {
		stroke-opacity: 1 !important;
		stroke-width: 8px !important;
	}

	:global(.flow-node rect) {
		transition: all 0.2s ease;
	}

	:global(.flow-node:hover rect) {
		filter: brightness(1.1) drop-shadow(0 4px 12px rgba(0,0,0,0.2)) !important;
	}

	/* Enhanced animations for bright theme */
	@keyframes flowPulse {
		0%, 100% { stroke-opacity: 0.7; }
		50% { stroke-opacity: 0.4; }
	}

	:global(.flow-link) {
		animation: flowPulse 6s ease-in-out infinite;
	}

	/* Better focus states for accessibility */
	:global(.flow-node rect:focus-visible) {
		outline: 3px solid #4A90E2;
		outline-offset: 2px;
	}

	/* Selection states for better visual feedback */
	:global(.flow-node rect.selected) {
		stroke: #007bff !important;
		stroke-width: 3px !important;
		filter: drop-shadow(0 0 12px rgba(0,123,255,0.8)) drop-shadow(0 2px 6px rgba(0,0,0,0.15)) !important;
	}

	:global(.flow-link.highlighted) {
		animation: flowHighlight 2s ease-in-out infinite;
	}

	@keyframes flowHighlight {
		0%, 100% { 
			stroke-opacity: 1.0;
			filter: drop-shadow(0 0 6px rgba(0,123,255,0.6));
		}
		50% { 
			stroke-opacity: 0.8;
			filter: drop-shadow(0 0 12px rgba(0,123,255,0.8));
		}
	}

	/* Enhanced connection indicators */
	:global(.flow-node.connected) {
		animation: nodeGlow 3s ease-in-out infinite;
	}

	@keyframes nodeGlow {
		0%, 100% { filter: drop-shadow(0 2px 6px rgba(0,0,0,0.15)); }
		50% { filter: drop-shadow(0 4px 12px rgba(0,123,255,0.3)); }
	}

	/* Navigation hint for bright theme */
	:global(body:after) {
		content: 'flow view';
		position: fixed;
		width: 80px;
		height: 25px;
		background: linear-gradient(45deg, #667eea, #764ba2);
		bottom: 8px;
		left: -20px;
		text-align: center;
		font-size: 9px;
		font-family: sans-serif;
		text-transform: uppercase;
		font-weight: bold;
		color: #fff;
		line-height: 25px;
		transform: rotate(45deg);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	/* Zoom instructions overlay */
	.zoom-instructions {
		position: absolute;
		top: 80px;
		right: 20px;
		background: rgba(255, 255, 255, 0.9);
		padding: 12px 16px;
		border-radius: 8px;
		font-size: 12px;
		color: #666;
		border: 1px solid #e0e0e0;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		z-index: 100;
	}

	@media (max-width: 768px) {
		.chart-container {
			padding-top: 50px;
		}
		
		.zoom-instructions {
			font-size: 10px;
			padding: 8px 12px;
			right: 10px;
		}
	}
</style> 