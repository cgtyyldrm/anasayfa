// --- Code.gs ---

function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  // Verileri olduğu gibi (metin formatında) çekiyoruz
  var data = sheet.getDataRange().getDisplayValues();
  
  if (data.length === 0) {
    return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
  }

  var headers = data[0];
  var rows = data.slice(1);
  
  var result = rows.map(function(row, rowIndex) {
    var obj = {};
    headers.forEach(function(header, i) {
      obj[header] = row[i] || "";
    });
    // Satır indeksini ekle (Python tarafında silme/düzenleme için kritik)
    obj["rowIndex"] = rowIndex; 
    return obj;
  });
  
  return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var params;
  
  try {
    params = JSON.parse(e.postData.contents);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Invalid JSON"})).setMimeType(ContentService.MimeType.JSON);
  }

  var action = params.action;
  var lock = LockService.getScriptLock();
  
  // Çakışmaları önlemek için kilitleme
  if (lock.tryLock(10000)) {
    try {
      
      // 1. GÖREV EKLEME
      if (action === "add") {
        sheet.appendRow([
          params.tarih, 
          params.kullanici, 
          params.ders, 
          params.konu, 
          params.durum, 
          params.notlar,
          "", // Baslangic
          0,  // Sure
          0   // SoruSayisi
        ]);
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Added"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 2. GÖREV SİLME
      else if (action === "delete") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2; // Başlık satırı nedeniyle +2
        
        sheet.deleteRow(sheetRow);
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Deleted"})).setMimeType(ContentService.MimeType.JSON);
      }

      // 3. GÖREV DÜZENLEME (TARİH EKLENDİ)
      else if (action === "edit") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2;
        
        // --- DEĞİŞİKLİK BURADA ---
        // 1. Sütun -> Tarih (Bunu ekledik)
        sheet.getRange(sheetRow, 1).setValue(params.tarih);

        // 3. Sütun -> Ders
        sheet.getRange(sheetRow, 3).setValue(params.ders);
        // 4. Sütun -> Konu
        sheet.getRange(sheetRow, 4).setValue(params.konu);
        // 6. Sütun -> Notlar
        sheet.getRange(sheetRow, 6).setValue(params.notlar);
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Edited"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 4. BAŞLATMA / TAMAMLAMA / GÜNCELLEME
      else if (action === "complete") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2;
        
        if (params.durum) sheet.getRange(sheetRow, 5).setValue(params.durum);
        if (params.sure !== undefined) sheet.getRange(sheetRow, 8).setValue(params.sure);
        if (params.soru_sayisi !== undefined) sheet.getRange(sheetRow, 9).setValue(params.soru_sayisi);
        
        // Eğer durum "Çalışılıyor" ise başlangıç zamanını at (Log amaçlı)
        if (params.durum === "Çalışılıyor") {
            sheet.getRange(sheetRow, 7).setValue(new Date().toISOString());
        }
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Updated"})).setMimeType(ContentService.MimeType.JSON);
      }
      
    } catch (e) {
       return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": e.toString()})).setMimeType(ContentService.MimeType.JSON);
    } finally {
      lock.releaseLock();
    }
  } else {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Busy"})).setMimeType(ContentService.MimeType.JSON);
  }
}