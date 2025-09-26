document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".slideshow").forEach((slideshow) => {
    const slides = slideshow.querySelectorAll(".slide");
    let index = 0;

    setInterval(() => {
      slides[index].classList.remove("active");
      index = (index + 1) % slides.length;
      slides[index].classList.add("active");
    }, 2000); // change every 2s
  });
});
