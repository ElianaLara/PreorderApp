document.addEventListener("DOMContentLoaded", () => {

  /* +/- TOGGLE LOGIC */
  document.querySelectorAll(".category-header, .subcategory-header").forEach(header => {
    header.addEventListener("click", () => {
      const container = header.closest(".category, .subcategory");
      if (!container) return;

      container.classList.toggle("open");
      header.querySelector(".toggle").textContent =
        container.classList.contains("open") ? "−" : "+";
    });
  });

  /* ADD ITEMS LOGIC */
  const itemList = document.getElementById("your-items-list");

  document.querySelectorAll(".add-btn").forEach(button => {
    button.addEventListener("click", () => {
      const name = button.dataset.name;
      const subcat = button.dataset.subcat;
      let size = "";

      const select = button.closest(".item").querySelector("select");
      if (select) size = select.value;

      // Only one item per subcategory
      const exists = [...itemList.children].some(
        li => li.dataset.subcat === subcat
      );
      if (exists) {
        alert(`You already added an item from "${subcat}"`);
        return;
      }

      // Create list item
      const li = document.createElement("li");
      li.dataset.subcat = subcat;

      // Item text
      const text = document.createElement("span");
      text.classList.add("item-text");
      text.textContent = size ? `${name} - ${size}` : name;

      // Remove button
      const removeBtn = document.createElement("button");
      removeBtn.textContent = "Remove";
      removeBtn.classList.add("remove-btn");
      removeBtn.addEventListener("click", () => li.remove());

      li.appendChild(text);
      li.appendChild(removeBtn);
      itemList.appendChild(li);
    });
  });

  /* FORM SUBMIT: ADD HIDDEN INPUTS */
  document.getElementById("preorder-form").addEventListener("submit", function () {
    document.querySelectorAll("input[name='items[]']").forEach(i => i.remove());

    [...itemList.children].forEach(li => {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "items[]";
      input.value = li.querySelector(".item-text").textContent;
      this.appendChild(input);
    });
  });

});


