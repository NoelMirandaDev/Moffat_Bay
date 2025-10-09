document.addEventListener("DOMContentLoaded", () => {
  const btn  = document.getElementById("accountMenuButton");
  const menu = document.getElementById("accountMenuList");

  if (!btn || !menu) return;

  function openMenu() {
    menu.classList.add("show");
    btn.setAttribute("aria-expanded", "true");
  }

  function closeMenu() {
    menu.classList.remove("show");
    btn.setAttribute("aria-expanded", "false");
  }

  function toggleMenu() {
    if (menu.classList.contains("show")) closeMenu();
    else openMenu();
  }

  // Toggle on avatar click
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  // Close on click outside
  document.addEventListener("click", (e) => {
    if (!menu.contains(e.target) && e.target !== btn) {
      closeMenu();
    }
  });

  // Close on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu();
  });
});