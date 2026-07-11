/* メニュードロワーの開閉 */
(function () {
  "use strict";
  var drawer = document.getElementById("site-drawer");
  if (!drawer) return;
  var toggles = document.querySelectorAll("[data-menu-toggle]");
  function setOpen(open) {
    drawer.hidden = !open;
    toggles.forEach(function (t) {
      t.setAttribute("aria-expanded", open ? "true" : "false");
    });
    if (open) {
      drawer.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }
  toggles.forEach(function (t) {
    t.addEventListener("click", function (e) {
      e.preventDefault();
      setOpen(drawer.hidden);
    });
  });
})();
