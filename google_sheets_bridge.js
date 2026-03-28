// google_sheets_bridge.js

const SPREADSHEET_ID = '1LhyUTStUq5Rv4za_OG-Q2VTYuf6myJt-c6B3ExvYhrI';

/**
 * Returns the "Status" sheet, creating it with correct headers if it doesn't exist.
 */
function getSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName('Status');
  if (!sheet) {
    sheet = ss.insertSheet('Status');
    sheet.appendRow(["Sign ID", "Latitude", "Longitude", "Status", "Right Arrow", "Left Arrow", "Fri_Sat", "Details"]);
  }
  return sheet;
}

/**
 * GET: Reads all sign data from the spreadsheet and returns it as a JSON map.
 */
function doGet(e) {
  try {
    const sheet = getSheet();
    const data = sheet.getDataRange().getValues();
    const statusMap = {};

    // Header index mapping:
    // 0: Sign ID, 1: Lat, 2: Lng, 3: Status, 4: Right, 5: Left, 6: Fri_Sat, 7: Details
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const id = row[0];
      if (id) {
        statusMap[id] = {
          id: id,
          status: row[3] || 'need',
          right: parseInt(row[4]) || 0,
          left: parseInt(row[5]) || 0,
          fri_sat: parseInt(row[6]) || 0,
          details: parseInt(row[7]) || 0
        };
      }
    }

    return ContentService.createTextOutput(JSON.stringify(statusMap))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (e) {
    return ContentService.createTextOutput(JSON.stringify({ error: e.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * POST: Receives sign updates from the web app and maps them to the correct spreadsheet columns.
 */
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
      const sign = payload[id];

      // Prepare values, ensuring defaults if fields are missing
      const status = typeof sign === 'string' ? sign : (sign.status || 'need');
      const right = parseInt(sign.right) || 0;
      const left = parseInt(sign.left) || 0;
      const fri_sat = parseInt(sign.fri_sat) || 0;
      const details = parseInt(sign.details) || 0;

      if (rowFound !== undefined) {
        // Update columns 4 through 8 (Status, Right, Left, Fri_Sat, Details)
        // Note: Range is (row, column, numRows, numColumns)
        sheet.getRange(rowFound, 4, 1, 5).setValues([[status, right, left, fri_sat, details]]);
      } else {
        // New sign entry: extract lat/lng from ID if possible
        let lat = "", lng = "";
        if (id.startsWith("sign-")) {
            const parts = id.replace("sign-", "").split("--");
            if (parts.length === 2) {
                lat = parts[0];
                lng = "-" + parts[1].replace(/^-/, "");
            }
        }
        sheet.appendRow([id, lat, lng, status, right, left, fri_sat, details]);
        idToRow[id] = sheet.getLastRow();
      }
    });

    return ContentService.createTextOutput("Success").setMimeType(ContentService.MimeType.TEXT);
  } catch (e) {
    return ContentService.createTextOutput("Error: " + e.toString()).setMimeType(ContentService.MimeType.TEXT);
  }
}