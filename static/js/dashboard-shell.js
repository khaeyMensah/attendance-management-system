(function () {
  const shell = document.getElementById("dashboard-shell");
  if (!shell) return;

  const profileToggle = document.getElementById("profile-toggle");
  const profileMenu = document.getElementById("profile-menu");
  const searchForm = document.getElementById("dashboard-search-form");
  const searchInput = document.getElementById("dashboard-search");

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
