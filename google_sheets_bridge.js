// google_sheets_bridge.js

const SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI';

function getSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName('Status');
  if (!sheet) {
    sheet = ss.insertSheet('Status');
    sheet.appendRow(['ID', 'Status']);
  }
  return sheet;
}

function doGet(e) {
  try {
    const sheet = getSheet();
    const data = sheet.getDataRange().getValues();
    const statusMap = {};

    for (let i = 1; i < data.length; i++) {
      if (data[i][0]) {
        let cellData = data[i][1];

        // Try to parse the cell value back into a JSON object
        try {
          // If the data is valid JSON, this will convert it to an object
          cellData = JSON.parse(cellData);
        } catch (parseError) {
          // If it fails (e.g., legacy string data like "retrieved"), it safely remains a string
        }

        statusMap[data[i][0]] = cellData;
      }
    }

    return ContentService.createTextOutput(JSON.stringify(statusMap))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (e) {
    return ContentService.createTextOutput(JSON.stringify({ error: e.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    const sheet = getSheet();
    const payload = JSON.parse(e.postData.contents);

    const data = sheet.getDataRange().getValues();
    const idToRow = {};
    for (let i = 1; i < data.length; i++) {
      if (data[i][0]) idToRow[data[i][0]] = i + 1;
    }

    Object.keys(payload).forEach(id => {
      const rowFound = idToRow[id];

      // CRITICAL FIX: Explicitly format as JSON string before pushing to the cell
      const valueToSave = typeof payload[id] === 'object'
        ? JSON.stringify(payload[id])
        : payload[id];

      if (rowFound !== undefined) {
        sheet.getRange(rowFound, 2).setValue(valueToSave);
      } else {
        sheet.appendRow([id, valueToSave]);
        idToRow[id] = sheet.getLastRow();
      }
    });

    return ContentService.createTextOutput("Success").setMimeType(ContentService.MimeType.TEXT);
  } catch (e) {
    return ContentService.createTextOutput("Error: " + e.toString()).setMimeType(ContentService.MimeType.TEXT);
  }
}