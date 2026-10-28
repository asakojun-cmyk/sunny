// 赤シート対応の印刷ボタン。押すと .rs-sheet だけを印刷する(しくみは css/red-sheet.css)
(function(){
  var root=document.documentElement;
  document.addEventListener("click",function(e){
    var b=e.target.closest&&e.target.closest("[data-rs-print]");
    if(!b)return;
    root.classList.add("rs-printing");
    window.print();
  });
  window.addEventListener("afterprint",function(){root.classList.remove("rs-printing")});
})();
