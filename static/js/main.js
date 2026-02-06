// ===== Courses Dropdown =====
(function () {
  "use strict";

  const dropdownToggle = document.querySelector(".dropdown-toggle");
  const dropdownMenu = document.querySelector(".dropdown-menu");
  const hamburger = document.querySelector(".navbar-hamburger");
  const navbarNav = document.querySelector(".navbar-nav");

  // Toggle courses dropdown
  if (dropdownToggle && dropdownMenu) {
    dropdownToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      const isOpen = dropdownMenu.classList.contains("show");

      if (isOpen) {
        closeDropdown();
      } else {
        openDropdown();
      }
    });
  }

  function openDropdown() {
    dropdownMenu.classList.add("show");
    dropdownToggle.classList.add("active");
  }

  function closeDropdown() {
    dropdownMenu.classList.remove("show");
    dropdownToggle.classList.remove("active");
  }

  // Close dropdown when clicking outside
  document.addEventListener("click", function (e) {
    if (
      dropdownMenu &&
      dropdownMenu.classList.contains("show") &&
      !dropdownMenu.contains(e.target) &&
      !dropdownToggle.contains(e.target)
    ) {
      closeDropdown();
    }
  });

  // Close dropdown on Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeDropdown();

      // Also close mobile nav
      if (navbarNav && navbarNav.classList.contains("mobile-open")) {
        navbarNav.classList.remove("mobile-open");
      }
    }
  });

  // Hamburger menu (mobile)
  if (hamburger && navbarNav) {
    hamburger.addEventListener("click", function (e) {
      e.stopPropagation();
      navbarNav.classList.toggle("mobile-open");
    });

    // Close mobile nav when clicking outside
    document.addEventListener("click", function (e) {
      if (
        navbarNav.classList.contains("mobile-open") &&
        !navbarNav.contains(e.target) &&
        !hamburger.contains(e.target)
      ) {
        navbarNav.classList.remove("mobile-open");
      }
    });
  }
})();
