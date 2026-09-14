document.addEventListener("DOMContentLoaded", () => {
  const resultsPage = document.querySelector(".results-page");
  // FIX: Look for the actual class you are using!
  const fetchedWrapper = document.querySelector(
    ".results-page__fetched-wrapper",
  );

  const toggleResultsState = () => {
    if (!resultsPage || !fetchedWrapper) {
      console.warn("Could not find resultsPage or fetchedWrapper in the DOM.");
      return;
    }

    // Check if the docking results card exists inside the wrapper
    const hasResults =
      fetchedWrapper.querySelector(".docking-results") !== null;

    if (hasResults) {
      resultsPage.classList.add("results-page--has-results");
      console.log("State changed: Results found!"); // Helpful for debugging
    } else {
      resultsPage.classList.remove("results-page--has-results");
      console.log("State changed: No results.");
    }
  };

  // 1. Run instantly on page load
  toggleResultsState();

  // 2. Listen natively for HTMX swaps
  document.body.addEventListener("htmx:afterSwap", () => {
    toggleResultsState();
  });
});
