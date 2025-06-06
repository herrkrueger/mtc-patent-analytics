<!-- Footer -->
<script>
	let showModal = $state(false);
	let { data } = $props();

	function countAllChildren(node) {
		if (!node.children) return 0;
		return node.children.reduce(
			(count, child) => count + countAllChildren(child),
			node.children.length
		);
	}

	let numberOfAllChildren = $derived(countAllChildren(data));

  

	function toggleModal() {
		showModal = !showModal;
	}
	function handleKeypress(event) {
		// Check if the 'Enter' key was pressed
		if (event.key === 'Enter' || event.keyCode === 13) {
			toggleModal();
		}
	}
</script>

    

<div
	class="footer absolute w-full bottom-0 right-0 opacity-70 bg-transparent p-4 text-right text-white text-xs"
>

	<button
		class="px-2 py-1 mr-2 bg-white text-black rounded-full shadow hover:bg-blue-600 focus:outline-none"
		onclick={toggleModal}
	>
		?
	</button>
  Symbols: {numberOfAllChildren} | 
	<a href="https://www.patscenar.io/imprint" target="_blank">Imprint</a> |
	<a href="https://www.patscenar.io/privacy" target="_blank">Privacy</a>
	| <a href="https://mtc.berlin" target="_blank">mtc.berlin</a>
</div>

{#if showModal}
	<div
		role="dialog"
		class="fixed top-0 left-0 w-full h-full flex items-center justify-center z-50"
		aria-label="Close Modal"
		aria-roledescription="dialog"
		aria-modal="true"
	>
		<div
			class="bg-white p-8 rounded shadow-lg max-w-xl w-full relative"
			aria-label="Modal Content"
			aria-roledescription="dialog"
		>
			<button
				class="absolute top-4 right-4 text-gray-600 hover:text-gray-800 focus:outline-none"
				onclick={toggleModal}
				onkeypress={handleKeypress}
				tabindex="0"
				aria-label="Close Modal"
			>
				&times;
			</button>
			<h2 class="text-xl font-bold mb-4">Help</h2>
			<!-- Your formattable help text goes here -->
			<p class="text-gray-700 text-xs">
				<strong>Usage Guidelines:</strong>
			</p>
			<ul class="list-disc list-outside mt-2 text-sm">
				<li>
					<span class="font-bold">Subclass Limitation:</span><br /> For optimal performance, subclasses
					are limited to 3 levels down.
				</li>
				<li>
					<span class="font-bold">Max Depth:</span><br /> You can add more subclasses by adding more
					depth than the standard depth of 4. But be warned: This will slow down the visualization.
				</li>
				<li>
					<span class="font-bold">Filtering by Patent Sections:</span><br /> Use Filters A - H to filter
					by Patent Section. You can add multiple sections simultaneously.
				</li>
				<li>
					<span class="font-bold">Zooming:</span><br /> Scroll upwards to zoom in and scroll downwards
					to zoom out. To revert to the initial zoom level, click "reset zoom".
				</li>
				<li>
					<span class="font-bold">Panning:</span><br /> Hold and drag the mouse to move around the visualization.
				</li>
				<li>
					<span class="font-bold">Node Interaction:</span><br /> Click on a node to view its ascendants.
					To deselect a node, simply click anywhere else on the visualization.
				</li>
				<li>
					<span class="font-bold">Viewing Classification Details:</span><br /> For in-depth classification
					details, zoom in very close on individual nodes.
				</li>
				<li>
					<span class="font-bold">Copying Node Text:</span><br /> Right-click on a node to copy its text.
				</li>
			</ul>
			<p class="text-right text-xs">
				Data from <a
					href="https://www.wipo.int/classifications/ipc/en/"
					target="_blank"
					class="underline">WIPO</a
				>.
			</p>
		</div>
	</div>
{/if}
