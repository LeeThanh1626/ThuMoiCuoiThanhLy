// Sheet "LoiChuc" với các cột: thoi_gian | ten | loi_chuc | thu_tu | an | ten_link
// - ten: tên khách nhập trong form (mặc định điền sẵn từ link).
// - ten_link: tên trong link mời (?to=...), để biết lời chúc đến từ link của ai.
// - thu_tu: số nhỏ hiện trước; để trống thì xếp sau, theo thời gian gửi (mới nhất trước).
// - an: tick checkbox (TRUE) để ẩn lời chúc. Mặc định để trống = hiện.
const SHEET_NAME = 'LoiChuc';
const HEADERS = ['thoi_gian', 'ten', 'loi_chuc', 'thu_tu', 'an', 'ten_link'];

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  } else if (sheet.getRange(1, HEADERS.length).getValue() === '') {
    // Sheet tạo từ bản cũ chưa có cột ten_link.
    sheet.getRange(1, HEADERS.length).setValue(HEADERS[HEADERS.length - 1]);
  }
  return sheet;
}

// Chạy một lần trong trình soạn thảo Apps Script để tạo sheet "LoiChuc" với tiêu đề và định dạng cột.
function setup() {
  const sheet = getSheet_();
  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS])
    .setFontWeight('bold').setBackground('#b71c1c').setFontColor('#ffffff');
  sheet.setFrozenRows(1);
  sheet.getRange('A2:A').setNumberFormat('dd/MM/yyyy HH:mm');
  sheet.getRange('C2:C').setWrap(true);
  [140, 160, 420, 70, 50, 160].forEach((w, i) => sheet.setColumnWidth(i + 1, w));
}

function json_(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  const rows = getSheet_().getDataRange().getValues().slice(1);
  const wishes = rows
    .filter((r) => r[2] && r[4] !== true && String(r[4]).toUpperCase() !== 'TRUE')
    .map((r) => ({
      time: new Date(r[0]).getTime() || 0,
      ten: String(r[1]),
      loi_chuc: String(r[2]),
      order: r[3] === '' ? Infinity : Number(r[3]),
    }))
    .sort((a, b) => (a.order - b.order) || (b.time - a.time))
    .map(({ ten, loi_chuc }) => ({ ten, loi_chuc }));
  return json_(wishes);
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    const ten = String(body.ten || '').trim().slice(0, 50);
    const loiChuc = String(body.loi_chuc || '').trim().slice(0, 1000);
    if (ten.length < 2 || !loiChuc) {
      return json_({ ok: false, error: 'invalid' });
    }
    const tenLink = String(body.ten_link || '').trim().slice(0, 100);
    const sheet = getSheet_();
    // Thêm dấu ' phía trước để Sheet không hiểu nội dung là công thức.
    sheet.appendRow([new Date(), "'" + ten, "'" + loiChuc, '', false, tenLink ? "'" + tenLink : '']);
    sheet.getRange(sheet.getLastRow(), 5).insertCheckboxes();
    return json_({ ok: true });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}
