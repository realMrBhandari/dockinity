// ============================================================
// CONFIGURATION
// ============================================================
const LIGAND_FETCH_URL = "/mol-dock/request/ligand-info";
const LIGAND_PLACEHOLDERS = ["2737368", "2214", "164648", "5280343"];

// ============================================================
// LIGAND INPUT CONTROLLER
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("input-ligands-container");
  const addButton = document.getElementById("add_more_field");

  if (!container || !addButton) return;

  const MAX_LIGANDS = 5;
  let totalFields =
    container.querySelectorAll(".docking-request__form-ligand-row").length + 1;
  let ligandCounter = totalFields;

  function updateAddButtonState() {
    if (totalFields >= MAX_LIGANDS) {
      addButton.style.display = "none";
    } else {
      addButton.style.display = "flex";
    }
  }

  addButton.addEventListener("click", () => {
    if (totalFields >= MAX_LIGANDS) return;

    const placeholderIndex = totalFields - 1;
    const assignedPlaceholder = LIGAND_PLACEHOLDERS[placeholderIndex] || "2244";

    ligandCounter++;
    totalFields++;

    // 1. CREATE ROW WRAPPER
    const rowWrapper = document.createElement("div");
    rowWrapper.className = "docking-request__form-ligand-row";

    // 2. CREATE INPUT
    const newInput = document.createElement("input");
    newInput.type = "number";
    newInput.name = "ligand_cid";
    newInput.id = `ligand-input-${ligandCounter}`;
    newInput.min = "1";
    newInput.placeholder = `e.g. ${assignedPlaceholder}`;
    newInput.required = true;
    newInput.autocomplete = "off";
    newInput.className =
      "docking-request__form-input docking-request__form-input-ligand";

    // Attach HTMX Attributes safely via setAttribute
    newInput.setAttribute("hx-post", LIGAND_FETCH_URL);
    newInput.setAttribute("hx-trigger", "input changed delay:700ms");
    newInput.setAttribute("hx-target", `#card-container-${ligandCounter}`);
    newInput.setAttribute("hx-swap", "innerHTML");
    newInput.setAttribute(
      "hx-vals",
      JSON.stringify({ lig_input_number: ligandCounter }),
    );

    // 3. CREATE INLINE REMOVE BUTTON (DOM Element creation avoids template literal string parse errors)
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "docking-request__form-ligand-remove";

    const svgIcon = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "svg",
    );
    svgIcon.setAttribute("class", "docking-request__form-ligand-remove-icon");
    svgIcon.setAttribute("width", "20");
    svgIcon.setAttribute("height", "20");
    svgIcon.setAttribute("fill", "currentColor");
    svgIcon.setAttribute("viewBox", "0 0 256 256");

    const pathElement = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path",
    );
    pathElement.setAttribute(
      "d",
      "M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM96,40h64v8H96Zm96,168H64V64H192ZM112,104v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm48,0v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Z",
    );

    svgIcon.appendChild(pathElement);
    removeBtn.appendChild(svgIcon);

    // 4. ASSEMBLE AND APPEND
    rowWrapper.appendChild(newInput);
    rowWrapper.appendChild(removeBtn);
    container.appendChild(rowWrapper);

    // Explicitly initialize HTMX for the new element
    if (typeof htmx !== "undefined") {
      htmx.process(newInput);
    }

    updateAddButtonState();
  });

  // REMOVE LIGAND INPUT (Event Delegation)
  container.addEventListener("click", (event) => {
    const removeBtn = event.target.closest(
      ".docking-request__form-ligand-remove",
    );
    if (!removeBtn) return;

    const rowWrapper = removeBtn.closest(".docking-request__form-ligand-row");
    if (!rowWrapper) return;

    const input = rowWrapper.querySelector(
      ".docking-request__form-input-ligand",
    );
    if (input) {
      const inputIdNum = input.id.replace("ligand-input-", "");
      const correspondingCard = document.getElementById(
        `ligand-card-${inputIdNum}`,
      );
      if (correspondingCard) {
        correspondingCard.remove();
      }
    }

    rowWrapper.remove();
    totalFields--;
    updateAddButtonState();
  });

  updateAddButtonState();
});
