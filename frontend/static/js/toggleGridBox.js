document.addEventListener("DOMContentLoaded", () => {
  // ============================================================
  // CONFIGURATION
  // Change these if Django IDs change.
  // ============================================================

  const BLIND_DOCKING_ID = "id_docking_type_0";
  const SITE_SPECIFIC_DOCKING_ID = "id_docking_type_1";

  const GRID_BOX_ID = "grid-box-wrapper";

  // ============================================================
  // ELEMENTS
  // ============================================================

  const blindDocking = document.getElementById(BLIND_DOCKING_ID);
  const siteSpecificDocking = document.getElementById(SITE_SPECIFIC_DOCKING_ID);

  const gridBox = document.getElementById(GRID_BOX_ID);

  // ============================================================
  // SAFETY CHECK
  // ============================================================

  if (!blindDocking || !siteSpecificDocking || !gridBox) {
    console.error("Docking mode elements could not be found.");
    return;
  }

  // ============================================================
  // GRID BOX INPUTS
  // ============================================================

  const gridInputs = gridBox.querySelectorAll("input");

  // ============================================================
  // DOCKING MODE HANDLER
  // ============================================================

  function updateDockingMode() {
    if (siteSpecificDocking.checked) {
      gridBox.hidden = false;

      gridInputs.forEach((input) => {
        input.disabled = false;
      });
    } else if (blindDocking.checked) {
      gridBox.hidden = true;

      gridInputs.forEach((input) => {
        input.disabled = true;
      });
    }
  }

  // ============================================================
  // LISTEN FOR CHANGES
  // ============================================================

  blindDocking.addEventListener("change", updateDockingMode);
  siteSpecificDocking.addEventListener("change", updateDockingMode);

  // ============================================================
  // INITIAL STATE
  // ============================================================

  updateDockingMode();
});
