document.addEventListener("DOMContentLoaded", () => {

  // !!! +/- logic
  // Select all headers: categories and all subcategories
  const headers = document.querySelectorAll(".category-header, .subcategory-header");

  headers.forEach(header => {
    header.addEventListener("click", () => {
      // Find the closest container (category or subcategory)
      const container = header.closest(".category, .subcategory");
      if (!container) return;

      // Toggle open class
      container.classList.toggle("open");

      // Update the + / − symbol
      const toggle = header.querySelector(".toggle");
      toggle.textContent = container.classList.contains("open") ? "−" : "+";
    });
  });



  //Add items logic
 const itemList = document.getElementById("your-items-list");

  document.querySelectorAll(".add-btn").forEach(button => {
    button.addEventListener("click", () => {
      const name = button.dataset.name;
      let size = button.dataset.size;
      const subcat = button.dataset.subcat;

      // Check for size select
      const select = button.closest(".item").querySelector("select");
      if (select) size = select.value;

      // Check if any item from this subcategory already exists
      const exists = Array.from(itemList.children).some(li => li.dataset.subcat === subcat);
      if (exists) {
        alert(`You already added an item from "${subcat}"`);
        return;
      }

      // Add the item
      const li = document.createElement("li");
      li.textContent = size ? `${name} - ${size}` : name;
      li.dataset.subcat = subcat; // track subcategory
      itemList.appendChild(li);
    });
  });
});


