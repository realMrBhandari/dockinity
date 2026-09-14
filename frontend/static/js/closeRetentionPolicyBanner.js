document.addEventListener("DOMContentLoaded", function () {
  const closeBtn = document.getElementById("close-banner");
  const banner = document.getElementById("info-banner");

  if (closeBtn && banner) {
    closeBtn.addEventListener("click", function () {
      banner.remove();
    });
  }
});
