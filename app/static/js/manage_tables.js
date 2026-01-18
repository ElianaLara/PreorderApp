// ========================
// Manage Tables JS
// ========================

document.addEventListener('DOMContentLoaded', () => {

    // ====== Head Chairs Toggle ======
    const headBtn = document.getElementById('toggle-head-chairs');
    headBtn.addEventListener('click', function () {
        const lastTableLeftChair = document.querySelector('.last-table-left');
        const firstTableRightChair = document.querySelector('.first-table-left');

        const tables = document.querySelectorAll('.table-wrapper');
        const lastTable = tables[tables.length - 1];
        const lastTableBox = lastTable.querySelector('.table-box');
        const lastTableChairs = lastTable.querySelectorAll('.chair:not(.side-chair)');

        const hidden = lastTableLeftChair.style.display === 'none';

        if (hidden) {
            headBtn.classList.add('active');
            headBtn.innerText = "Remove Head Chairs";

            if (lastTableLeftChair) lastTableLeftChair.style.display = 'flex';
            if (firstTableRightChair) firstTableRightChair.style.display = 'flex';

            lastTableBox.style.display = 'none';
            lastTableChairs.forEach(chair => chair.style.display = 'none');
        } else {
            headBtn.classList.remove('active');
            headBtn.innerText = "Add Head Chairs";

            if (lastTableLeftChair) lastTableLeftChair.style.display = 'none';
            if (firstTableRightChair) firstTableRightChair.style.display = 'none';

            lastTableBox.style.display = 'block';
            lastTableChairs.forEach(chair => chair.style.display = 'flex');
        }
    });

    // ====== Guest Card Toggle ======
    function toggleGuest(clickedCard) {
        document.querySelectorAll('.guest-card').forEach(card => {
            const details = card.querySelector('.guest-details');
            if (card !== clickedCard) details.style.display = 'none';
        });

        const details = clickedCard.querySelector('.guest-details');
        details.style.display = details.style.display === 'block' ? 'none' : 'block';
    }

    document.querySelectorAll('.guest-card').forEach(card => {
        card.addEventListener('click', () => toggleGuest(card));
    });

    // ====== Drag & Drop ======
    function allowDrop(ev) {
        ev.preventDefault();
    }

    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.dataset.person);
    }

    function drop(ev) {
        ev.preventDefault();
        const name = ev.dataTransfer.getData("text");

        const allChairs = document.querySelectorAll('.chair');
        const alreadySeated = Array.from(allChairs).some(chair => {
            const span = chair.querySelector('.chair-name');
            return span && span.innerText === name;
        });
        if (alreadySeated) {
            alert(`${name} is already seated!`);
            return;
        }

        const existingName = ev.target.querySelector('.chair-name');
        if (existingName) {
            const prevName = existingName.innerText;
            existingName.remove();
            const guestCard = document.querySelector(`[data-person='${prevName}']`);
            if (guestCard) guestCard.parentElement.style.opacity = "1";
        }

        const span = document.createElement('span');
        span.classList.add('chair-name');
        span.innerText = name;
        ev.target.appendChild(span);
        ev.target.dataset.person = name;

    }

    document.querySelectorAll('.chair').forEach(chair => {
        chair.addEventListener('click', () => {
            const span = chair.querySelector('.chair-name');
            if (!span) return;
            const name = span.innerText;
            span.remove();
            chair.removeAttribute('data-person');

        });

        chair.addEventListener('dragover', allowDrop);
        chair.addEventListener('drop', drop);
    });

    document.querySelectorAll('.guest-name').forEach(nameSpan => {
        nameSpan.addEventListener('dragstart', drag);
    });

    // ====== Sort Dropdown ======
    const sortBtn = document.getElementById('sort-guests');
    const sortOptions = document.getElementById('sort-options');
    const categoryBox = document.getElementById('category-box');
    const categoryTitle = document.getElementById('category-title');
    const itemList = document.getElementById('item-list');

    sortBtn.addEventListener('click', () => {
        const isVisible = !categoryBox.classList.contains('d-none');

        if (isVisible) {
            // Hide everything if already visible
            categoryBox.classList.add('d-none');
            sortOptions.classList.add('d-none');
        } else {
            // Show dropdown
            sortOptions.classList.remove('d-none');
            categoryBox.classList.add('d-none'); // Keep category box hidden until a category is clicked
        }
    });

    document.querySelectorAll('.sort-option').forEach(option => {
        option.addEventListener('click', () => {
            const category = option.dataset.category;

            categoryTitle.textContent = category;
            itemList.innerHTML = '';

            if (categoryItems[category]) {
                Object.entries(categoryItems[category]).forEach(([name, count]) => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-outline-success btn-sm mb-1 w-100';
                    btn.textContent = `${name} × ${count}`;

                    btn.addEventListener('click', () => {
                        const itemName = name; // <-- FIXED here

                        // Reset all name highlights
                        document.querySelectorAll('.chair-name').forEach(nameEl => {
                            nameEl.classList.remove('highlight');
                        });

                        // Highlight only the names of people who ordered this item
                        document.querySelectorAll('.chair').forEach(chair => {
                            const person = chair.dataset.person;

                            if (person && orderLookup[person]?.includes(itemName)) {
                                const nameEl = chair.querySelector('.chair-name');
                                if (nameEl) {
                                    nameEl.classList.add('highlight');
                                }
                            }
                        });
                    });

                    itemList.appendChild(btn);
                });
            }

            categoryBox.classList.remove('d-none');
            sortOptions.classList.add('d-none');
        });
    });
 });