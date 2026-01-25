document.addEventListener("DOMContentLoaded", () => {
  // Select all headers, both categories and subcategories
  const headers = document.querySelectorAll(".category-header, .subcategory-header");

  headers.forEach(header => {
    header.addEventListener("click", () => {
      // Find the closest container with category/subcategory class
      const container = header.closest(".category, .subcategory");
      container.classList.toggle("open");

      // Change the + / − sign
      const toggle = header.querySelector(".toggle");
      toggle.textContent = container.classList.contains("open") ? "−" : "+";
    });
  });
});
