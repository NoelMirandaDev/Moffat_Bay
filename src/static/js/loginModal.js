document.addEventListener("DOMContentLoaded", () => {
  const loginModal = document.getElementById("loginModal");
  const loginBtn = document.getElementById("loginBtn");
  const closeTriggers = document.querySelectorAll("[data-close-modal]");

  if (!loginModal) return; // No modal on this page

  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      loginModal.classList.add("show");
    });
  }

  closeTriggers.forEach(el => {
    el.addEventListener("click", () => {
      loginModal.classList.remove("show");
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      loginModal.classList.remove("show");
    }
  });
});