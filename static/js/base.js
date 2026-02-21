// Tiny JS: mobile nav toggle
document
  .getElementById("mobile-menu-button")
  ?.addEventListener("click", function () {
    const m = document.getElementById("mobile-menu");
    if (m) m.classList.toggle("hidden");
  });

// Sidebar collapse toggle (persists in localStorage)
(function () {
  const key = "sidebarCollapsed";
  const toggle = document.getElementById("sidebar-toggle");
  const applyState = (collapsed) => {
    if (collapsed) document.body.classList.add("sidebar-collapsed");
    else document.body.classList.remove("sidebar-collapsed");
    if (toggle) {
      const label = collapsed ? "Expand sidebar" : "Collapse sidebar";
      toggle.setAttribute("aria-pressed", collapsed ? "true" : "false");
      toggle.setAttribute("title", label);
      toggle.setAttribute("aria-label", label);
    }
  };

  // Initialize from storage
  try {
    const stored = localStorage.getItem(key);
    applyState(stored === "true");
  } catch (e) {}

  if (toggle) {
    toggle.addEventListener("click", function () {
      const isCollapsed = document.body.classList.toggle("sidebar-collapsed");
      try {
        localStorage.setItem(key, isCollapsed ? "true" : "false");
      } catch (e) {}
      const label = isCollapsed ? "Expand sidebar" : "Collapse sidebar";
      toggle.setAttribute("aria-pressed", isCollapsed ? "true" : "false");
      toggle.setAttribute("title", label);
      toggle.setAttribute("aria-label", label);
    });
  }
})();
