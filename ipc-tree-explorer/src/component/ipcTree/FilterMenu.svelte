<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { searchedSymbol, typeaheadSuggestions } from '$lib/stores';
	/**
	 * @typedef {Object} Props
	 * @property {any} buttonSymbols
	 * @property {any} selectedSymbols
	 * @property {any} toggleSymbol
	 * @property {boolean} [shouldResetZoom]
	 * @property {string} [dataMode]
	 * @property {any} data
	 * @property {any} MAX_DEPTH
	 */

	/** @type {Props} */
	let {
		buttonSymbols,
		selectedSymbols,
		toggleSymbol,
		shouldResetZoom = $bindable(false),
		dataMode = $bindable('ipc'),
		data = $bindable(),
		MAX_DEPTH = $bindable()
	} = $props();
	
	let inputValue = $state('');
	let selectedIndex = $state(-1);
	let items: HTMLElement[] = $state([]);
	let suggestions = $state([]); // Local suggestions state

	// Use derived state to extract symbols from data - this prevents infinite loops
	let symbols = $derived(() => {
		if (!data) return [];
		const symbolsArray: string[] = [];
		extractSymbols(data, symbolsArray);
		return symbolsArray;
	});

	// Derived suggestions based on input
	let filteredSuggestions = $derived.by(() => {
		if (!inputValue || inputValue.length === 0) return [];
		return symbols().filter((symbol) => symbol.startsWith(inputValue.toUpperCase()));
	});

	function handleSearchClick() {
		$searchedSymbol = inputValue.toUpperCase();
	}

	function handleKeydown(event: KeyboardEvent) {
		let container = document.getElementById('typeahead-listbox');
		if (!container) return;
		
		switch (event.key) {
			case 'ArrowDown':
				if (selectedIndex < filteredSuggestions.length - 1) selectedIndex++;
				if (items[selectedIndex]) {
					const element = items[selectedIndex];
					if (
						element.offsetTop + element.clientHeight >
						container.scrollTop + container.clientHeight
					) {
						container.scrollTop =
							element.offsetTop +
							element.clientHeight -
							container.clientHeight;
					}
				}
				break;
			case 'ArrowUp':
				if (selectedIndex > 0) selectedIndex--;
				if (items[selectedIndex]) {
					const element = items[selectedIndex];
					if (element.offsetTop < container.scrollTop) {
						container.scrollTop = element.offsetTop;
					}
				}
				break;
			case 'Enter':
				if (selectedIndex > -1 && selectedIndex < filteredSuggestions.length) {
					inputValue = filteredSuggestions[selectedIndex];
					handleSearchClick();
					selectedIndex = -1;
				}
				break;
			case 'Escape':
				selectedIndex = -1;
				break;
		}
	}

	function handleInputChange() {
		// Reset selected index when input changes
		selectedIndex = -1;
	}

	function extractSymbols(dataObj: any, symbolsArray: string[]) {
		if (dataObj.symbol) {
			symbolsArray.push(dataObj.symbol);
		}
		if (dataObj.children && dataObj.children.length > 0) {
			for (let child of dataObj.children) {
				extractSymbols(child, symbolsArray);
			}
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
</script>

<div
	class="filter-menu"
	role="toolbar"
	aria-label="Patent classification controls"
>
	<!-- Header Row -->
	<div class="filter-header">
		<div class="filter-title">
			<h2>Patent Classification Explorer</h2>
			<p>Choose sections and adjust depth to explore the patent tree</p>
		</div>
		<a href="https://mtc.berlin" target="_blank" class="logo-link">
			<img src="mtc_logo.svg" alt="MTC Logo" width="40" height="40" />
		</a>
	</div>

	<!-- Controls Grid -->
	<div class="controls-grid">
		<!-- Classification Type -->
		<div class="control-group">
			<label class="control-label">Classification</label>
			<div class="button-group">
				<button
					type="button"
					class="toggle-btn {dataMode === 'ipc' ? 'active' : ''}"
					onclick={() => (dataMode = 'ipc')}
					aria-pressed={dataMode === 'ipc'}
				>
					IPC
				</button>
				<button
					type="button"
					class="toggle-btn {dataMode === 'cpc' ? 'active' : ''}"
					onclick={() => (dataMode = 'cpc')}
					aria-pressed={dataMode === 'cpc'}
				>
					CPC
				</button>
			</div>
		</div>

		<!-- Section Selection -->
		<div class="control-group">
			<label class="control-label">Patent Sections</label>
			<div class="section-buttons">
				{#each buttonSymbols as symbol}
					<button
						type="button"
						class="section-btn {selectedSymbols.has(symbol) ? 'selected' : ''}"
						onclick={() => toggleSymbol(symbol)}
						aria-pressed={selectedSymbols.has(symbol)}
						title="{symbol}: {symbolToTitleMapping[symbol] || 'Unknown'}"
					>
						{symbol}
					</button>
				{/each}
			</div>
		</div>

		<!-- Depth Control -->
		<div class="control-group">
			<label for="depthSlider" class="control-label">
				Max Depth: <span class="depth-value {MAX_DEPTH > 4 ? 'high' : 'normal'}">{MAX_DEPTH}</span>
			</label>
			<div class="slider-container">
				<input
					id="depthSlider"
					type="range"
					min="3"
					max="10"
					bind:value={MAX_DEPTH}
					class="depth-slider"
					aria-label="Maximum tree depth"
				/>
				<div class="slider-labels">
					<span>3</span>
					<span>10</span>
				</div>
			</div>
		</div>

		<!-- Search -->
		<div class="control-group">
			<label class="control-label">Search Symbol</label>
			<div class="search-container">
				<input
					type="text"
					class="search-input"
					bind:value={inputValue}
					oninput={handleInputChange}
					onkeydown={handleKeydown}
					placeholder="Enter patent symbol..."
					aria-label="Search patent symbols"
					role="combobox"
					aria-autocomplete="list"
					aria-controls="typeahead-listbox"
					aria-expanded={filteredSuggestions.length > 0}
				/>
				<button
					type="button"
					class="search-btn"
					onclick={handleSearchClick}
					aria-label="Search"
				>
					🔍
				</button>
			</div>
			
			<!-- Typeahead Dropdown -->
			{#if inputValue.length > 0}
				<div
					id="typeahead-listbox"
					role="listbox"
					class="typeahead-dropdown"
				>
					{#if filteredSuggestions.length > 0}
						{#each filteredSuggestions as suggestion, index}
							<div
								bind:this={items[index]}
								role="option"
								aria-selected={index === selectedIndex}
								tabindex="0"
								class="typeahead-item {index === selectedIndex ? 'selected' : ''}"
								onclick={() => {
									inputValue = suggestion;
									selectedIndex = -1;
									handleSearchClick();
								}}
								onkeydown={() => {
									inputValue = suggestion;
									selectedIndex = -1;
								}}
							>
								{suggestion}
							</div>
						{/each}
					{:else}
						<div class="typeahead-empty">
							Add more sections or increase depth if symbol not found.
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- Reset Zoom -->
		<div class="control-group">
			<button
				type="button"
				class="reset-btn"
				onclick={() => {
					shouldResetZoom = true;
				}}
				aria-label="Reset zoom to fit view"
			>
				🔄 Reset Zoom
			</button>
		</div>
	</div>
</div>

<style>
	.filter-menu {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		background: linear-gradient(135deg, rgba(13, 13, 27, 0.98) 0%, rgba(35, 35, 58, 0.95) 100%);
		backdrop-filter: blur(12px);
		border-bottom: 1px solid rgba(255, 224, 130, 0.2);
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
		z-index: 1000;
		padding: 1rem 1.5rem;
		font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	}

	.filter-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
	}

	.filter-title h2 {
		color: #ffe082;
		font-size: 1.25rem;
		font-weight: 600;
		margin: 0 0 0.25rem 0;
		letter-spacing: 0.025em;
	}

	.filter-title p {
		color: #bfae7c;
		font-size: 0.875rem;
		margin: 0;
		opacity: 0.9;
	}

	.logo-link {
		opacity: 0.8;
		transition: opacity 0.2s ease;
	}

	.logo-link:hover {
		opacity: 1;
	}

	.controls-grid {
		display: grid;
		grid-template-columns: auto 1fr auto auto auto;
		gap: 2rem;
		align-items: start;
	}

	.control-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		min-width: 0;
	}

	.control-label {
		color: #ffe082;
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin: 0;
	}

	.button-group {
		display: flex;
		border-radius: 6px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.toggle-btn {
		background: rgba(255, 255, 255, 0.1);
		border: none;
		color: #fff;
		padding: 0.5rem 1rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s ease;
		border-right: 1px solid rgba(255, 255, 255, 0.1);
	}

	.toggle-btn:last-child {
		border-right: none;
	}

	.toggle-btn:hover {
		background: rgba(255, 224, 130, 0.2);
	}

	.toggle-btn.active {
		background: #ffe082;
		color: #181824;
	}

	.section-buttons {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.section-btn {
		width: 2.5rem;
		height: 2.5rem;
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.1);
		color: #fff;
		font-weight: 600;
		font-size: 1rem;
		cursor: pointer;
		transition: all 0.2s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.section-btn:hover {
		border-color: #ffe082;
		background: rgba(255, 224, 130, 0.1);
		transform: translateY(-1px);
	}

	.section-btn.selected {
		border-color: #ffe082;
		background: #ffe082;
		color: #181824;
		box-shadow: 0 4px 12px rgba(255, 224, 130, 0.3);
	}

	.slider-container {
		position: relative;
	}

	.depth-slider {
		width: 120px;
		height: 6px;
		border-radius: 3px;
		background: rgba(255, 255, 255, 0.2);
		outline: none;
		-webkit-appearance: none;
		cursor: pointer;
	}

	.depth-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 18px;
		height: 18px;
		border-radius: 50%;
		background: #ffe082;
		cursor: pointer;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
		transition: transform 0.2s ease;
	}

	.depth-slider::-webkit-slider-thumb:hover {
		transform: scale(1.1);
	}

	.depth-slider::-moz-range-thumb {
		width: 18px;
		height: 18px;
		border-radius: 50%;
		background: #ffe082;
		cursor: pointer;
		border: none;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
	}

	.slider-labels {
		display: flex;
		justify-content: space-between;
		margin-top: 0.25rem;
		font-size: 0.75rem;
		color: #bfae7c;
	}

	.depth-value {
		font-weight: 600;
		padding: 0.125rem 0.375rem;
		border-radius: 4px;
		background: rgba(255, 255, 255, 0.1);
	}

	.depth-value.high {
		background: rgba(255, 107, 107, 0.2);
		color: #ff6b6b;
	}

	.depth-value.normal {
		background: rgba(81, 207, 102, 0.2);
		color: #51cf66;
	}

	.search-container {
		display: flex;
		position: relative;
	}

	.search-input {
		flex: 1;
		padding: 0.5rem 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px 0 0 6px;
		background: rgba(255, 255, 255, 0.1);
		color: #fff;
		font-size: 0.875rem;
		outline: none;
		transition: border-color 0.2s ease;
		min-width: 180px;
	}

	.search-input:focus {
		border-color: #ffe082;
		background: rgba(255, 255, 255, 0.15);
	}

	.search-input::placeholder {
		color: rgba(255, 255, 255, 0.5);
	}

	.search-btn {
		padding: 0.5rem 0.75rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-left: none;
		border-radius: 0 6px 6px 0;
		background: rgba(255, 224, 130, 0.2);
		color: #ffe082;
		cursor: pointer;
		transition: background-color 0.2s ease;
		font-size: 0.875rem;
	}

	.search-btn:hover {
		background: rgba(255, 224, 130, 0.3);
	}

	.typeahead-dropdown {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		background: rgba(35, 35, 58, 0.98);
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 224, 130, 0.3);
		border-radius: 6px;
		max-height: 200px;
		overflow-y: auto;
		z-index: 1001;
		margin-top: 0.25rem;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
	}

	.typeahead-item {
		padding: 0.75rem;
		color: #fff;
		cursor: pointer;
		transition: background-color 0.2s ease;
		font-size: 0.875rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.1);
	}

	.typeahead-item:last-child {
		border-bottom: none;
	}

	.typeahead-item:hover,
	.typeahead-item.selected {
		background: rgba(255, 224, 130, 0.2);
		color: #ffe082;
	}

	.typeahead-empty {
		padding: 0.75rem;
		color: #bfae7c;
		font-style: italic;
		font-size: 0.875rem;
		text-align: center;
	}

	.reset-btn {
		padding: 0.5rem 1rem;
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 6px;
		background: rgba(255, 255, 255, 0.1);
		color: #fff;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s ease;
		white-space: nowrap;
	}

	.reset-btn:hover {
		border-color: #ffe082;
		background: rgba(255, 224, 130, 0.1);
		transform: translateY(-1px);
	}

	/* Responsive Design */
	@media (max-width: 1200px) {
		.controls-grid {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}
		
		.control-group {
			align-items: start;
		}
	}

	@media (max-width: 768px) {
		.filter-menu {
			padding: 0.75rem 1rem;
		}
		
		.filter-header {
			flex-direction: column;
			gap: 0.5rem;
			text-align: center;
		}
		
		.section-buttons {
			justify-content: center;
		}
		
		.search-input {
			min-width: 140px;
		}
	}
</style>
