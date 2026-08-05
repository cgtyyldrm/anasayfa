// --- Code.gs (Doğru/Yanlış & LGS Denemeleri Destekli) ---

function getLgsSheet(ss) {
  var sheet = ss.getSheetByName("LGS_Denemeler");
  if (!sheet) {
    sheet = ss.insertSheet("LGS_Denemeler");
    sheet.appendRow([
      "id", "ogrenci", "deneme_adi", "yayin", "tarih", 
      "sure_dk", "zorluk", "notlar", "toplam_net", "lgs_puani", 
      "dersler_json", "created_at"
    ]);
  }
  return sheet;
}

function parseJsonSafe(str) {
  if (!str) return {};
  if (typeof str === "object") return str;
  try {
    return JSON.parse(str);
  } catch (e) {
    return {};
  }
}

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // --- 1. LGS DENEMELERİ GET İSTEĞİ (?type=lgs veya ?sheet=lgs) ---
  if (e && e.parameter && (e.parameter.type === "lgs" || e.parameter.sheet === "lgs")) {
    var lgsSheet = getLgsSheet(ss);
    var data = lgsSheet.getDataRange().getDisplayValues();
    
    if (data.length <= 1) {
      return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
    }
    
    var rows = data.slice(1);
    var result = rows.map(function(row) {
      return {
        "id": row[0] || "",
        "ogrenci": row[1] || "",
        "deneme_adi": row[2] || "",
        "yayin": row[3] || "",
        "tarih": row[4] || "",
        "sure_dk": parseFloat(row[5]) || 0,
        "zorluk": row[6] || "Orta",
        "notlar": row[7] || "",
        "toplam_net": parseFloat(row[8]) || 0,
        "lgs_puani": parseFloat(row[9]) || 0,
        "dersler": parseJsonSafe(row[10]),
        "created_at": row[11] || ""
      };
    });
    
    return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
  }

  // --- 2. VARSAYILAN GÜNLÜK GÖREVLER / ÇALIŞMALAR GET İSTEĞİ ---
  var sheet = ss.getActiveSheet();
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
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var params;
  
  try {
    params = JSON.parse(e.postData.contents);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Invalid JSON"})).setMimeType(ContentService.MimeType.JSON);
  }

  var action = params.action;
  var lock = LockService.getScriptLock();
  
  if (lock.tryLock(15000)) {
    try {
      
      // ==========================================
      // --- LGS DENEMELERİ AKSİYONLARI ---
      // ==========================================
      
      // A. LGS DENEME EKLEME
      if (action === "add_lgs") {
        var lgsSheet = getLgsSheet(ss);
        var derslerStr = typeof params.dersler === "string" ? params.dersler : JSON.stringify(params.dersler || {});
        
        lgsSheet.appendRow([
          params.id || "",
          params.ogrenci || "",
          params.deneme_adi || "",
          params.yayin || "",
          params.tarih || "",
          params.sure_dk || 0,
          params.zorluk || "Orta",
          params.notlar || "",
          params.toplam_net || 0,
          params.lgs_puani || 0,
          derslerStr,
          params.created_at || new Date().toISOString()
        ]);
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "LGS exam added"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // B. LGS DENEME SİLME (id'ye göre)
      else if (action === "delete_lgs") {
        var lgsSheet = getLgsSheet(ss);
        var data = lgsSheet.getDataRange().getValues();
        var targetId = params.id;
        var deleted = false;
        
        for (var i = 1; i < data.length; i++) {
          if (String(data[i][0]) === String(targetId)) {
            lgsSheet.deleteRow(i + 1);
            deleted = true;
            break;
          }
        }
        
        return ContentService.createTextOutput(JSON.stringify({
          "status": deleted ? "success" : "not_found", 
          "message": deleted ? "LGS exam deleted" : "Exam ID not found"
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      // C. LGS TÜM DENEMELERİ TOPLU SENKRONİZE ETME / AKTARMA
      else if (action === "sync_all_lgs") {
        var lgsSheet = getLgsSheet(ss);
        var lastRow = lgsSheet.getLastRow();
        if (lastRow > 1) {
          lgsSheet.deleteRows(2, lastRow - 1);
        }
        
        var exams = params.exams || [];
        for (var k = 0; k < exams.length; k++) {
          var item = exams[k];
          var derslerStr = typeof item.dersler === "string" ? item.dersler : JSON.stringify(item.dersler || {});
          lgsSheet.appendRow([
            item.id || "",
            item.ogrenci || "",
            item.deneme_adi || "",
            item.yayin || "",
            item.tarih || "",
            item.sure_dk || 0,
            item.zorluk || "Orta",
            item.notlar || "",
            item.toplam_net || 0,
            item.lgs_puani || 0,
            derslerStr,
            item.created_at || new Date().toISOString()
          ]);
        }
        
        return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "All LGS exams synced", "count": exams.length})).setMimeType(ContentService.MimeType.JSON);
      }

      // ==========================================
      // --- VARSAYILAN GÜNLÜK GÖREVLER AKSİYONLARI ---
      // ==========================================
      
      var sheet = ss.getActiveSheet();
      
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