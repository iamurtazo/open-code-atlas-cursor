// ===== Courses Dropdown & Hamburger =====
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
    if (!dropdownMenu) return;
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


// ===== Auth Modals =====
(function () {
  "use strict";

  const signupModal = document.getElementById("signupModal");
  const loginModal = document.getElementById("loginModal");

  // Guard: modals don't exist when user is logged in
  if (!signupModal || !loginModal) return;

  // Buttons
  const openSignupBtn = document.getElementById("openSignupModal");
  const openLoginBtn = document.getElementById("openLoginModal");
  const closeSignupBtn = document.getElementById("closeSignupModal");
  const closeLoginBtn = document.getElementById("closeLoginModal");
  const switchToLogin = document.getElementById("switchToLogin");
  const switchToSignup = document.getElementById("switchToSignup");

  // Forms & errors
  const signupForm = document.getElementById("signupForm");
  const loginForm = document.getElementById("loginForm");
  const signupError = document.getElementById("signupError");
  const loginError = document.getElementById("loginError");

  // ── Helpers ──

  function openModal(modal) {
    closeAllModals();
    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  }

  function closeModal(modal) {
    modal.classList.remove("show");
    document.body.style.overflow = "";
  }

  function closeAllModals() {
    closeModal(signupModal);
    closeModal(loginModal);
    hideError(signupError);
    hideError(loginError);
  }

  function showError(el, message) {
    el.textContent = message;
    el.classList.add("show");
  }

  function hideError(el) {
    el.textContent = "";
    el.classList.remove("show");
  }

  // ── Open / Close listeners ──

  openSignupBtn.addEventListener("click", function () {
    openModal(signupModal);
  });

  openLoginBtn.addEventListener("click", function () {
    openModal(loginModal);
  });

  closeSignupBtn.addEventListener("click", function () {
    closeAllModals();
  });

  closeLoginBtn.addEventListener("click", function () {
    closeAllModals();
  });

  // ── Switch between modals ──

  switchToLogin.addEventListener("click", function (e) {
    e.preventDefault();
    openModal(loginModal);
  });

  switchToSignup.addEventListener("click", function (e) {
    e.preventDefault();
    openModal(signupModal);
  });

  // ── Close on overlay click ──

  signupModal.addEventListener("click", function (e) {
    if (e.target === signupModal) closeAllModals();
  });

  loginModal.addEventListener("click", function (e) {
    if (e.target === loginModal) closeAllModals();
  });

  // ── Close on Escape ──

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeAllModals();
  });

  // ── Signup form submission ──

  signupForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    hideError(signupError);

    const formData = new FormData(signupForm);

    try {
      const response = await fetch("/signup", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        window.location.reload();
      } else {
        const data = await response.json();
        showError(signupError, data.detail || "Signup failed. Please try again.");
      }
    } catch (err) {
      showError(signupError, "Network error. Please try again.");
    }
  });

  // ── Login form submission ──

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    hideError(loginError);

    const formData = new FormData(loginForm);

    try {
      const response = await fetch("/login", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        window.location.reload();
      } else {
        const data = await response.json();
        showError(loginError, data.detail || "Login failed. Please try again.");
      }
    } catch (err) {
      showError(loginError, "Network error. Please try again.");
    }
  });
})();
