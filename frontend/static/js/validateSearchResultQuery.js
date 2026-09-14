const experimentInput = document.getElementById("experiment-id-field");
const fetchButton = document.getElementById("fetch-results");
const experimentIdRegex = /^DKN-20\d{2}-(0[1-9]|1[0-2])-[A-Za-z0-9_-]{16}$/;
function validateExperimentId() {
  fetchButton.disabled = !experimentIdRegex.test(experimentInput.value);
}
experimentInput.addEventListener("input", validateExperimentId);
validateExperimentId();
