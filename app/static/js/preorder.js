document.addEventListener("DOMContentLoaded", () => {
  const headers = document.querySelectorAll(".category-header");

  headers.forEach(header => {
    header.addEventListener("click", () => {
      const category = header.parentElement;
      category.classList.toggle("open");

      const toggle = header.querySelector(".toggle");
      toggle.textContent = category.classList.contains("open") ? "−" : "+";
    });
  });
});
