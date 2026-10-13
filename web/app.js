"use strict";

(function () {
  const METHODS = ["Unspecified", "Greulich-Pyle", "Tanner-Whitehouse", "Other"];

  function compareBoneAges(chronological, skeletal, method = "Unspecified") {
    for (const [name, value] of [["Chronological age", chronological], ["Reported bone age", skeletal]]) {
      if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 240) {
        throw new RangeError(name + " must be a finite number between 0 and 240 months.");
      }
    }
    if (!METHODS.includes(method)) {
      throw new RangeError("Select a valid assessment method.");
    }
    const delta = Math.round((skeletal - chronological) * 100) / 100;
    return {
      chronological_age_months: Math.round(chronological * 100) / 100,
      bone_age_months: Math.round(skeletal * 100) / 100,
      difference_months: delta,
      direction: delta > 0 ? "advanced" : delta < 0 ? "delayed" : "equal",
      assessment_method: method
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { compareBoneAges };
  }

  if (typeof document === "undefined") return;
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("comparison-form");
    const result = document.getElementById("result");
    const error = document.getElementById("error");
    const exportButton = document.getElementById("export");
    let last = null;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      error.textContent = "";
      result.hidden = true;
      exportButton.disabled = true;
      last = null;
      try {
        const chronological = Number(document.getElementById("chronological").value);
        const skeletal = Number(document.getElementById("skeletal").value);
        const method = document.getElementById("method").value;
        last = compareBoneAges(chronological, skeletal, method);
        document.getElementById("chronological-result").textContent =
          last.chronological_age_months.toFixed(2) + " months";
        document.getElementById("skeletal-result").textContent =
          last.bone_age_months.toFixed(2) + " months";
        const signed = last.difference_months > 0 ? "+" : "";
        document.getElementById("difference-result").textContent =
          signed + last.difference_months.toFixed(2) + " months";
        document.getElementById("direction-result").textContent =
          last.direction === "equal"
            ? "Entered ages are equal."
            : "Entered skeletal age is " + last.direction + " relative to chronological age.";
        result.hidden = false;
        exportButton.disabled = false;
      } catch (e) {
        error.textContent = e.message;
      }
    });

    form.addEventListener("reset", function () {
      result.hidden = true;
      error.textContent = "";
      exportButton.disabled = true;
      last = null;
    });

    exportButton.addEventListener("click", function () {
      if (!last) return;
      const columns = ["chronological_age_months", "bone_age_months",
        "difference_months", "direction", "assessment_method"];
      const csv = columns.join(",") + "\r\n" +
        columns.map(function (key) {
          const value = String(last[key]);
          return '"' + value.replace(/"/g, '""') + '"';
        }).join(",") + "\r\n";
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "bone-age-comparison.csv";
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    });
  });
})();
