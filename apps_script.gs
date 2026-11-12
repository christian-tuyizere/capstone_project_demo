// The chatbot's log: paste this into your Google Sheet (Extensions, Apps Script), save, then
// Deploy, New deployment, type Web app, Execute as: Me, Who has access: Anyone.
// The Web app URL that Google shows is the LOG_URL secret of the chatbot. Keep it private:
// anyone who has it can add rows to this Sheet.
const COLUMNS = ["time", "user", "turn", "message", "intent", "confidence", "answered_by",
                 "reply", "feedback"];

function safe(value) {
  // A message that starts with = + or @ would become a formula. Store it as text.
  if (typeof value === "string" && /^[=+@-]/.test(value)) return "'" + value;
  return value === undefined ? "" : value;
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);              // two visitors at the same moment: one row at a time
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) sheet.appendRow(COLUMNS);
    const row = JSON.parse(e.postData.contents);
    sheet.appendRow(COLUMNS.map(function (c) { return safe(row[c]); }));
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput("ok");
}
