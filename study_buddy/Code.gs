function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  // Tüm veriyi string olarak alıyoruz (Format bozulmaması için)
  var data = sheet.getDataRange().getDisplayValues();
  
  if (data.length === 0) {
    return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
  }

  var headers = data[0];
  var rows = data.slice(1);
  
  var result = rows.map(function(row, rowIndex) {
    var obj = {};
    headers.forEach(function(header, i) {
      obj[header] = row[i];
      if (obj[header] === undefined) obj[header] = "";
    });
    // Satır indeksini de gönderelim ki Python tarafı hangi satırı güncelleyeceğini bilsin
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
      
      // --- 1. YENİ GÖREV EKLEME ---
      if (action === "add") {
        // Artık 9 Sütunumuz var: 
        // Tarih, Kullanıcı, Ders, Konu, Durum, Notlar, Baslangic, Sure, SoruSayisi
        sheet.appendRow([
          params.tarih, 
          params.kullanici, 
          params.ders, 
          params.konu, 
          params.durum, 
          params.notlar,
          "", // Baslangic (Boş)
          0,  // Sure (0)
          0   // SoruSayisi (0) -> BURASI YENİ EKLENDİ
        ]);
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Added"})).setMimeType(ContentService.MimeType.JSON);
        
      // --- 2. GÖREVE BAŞLAMA ---
      } else if (action === "start") {
        var rowIndex = parseInt(params.rowIndex); 
        var sheetRow = rowIndex + 2; // Başlık satırı + 0 index düzeltmesi
        
        // 5. Sütun (Durum) -> "Çalışılıyor"
        sheet.getRange(sheetRow, 5).setValue("Çalışılıyor");
        
        // 7. Sütun (Baslangic) -> Şimdiki Zaman
        var now = new Date();
        sheet.getRange(sheetRow, 7).setValue(now.toISOString());
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Started"})).setMimeType(ContentService.MimeType.JSON);

      // --- 3. GÜNCELLEME / TAMAMLAMA / MOLA ---
      } else if (action === "complete") {
        var rowIndex = parseInt(params.rowIndex); 
        var sheetRow = rowIndex + 2; 
        
        // 5. Sütun (Durum) -> Python'dan ne gelirse o ("Tamamlandı" veya "Beklemede")
        if (params.durum) {
          sheet.getRange(sheetRow, 5).setValue(params.durum);
        }
        
        // 8. Sütun (Sure) -> Saniye cinsinden günceller
        if (params.sure !== undefined) {
          sheet.getRange(sheetRow, 8).setValue(params.sure);
        }

        // 9. Sütun (SoruSayisi) -> BURASI YENİ EKLENDİ
        if (params.soru_sayisi !== undefined) {
          sheet.getRange(sheetRow, 9).setValue(params.soru_sayisi);
        }
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Updated"})).setMimeType(ContentService.MimeType.JSON);
      }
      
    } catch (e) {
       return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": e.toString()})).setMimeType(ContentService.MimeType.JSON);
    } finally {
      lock.releaseLock();
    }
  } else {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Server busy"})).setMimeType(ContentService.MimeType.JSON);
  }
}