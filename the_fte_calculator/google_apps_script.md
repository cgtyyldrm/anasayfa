// --- KOD BAŞLANGICI ---
function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var result = { titles: [], penalties: [] };
  
  try {
    var titleSheet = ss.getSheetByName("Titles");
    var penaltySheet = ss.getSheetByName("Penalties");
    
    if (titleSheet) {
      var data = titleSheet.getDataRange().getValues();
      // Başlık hariç (satır 1) veriyi al
      for (var i = 1; i < data.length; i++) {
        // Satır dolu mu kontrol et
        if(data[i] && data[i].length > 1) {
          result.titles.push({
            "Ünvan": data[i][0], 
            "Katsayı": data[i][1]
          });
        }
      }
    }
    
    if (penaltySheet) {
      var data = penaltySheet.getDataRange().getValues();
      for (var i = 1; i < data.length; i++) {
        if(data[i] && data[i].length > 1) {
          result.penalties.push({
            "Anahtar Kelime": data[i][0], 
            "Kesinti": data[i][1]
          });
        }
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000); // Çakışmayı önlemek için kilitle
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    
    // Gelen veriyi güvenli şekilde parse et
    var params;
    try {
      params = JSON.parse(e.postData.contents);
    } catch(parseErr) {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error", 
        "message": "JSON Format Hatası: Veri boşluklu veya bozuk gönderildi."
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    var action = params.action || "save";
    
    // Sayfaları Hazırla
    var titleSheet = ss.getSheetByName("Titles");
    if (!titleSheet) { 
      titleSheet = ss.insertSheet("Titles"); 
      titleSheet.appendRow(["Ünvan", "Katsayı"]); // Başlıkları ekle
    }
    
    var penaltySheet = ss.getSheetByName("Penalties");
    if (!penaltySheet) { 
      penaltySheet = ss.insertSheet("Penalties"); 
      penaltySheet.appendRow(["Anahtar Kelime", "Kesinti"]); // Başlıkları ekle
    }
    
    // Kaydetme İşlemi
    if (action === "save") {
      // Önce temizle (başlık hariç temizlemek daha güvenli ama komple temizleyip baştan yazıyoruz)
      titleSheet.clear();
      penaltySheet.clear();
      
      titleSheet.appendRow(["Ünvan", "Katsayı"]);
      penaltySheet.appendRow(["Anahtar Kelime", "Kesinti"]);
      
      // Ünvanları Yaz (Boşluk kontrolü yaparak)
      if (params.titles && params.titles.length > 0) {
        var titleRows = [];
        params.titles.forEach(function(row) {
          // Gelen JSON key'leri ile buradaki stringler BİREBİR aynı olmalı
          var unvan = row["Ünvan"] || row["Unvan"] || "";
          var katsayi = row["Katsayı"] || row["Katsayi"] || 1.0;
          titleRows.push([unvan, katsayi]);
        });
        if(titleRows.length > 0) {
          titleSheet.getRange(2, 1, titleRows.length, 2).setValues(titleRows);
        }
      }
      
      // Kesintileri Yaz (Boşluklu key sorunu burada çözülüyor)
      if (params.penalties && params.penalties.length > 0) {
        var penaltyRows = [];
        params.penalties.forEach(function(row) {
          // Python'dan "Anahtar Kelime" (boşluklu) geliyor, bunu string olarak yakalıyoruz
          var anahtar = row["Anahtar Kelime"] || row["Anahtar_Kelime"] || "";
          var kesinti = row["Kesinti"] || 0.0;
          penaltyRows.push([anahtar, kesinti]);
        });
        if(penaltyRows.length > 0) {
          penaltySheet.getRange(2, 1, penaltyRows.length, 2).setValues(penaltyRows);
        }
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "Veriler işlendi."}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "critical_error", "message": error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
// --- KOD BİTİŞİ ---