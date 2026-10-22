(() => {
  const root = document.documentElement;
  const control = document.querySelector(".theme-toggle");
  const label = document.querySelector("[data-theme-label]");
  const media = matchMedia("(prefers-color-scheme: dark)");
  const options = ["system", "light", "dark"];
  let preference = root.dataset.theme || "system";
  const effectiveTheme = () => preference === "system" ? (media.matches ? "dark" : "light") : preference;
  const apply = () => {
    if (preference === "system") delete root.dataset.theme;
    else root.dataset.theme = preference;
    const next = options[(options.indexOf(preference) + 1) % options.length];
    label.textContent = preference[0].toUpperCase() + preference.slice(1);
    control.setAttribute("aria-label", `Color theme: ${label.textContent}. Switch to ${next} mode.`);
    control.hidden = false;
    for (const image of document.querySelectorAll("img[data-themed]")) {
      const source = image.parentElement.querySelector("source");
      const url = `${image.dataset.themed}-${effectiveTheme()}.svg`;
      if (source) source.srcset = url;
      image.src = url;
    }
  };
  control.addEventListener("click", () => {
    preference = options[(options.indexOf(preference) + 1) % options.length];
    try {
      if (preference === "system") localStorage.removeItem("profile-theme");
      else localStorage.setItem("profile-theme", preference);
    } catch {}
    apply();
  });
  media.addEventListener("change", apply);
  window.addEventListener("storage", event => {
    if (event.key !== "profile-theme" && event.key !== null) return;
    preference = options.includes(event.newValue) ? event.newValue : "system";
    apply();
  });
  apply();
})();
