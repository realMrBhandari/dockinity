function setupMoleculeInteraction(viewer) {
  const molecule = document.getElementById("dockinity-molecule");

  let resumeTimer;
  let isInteracting = false;

  // 3Dmol spin speed:
  // 0.25 degrees every 25ms = 10 degrees/second
  const spinSpeed = 0.25;

  function startSpinning() {
    viewer.spin("y", spinSpeed);
  }

  function stopSpinning() {
    viewer.spin(false);
  }

  // Prevent mouse wheel from reaching 3Dmol.
  // This disables zooming while preserving normal page scrolling.
  molecule.addEventListener(
    "wheel",
    (event) => {
      event.stopPropagation();
    },
    { capture: true },
  );

  // User starts interacting with the molecule
  molecule.addEventListener("pointerdown", () => {
    isInteracting = true;

    clearTimeout(resumeTimer);
    stopSpinning();
  });

  // User releases the molecule
  window.addEventListener("pointerup", () => {
    if (!isInteracting) return;

    isInteracting = false;

    clearTimeout(resumeTimer);

    // Stay still for 1 second after interaction
    resumeTimer = setTimeout(() => {
      startSpinning();
    }, 1000);
  });

  // Safety fallback
  window.addEventListener("pointercancel", () => {
    if (!isInteracting) return;

    isInteracting = false;

    clearTimeout(resumeTimer);

    resumeTimer = setTimeout(() => {
      startSpinning();
    }, 1000);
  });

  // Start automatic rotation
  startSpinning();
}

// Wait for the embedded 3Dmol viewer to initialize
document.addEventListener("DOMContentLoaded", () => {
  const viewerId = "dockinity-molecule";

  const checkViewer = setInterval(() => {
    if (
      typeof $3Dmol !== "undefined" &&
      $3Dmol.viewers &&
      $3Dmol.viewers[viewerId]
    ) {
      clearInterval(checkViewer);

      const viewer = $3Dmol.viewers[viewerId];

      setupMoleculeInteraction(viewer);
    }
  }, 100);
});
