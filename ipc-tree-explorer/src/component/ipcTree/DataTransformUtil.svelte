<!-- @migration-task Error while migrating Svelte code: Identifier 'toggleSymbol' has already been declared
https://svelte.dev/e/js_parse_error -->
<script>
    export let buttonSymbols;
    export let selectedSymbols;
    export let toggleSymbol;
    export let shouldResetZoom;
    
    function reshapeData(ipcClass, depth = 0) {
    if (depth >= MAX_DEPTH) return [];  // Prevent reshaping if depth exceeds the limit
    
    return ipcClass.map(entry => ({
        symbol: entry.symbol,
        title: entry.title || symbolToTitleMapping[entry.symbol] || 'Unknown',
        children: entry.children ? reshapeData(entry.children, depth + 1) : []
    }));
}

let data = {
    title: 'Root Title',
    symbol: 'Root Symbol',
    children: [{
        symbol: 'F',
        title: symbolToTitleMapping['F'] || 'Unknown',
        children: reshapeData(symbolDataMap['F'])
    }]
};


$: console.log('data', data);


function toggleSymbol(symbol) {
  isLoading = true;
    console.log('toggleSymbol', symbol);

    const existingChild = data.children.find(child => child.symbol === symbol);

    if (existingChild) {
        // If the symbol is already selected, remove it from the children of data
        data = {
            ...data,
            children: data.children.filter(child => child.symbol !== symbol)
        };
        selectedSymbols.delete(symbol);
        selectedSymbols = selectedSymbols;
    } else {
        // If the symbol is not yet selected, add it to the children of data
        let newChild = {
            symbol: symbol,
            title: 'Some Default Title', // Update this accordingly
            children: reshapeData(symbolDataMap[symbol])
        };
        
        data = {
            ...data,
            children: [...data.children, newChild]
        };
        
        selectedSymbols.add(symbol);
        selectedSymbols = selectedSymbols;
        console.log("data after toggle", data);
        console.log("selectedSymbols after toggle", selectedSymbols);
    }
}
</script>