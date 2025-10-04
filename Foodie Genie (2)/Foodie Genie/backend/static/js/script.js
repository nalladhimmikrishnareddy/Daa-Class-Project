// Runs after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // ==============================
  // INGREDIENTS PAGE PREVIEW CHIPS
  // ==============================
  const input = document.querySelector("input[name='ingredients']");
  const form = document.querySelector("form");
  const previewBox = document.createElement("div");

  if (input && form) {
    previewBox.style.marginTop = "10px";
    previewBox.style.display = "flex";
    previewBox.style.flexWrap = "wrap";
    previewBox.style.gap = "6px";
    input.insertAdjacentElement("afterend", previewBox);

    input.addEventListener("input", () => {
      previewBox.innerHTML = "";
      const items = input.value.split(",").map((s) => s.trim()).filter(Boolean);
      items.forEach((i) => {
        const chip = document.createElement("span");
        chip.textContent = i;
        chip.style.padding = "4px 8px";
        chip.style.background = "rgba(37,99,235,0.1)";
        chip.style.color = "#2563eb";
        chip.style.fontSize = "13px";
        chip.style.borderRadius = "999px";
        previewBox.appendChild(chip);
      });
    });

    // Validation
    form.addEventListener("submit", (e) => {
      const items = input.value.split(",").map((s) => s.trim()).filter(Boolean);
      if (items.length === 0) {
        e.preventDefault();
        alert("⚠️ Please enter at least one ingredient.");
        input.style.border = "2px solid red";
        setTimeout(() => (input.style.border = ""), 1500);
      }
    });
  }

  // ==============================
  // FADE-IN ANIMATION FOR RECIPES
  // ==============================
  const recipes = document.querySelectorAll(".recipe-card");
  recipes.forEach((card, idx) => {
    card.style.opacity = 0;
    card.style.transform = "translateY(10px)";
    card.style.transition = "all .4s ease";
    setTimeout(() => {
      card.style.opacity = 1;
      card.style.transform = "translateY(0)";
    }, 120 * idx);
  });

  // ==============================
  // FILTERS LOGIC (recipes.html)
  // ==============================
  const filterCheckboxes = document.querySelectorAll(".sidebar input[type=checkbox]");
  if (filterCheckboxes.length) {
    const params = new URLSearchParams(window.location.search);

    // Auto-check based on URL params
    filterCheckboxes.forEach((cb) => {
      const values = (params.get(cb.name) || "").split(",");
      if (values.includes(cb.value)) {
        cb.checked = true;
      }
    });

    // On change → rebuild URL with selected filters
    filterCheckboxes.forEach((cb) => {
      cb.addEventListener("change", () => {
        const newParams = new URLSearchParams();

        // Preserve old params like "page"
        for (const [key, val] of params.entries()) {
          if (!["cuisine", "diet", "time"].includes(key)) {
            newParams.set(key, val);
          }
        }

        // Collect selected per filter group
        ["cuisine", "diet", "time"].forEach((group) => {
          const selected = Array.from(document.querySelectorAll(`input[name='${group}']:checked`))
            .map(el => el.value);
          if (selected.length) newParams.set(group, selected.join(","));
        });

        // Reload with new filters
        window.location.search = newParams.toString();
      });
    });
  }
});
