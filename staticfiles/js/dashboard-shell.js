(function () {
  const shell = document.getElementById("dashboard-shell");
  if (!shell) return;

  const profileToggle = document.getElementById("profile-toggle");
  const profileMenu = document.getElementById("profile-menu");
  const sidebarToggle = document.getElementById("sidebar-toggle");
  const sidebarPanel = document.getElementById("dashboard-sidebar-panel");
  const searchForm = document.getElementById("dashboard-search-form");
  const searchInput = document.getElementById("dashboard-search");
  const mobileQuery = window.matchMedia("(max-width: 767px)");

  const isMobileViewport = function () {
    return mobileQuery.matches;
  };

  const setMobileSidebarState = function (open) {
    document.body.classList.toggle("mobile-sidebar-open", open);
    if (sidebarToggle) {
      sidebarToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
  };

  const closeMobileSidebar = function () {
    setMobileSidebarState(false);
  };

  const handleViewportMode = function () {
    if (isMobileViewport()) {
      closeMobileSidebar();
    } else {
      closeMobileSidebar();
    }
  };

  handleViewportMode();
  mobileQuery.addEventListener("change", handleViewportMode);

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      if (!isMobileViewport()) return;
      const isOpen = document.body.classList.contains("mobile-sidebar-open");
      setMobileSidebarState(!isOpen);
    });
  }

  if (profileToggle && profileMenu) {
    const closeMenu = function () {
      profileMenu.classList.add("hidden");
      profileToggle.setAttribute("aria-expanded", "false");
    };

    profileToggle.addEventListener("click", function (event) {
      event.stopPropagation();
      const isHidden = profileMenu.classList.toggle("hidden");
      profileToggle.setAttribute("aria-expanded", isHidden ? "false" : "true");
    });

    document.addEventListener("click", function (event) {
      if (!profileMenu.contains(event.target) && !profileToggle.contains(event.target)) {
        closeMenu();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
  }

  document.addEventListener("click", function (event) {
    if (!isMobileViewport()) return;
    if (!document.body.classList.contains("mobile-sidebar-open")) return;
    if (!sidebarPanel || !sidebarToggle) return;

    const clickedInsideSidebar = sidebarPanel.contains(event.target);
    const clickedToggle = sidebarToggle.contains(event.target);
    if (!clickedInsideSidebar && !clickedToggle) {
      closeMobileSidebar();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeMobileSidebar();
    }
  });

  if (sidebarPanel) {
    sidebarPanel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (isMobileViewport()) {
          closeMobileSidebar();
        }
      });
    });
  }

  if (searchForm && searchInput) {
    searchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      const query = searchInput.value.trim().toLowerCase();
      if (!query) return;

      const role = shell.dataset.role || "";
      const studentDashboardUrl = shell.dataset.studentDashboardUrl || "";
      const lecturerDashboardUrl = shell.dataset.lecturerDashboardUrl || "";
      const adminDashboardUrl = shell.dataset.adminDashboardUrl || "";
      const passwordChangeUrl = shell.dataset.passwordChangeUrl || "";
      const logoutUrl = shell.dataset.logoutUrl || "";

      const dashboardUrl =
        role === "lecturer"
          ? lecturerDashboardUrl
          : role === "admin"
            ? adminDashboardUrl
            : studentDashboardUrl;

      const routes = {
        dashboard: dashboardUrl,
        "scan qr code": studentDashboardUrl ? studentDashboardUrl + "#scan-qr" : "",
        "my attendance": studentDashboardUrl ? studentDashboardUrl + "#attendance" : "",
        courses: lecturerDashboardUrl ? lecturerDashboardUrl + "#courses" : "",
        sessions: lecturerDashboardUrl ? lecturerDashboardUrl + "#sessions" : "",
        reports: lecturerDashboardUrl ? lecturerDashboardUrl + "#attendance-reports" : "",
        profile: dashboardUrl,
        settings: passwordChangeUrl,
        logout: logoutUrl
      };

      if (routes[query]) {
        window.location.href = routes[query];
      }
    });
  }
})();
