/* トップの「卒業生の声」の設定(ここだけ書きかえればよい)
   sheetCsvUrl : スプレッドシートの「ウェブに公開」で出したCSVのURL(…/pub?gid=…&single=true&output=csv)
   formUrl     : 卒業生が声を送るGoogleフォームのURL(…/viewform)
   どちらも空のあいだは、トップに何も出ない。
   formUrl だけ入れると、「あなたの声を聞かせてください」の入口だけが出る。
   作り方は picnic-docs の「卒業生の声_フォームとシートの作り方.md」 */
window.KOE_CONFIG = {
  sheetCsvUrl: "",
  formUrl: ""
};
