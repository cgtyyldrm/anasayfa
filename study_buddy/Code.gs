// --- Code.gs (Doğru/Yanlış Destekli) ---

function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
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
  
  if (lock.tryLock(10000)) {
    try {
      
      // 1. EKLEME (Sütun sırasına dikkat: Sure, Dogru, Yanlis, Bos, Toplam)
      if (action === "add") {
        sheet.appendRow([
          params.tarih, 
          params.kullanici, 
          params.ders, 
          params.konu, 
          params.durum, 
          params.notlar,
          "", // Baslangic
          params.sure || 0,  // Sure
          params.dogru || 0,  // Dogru
          params.yanlis || 0,  // Yanlis
          params.bos || 0,  // Bos
          params.toplam || 0   // Toplam
        ]);
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Added"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 2. SİLME
      else if (action === "delete") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2; 
        sheet.deleteRow(sheetRow);
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Deleted"})).setMimeType(ContentService.MimeType.JSON);
      }

      // 3. DÜZENLEME (Tarih, Ders, Konu)
      else if (action === "edit") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2;
        
        sheet.getRange(sheetRow, 1).setValue(params.tarih);
        sheet.getRange(sheetRow, 3).setValue(params.ders);
        sheet.getRange(sheetRow, 4).setValue(params.konu);
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Edited"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 4. TAMAMLAMA / İLERLEME GÜNCELLEME (Doğru/Yanlış Eklendi)
      else if (action === "complete") {
        var rowIndex = parseInt(params.rowIndex);
        var sheetRow = rowIndex + 2;
        
        // Durum
        if (params.durum) sheet.getRange(sheetRow, 5).setValue(params.durum);
        
        // Süre (Sütun 8)
        if (params.sure !== undefined) sheet.getRange(sheetRow, 8).setValue(params.sure);
        
        // Doğru (Sütun 9)
        if (params.dogru !== undefined) sheet.getRange(sheetRow, 9).setValue(params.dogru);
        
        // Yanlış (Sütun 10)
        if (params.yanlis !== undefined) sheet.getRange(sheetRow, 10).setValue(params.yanlis);
        
        // Boş (Sütun 11)
        if (params.bos !== undefined) sheet.getRange(sheetRow, 11).setValue(params.bos);

        // Toplam Hesapla ve Yaz (Sütun 12)
        // Eğer param olarak gelmediyse hücreden oku, ama genelde Python gönderir. 
        // Biz Python'dan toplamı göndereceğiz garanti olsun.
        if (params.toplam !== undefined) sheet.getRange(sheetRow, 12).setValue(params.toplam);
        
        // Başlangıç Zamanı Logla
        if (params.durum === "Çalışılıyor") {
            var cell = sheet.getRange(sheetRow, 7);
            if(cell.getValue() === "") cell.setValue(new Date().toISOString());
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