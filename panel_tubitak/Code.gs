// Code.gs - Google Apps Script Code

function doGet(e) {
  const action = e.parameter.action;
  
  if (action === "verifyLogin") {
    const username = e.parameter.username;
    const password = e.parameter.password;
    
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Users");
    if (!sheet) return ContentService.createTextOutput(JSON.stringify({ success: false, message: "Users sheet not found" })).setMimeType(ContentService.MimeType.JSON);
    
    const data = sheet.getDataRange().getValues();
    // Skip header
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] == username && data[i][1] == password) {
        return ContentService.createTextOutput(JSON.stringify({ 
          success: true, 
          user: { 
            username: data[i][0], 
            role: data[i][2],
            name: data[i][3]
          } 
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({ success: false, message: "Invalid credentials" })).setMimeType(ContentService.MimeType.JSON);
  }
  
  if (action === "getScores") {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Votes");
    if (!sheet) return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
    
    const data = sheet.getDataRange().getValues();
    if (data.length < 2) return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);

    const headers = data.shift(); // Remove headers
    
    const results = data.map(row => {
      // Columns: PanelistId, PanelistName, OzgunDeger, Yontem, ProjeYonetimi, YayginEtki, Timestamp
      return {
        panelistId: row[0],
        panelistName: row[1],
        ozgun_deger: row[2],
        yontem: row[3],
        proje_yonetimi: row[4],
        yaygin_etki: row[5]
      };
    });
    
    return ContentService.createTextOutput(JSON.stringify(results)).setMimeType(ContentService.MimeType.JSON);
  }

  if (action === "getGameState") {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Settings");
    if (!sheet) return ContentService.createTextOutput(JSON.stringify({ activeCriteria: [], resultsPublished: false })).setMimeType(ContentService.MimeType.JSON);
    
    // Structure: Key | Value
    // A1: ActiveCriteria | comma_separated_ids
    // A2: ResultsPublished | true/false
    
    const activeCriteria = sheet.getRange("B1").getValue().toString().split(",").filter(x => x);
    const resultsPublished = sheet.getRange("B2").getValue() === true;
    
    return ContentService.createTextOutput(JSON.stringify({ 
      activeCriteria, 
      resultsPublished 
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  return ContentService.createTextOutput("Invalid Action");
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    if (data.action === "submitVote") {
      let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Votes");
      if (!sheet) {
        sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet("Votes");
        sheet.appendRow(["PanelistId", "PanelistName", "OzgunDeger", "Yontem", "ProjeYonetimi", "YayginEtki", "Timestamp"]);
      }
      
      sheet.appendRow([
        data.panelistId, 
        data.panelistName,
        data.scores.ozgun_deger,
        data.scores.yontem,
        data.scores.proje_yonetimi,
        data.scores.yaygin_etki,
        new Date()
      ]);
      
      return ContentService.createTextOutput(JSON.stringify({ success: true }));
    }

    if (data.action === "updateGameState") {
       let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Settings");
       if (!sheet) {
         setup(); // Try to ensure it exists
         sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Settings");
       }
       
       if (data.activeCriteria !== undefined) {
         sheet.getRange("B1").setValue(data.activeCriteria.join(","));
       }
       
       if (data.resultsPublished !== undefined) {
         sheet.getRange("B2").setValue(data.resultsPublished);
       }
       
       return ContentService.createTextOutput(JSON.stringify({ success: true }));
    }

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ success: false, error: err.toString() }));
  }
}

function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Setup Users Sheet
  let usersSheet = ss.getSheetByName("Users");
  if (!usersSheet) {
    usersSheet = ss.insertSheet("Users");
    usersSheet.appendRow(["Username", "Password", "Role", "Name"]);
    usersSheet.appendRow(["admin", "admin", "admin", "Sistem Yöneticisi"]);
  }
  
  // Add Requested Panelists
  const newUsers = [
    ["vceyhan@omu.edu.tr", "zos2237", "panelist", "V. Ceyhan"],
    ["eselim@omu.edu.tr", "zos2237", "panelist", "E. Selim"],
    ["gerener@omu.edu.tr", "zos2237", "panelist", "G. Erener"]
  ];
  
  const existingUsers = usersSheet.getDataRange().getValues().map(row => row[0]);
  
  newUsers.forEach(user => {
    if (!existingUsers.includes(user[0])) {
      usersSheet.appendRow(user);
    }
  });
  
  // Setup Votes Sheet
  let votesSheet = ss.getSheetByName("Votes");
  if (!votesSheet) {
     votesSheet = ss.insertSheet("Votes");
  }
  votesSheet.getRange("A1:G1").setValues([["PanelistId", "PanelistName", "OzgunDeger", "Yontem", "ProjeYonetimi", "YayginEtki", "Timestamp"]]);

  // Setup Settings Sheet (For Game State)
  let settingsSheet = ss.getSheetByName("Settings");
  if (!settingsSheet) {
    settingsSheet = ss.insertSheet("Settings");
    settingsSheet.getRange("A1").setValue("ActiveCriteria");
    settingsSheet.getRange("B1").setValue(""); // Comma separated list
    settingsSheet.getRange("A2").setValue("ResultsPublished");
    settingsSheet.getRange("B2").setValue(false);
  }
}
