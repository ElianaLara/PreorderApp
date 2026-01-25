document.addEventListener("DOMContentLoaded", () => {
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
});

