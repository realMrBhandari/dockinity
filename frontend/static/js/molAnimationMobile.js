document.addEventListener("DOMContentLoaded", function () {
  if (window.matchMedia("(max-width: 480px)").matches) {
    setTimeout(() => {
      let viewer = $3Dmol.viewers["dockinity-molecule"];

      if (viewer) {
        viewer.zoom(0.85);
        viewer.render();
      }
    }, 500);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const molecule = document.getElementById("dockinity-molecule");

  if (!molecule) return;

  function preventScroll(event) {
    event.preventDefault();
  }

  molecule.addEventListener("touchmove", preventScroll, {
    passive: false,
  });

  molecule.addEventListener("wheel", preventScroll, {
    passive: false,
  });
});
