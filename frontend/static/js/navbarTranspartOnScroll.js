const navbar = document.querySelector(".navbar");
const toggle = document.querySelector(".navbar__toggle");

// OPEN MENU
function openMenu() {
  navbar.classList.add("is-open");
  document.body.classList.add("nav-is-open"); // Triggers the body push-down CSS

  toggle.setAttribute("aria-expanded", "true");
  toggle.setAttribute("aria-label", "Close navigation");
}

// CLOSE MENU
function closeMenu() {
  navbar.classList.remove("is-open");
  document.body.classList.remove("nav-is-open"); // Pulls the body back up

  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-label", "Open navigation");
}

// TOGGLE MENU
function toggleMenu() {
  const isOpen = navbar.classList.contains("is-open");

  if (isOpen) {
    closeMenu();
  } else {
    openMenu();
  }
}

// TOGGLE BUTTON
toggle.addEventListener("click", toggleMenu);

// CLOSE WHEN CLICKING OUTSIDE
document.addEventListener("click", (event) => {
  if (!navbar.contains(event.target)) {
    closeMenu();
  }
});

// CLOSE WITH ESCAPE
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeMenu();
  }
});

// RESET WHEN RETURNING TO DESKTOP
window.addEventListener("resize", () => {
  if (window.innerWidth > 768) {
    closeMenu();
  }
});

// NAVBAR SCROLL BEHAVIOR
function handleNavbarScroll() {
  if (window.scrollY > 10) {
    navbar.classList.add("navbar--scrolled");
  } else {
    navbar.classList.remove("navbar--scrolled");
  }
}

window.addEventListener("scroll", handleNavbarScroll);

// Run once when the page loads
handleNavbarScroll();
