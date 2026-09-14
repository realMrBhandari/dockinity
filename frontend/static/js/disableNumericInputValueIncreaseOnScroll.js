// Disable mouse wheel changing values on ALL number inputs globally
document.addEventListener(
  "wheel",
  function (event) {
    if (document.activeElement.type === "number") {
      document.activeElement.blur();
    }
  },
  { passive: true },
);
