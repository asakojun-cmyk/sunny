/* 養成学校の比較ページ — 表はHTMLに書いてあり、ここでは表示のしぼり込みだけを行う
   - 学校:チェックした学校だけ表示(最大3校)。何も選ばなければ全校
   - 項目:チェックしたまとまり(お金・自宅で受けられるか など)だけ表示。何も選ばなければ全項目
   選択は URL(?schools=a,b&items=cost,style)で保持。学校はローカルストレージにも保存 */
(function () {
  "use strict";
  var table = document.querySelector(".cmp");
  var schoolBoxes = document.querySelectorAll("[data-compare-checkbox]");
  var groupBoxes = document.querySelectorAll("[data-compare-group]");
  var status = document.querySelector("[data-compare-status]");
  if (!table || !schoolBoxes.length) return;

  var store = window.kyarikonCompare;
  var MAX = store ? store.MAX : 3;
  var total = schoolBoxes.length;
  var GROUP_NAME = {};
  groupBoxes.forEach(function (cb) {
    var label = cb.parentNode.querySelector("span");
    GROUP_NAME[cb.value] = label ? label.textContent.replace(/[(（].*$/, "") : cb.value;
  });

  function listParam(name) {
    return (new URLSearchParams(location.search).get(name) || "").split(",").filter(function (s) {
      return s;
    });
  }

  function initialSchools() {
    var fromUrl = listParam("schools");
    if (fromUrl.length) return fromUrl.slice(0, MAX);
    return store ? store.getSelection() : [];
  }

  function checked(boxes) {
    var sel = [];
    boxes.forEach(function (c) {
      if (c.checked) sel.push(c.value);
    });
    return sel;
  }

  function persist(schools, groups) {
    if (store) store.setSelection(schools);
    var url = new URL(location.href);
    if (schools.length) url.searchParams.set("schools", schools.join(","));
    else url.searchParams.delete("schools");
    if (groups.length) url.searchParams.set("items", groups.join(","));
    else url.searchParams.delete("items");
    history.replaceState(null, "", url.toString());
  }

  function apply(schools, groups) {
    schoolBoxes.forEach(function (cb) {
      cb.checked = schools.indexOf(cb.value) !== -1;
      cb.disabled = !cb.checked && schools.length >= MAX;
    });
    groupBoxes.forEach(function (cb) {
      cb.checked = groups.indexOf(cb.value) !== -1;
    });

    var allSchools = schools.length === 0;
    table.querySelectorAll("[data-school]").forEach(function (cell) {
      cell.hidden = !allSchools && schools.indexOf(cell.getAttribute("data-school")) === -1;
    });
    var shown = allSchools ? total : schools.length;
    table.querySelectorAll(".cmp__group th").forEach(function (th) {
      th.colSpan = shown + 1;
    });

    var allGroups = groups.length === 0;
    table.querySelectorAll("tbody tr[data-group]").forEach(function (row) {
      var g = row.getAttribute("data-group");
      row.hidden = !allGroups && g !== "date" && groups.indexOf(g) === -1;
    });

    if (status) {
      var parts = [];
      parts.push(allSchools ? total + "校すべて" : shown + "校");
      parts.push(
        allGroups
          ? "すべての項目"
          : groups
              .map(function (g) {
                return "「" + (GROUP_NAME[g] || g) + "」";
              })
              .join("")
      );
      var filtered = !allSchools || !allGroups;
      status.innerHTML =
        parts.join("・") +
        "を表示しています。" +
        (filtered ? ' <button type="button" class="cmp__reset">すべて表示に戻す</button>' : "");
      var reset = status.querySelector(".cmp__reset");
      if (reset) {
        reset.addEventListener("click", function () {
          persist([], []);
          apply([], []);
        });
      }
    }
  }

  function onChange() {
    var schools = checked(schoolBoxes).slice(0, MAX);
    var groups = checked(groupBoxes);
    persist(schools, groups);
    apply(schools, groups);
  }

  schoolBoxes.forEach(function (cb) {
    cb.addEventListener("change", onChange);
  });
  groupBoxes.forEach(function (cb) {
    cb.addEventListener("change", onChange);
  });

  apply(initialSchools(), listParam("items"));
})();
