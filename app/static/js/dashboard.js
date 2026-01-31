let dateAsc = true;
let statusAsc = true;

const statusPriority = {
  pending: 1,
  completed: 2,
  approved: 3
};

function parseUKDate(dateStr) {
  const [day, month, year] = dateStr.split('/');
  return new Date(year, month - 1, day);
}

function sortByDate() {
  const table = document.querySelector('.orders-table');
  const rows = Array.from(table.querySelectorAll('.order-row'));

  rows.sort((a, b) => {
    const dateA = parseUKDate(a.children[4].innerText.trim());
    const dateB = parseUKDate(b.children[4].innerText.trim());

    return dateAsc ? dateA - dateB : dateB - dateA;
  });

  dateAsc = !dateAsc;
  rows.forEach(row => table.appendChild(row));
}

function sortByStatus() {
  const table = document.querySelector('.orders-table');
  const rows = Array.from(table.querySelectorAll('.order-row'));

  rows.sort((a, b) => {
    const statusA = a.querySelector('.status-dropdown').value;
    const statusB = b.querySelector('.status-dropdown').value;

    const diff = statusPriority[statusA] - statusPriority[statusB];
    return statusAsc ? diff : -diff;
  });

  statusAsc = !statusAsc;
  rows.forEach(row => table.appendChild(row));
}

