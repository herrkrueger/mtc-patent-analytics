import { writable } from 'svelte/store';
export const searchedSymbol = writable("");
export const typeaheadSuggestions = writable([]);
export const zoomStore = writable('');