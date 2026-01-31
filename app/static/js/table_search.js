function enableTableSearch(inputId, tableId) { //Takes two arguments
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!searchInput || !table) return; // prevents errors

    searchInput.addEventListener('keyup', function() { // Listens for the release of a key (updates while type)
        const filter = this.value.toLowerCase(); //current text
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            // Check all cells in the row
            // converts to an array to use map
            const text = Array.from(row.cells).map(cell => cell.textContent.toLowerCase()).join(' ');
            row.style.display = text.includes(filter) ? '' : 'none'; //if the row includes it, it is visible if not hidden
        });
    });
}