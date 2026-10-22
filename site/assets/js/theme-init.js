(() => {
  try {
    const theme = localStorage.getItem("profile-theme");
    if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
  } catch {}
})();
