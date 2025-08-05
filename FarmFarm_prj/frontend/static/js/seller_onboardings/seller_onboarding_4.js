document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("benefitModal");
    const btn = document.getElementById("benefits");
    const closeBtn = modal.querySelector(".close-btn");

    btn.addEventListener("click", () => {
      modal.style.display = "flex";
    });

    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    });
});
