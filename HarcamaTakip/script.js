// --- AYARLAR ---
// Google Apps Script'ten aldığınız uzun URL'yi buraya yapıştırın:
const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwK9Ps8qQkPrJvkeqAZtKqGRshfW3OQWtdxnXRHWf6DzyozoqtTGXMvLTDHPcQLQei9/exec";


// Durum Yönetimi
const state = {
    currentUser: localStorage.getItem('currentUser') || null,
    transactions: []
};

// İkonlar
const categoryIcons = {
    'food': 'fa-utensils', 'Yemek': 'fa-utensils',
    'transport': 'fa-bus', 'Ulaşım': 'fa-bus',
    'entertainment': 'fa-gamepad', 'Eğlence': 'fa-gamepad',
    'education': 'fa-graduation-cap', 'Eğitim': 'fa-graduation-cap',
    'clothing': 'fa-shirt', 'Giyim': 'fa-shirt',
    'other': 'fa-bag-shopping', 'Diğer': 'fa-bag-shopping',
    'Harçlık': 'fa-wallet'
};
const categoryLabels = { food: 'Yemek', transport: 'Ulaşım', entertainment: 'Eğlence', education: 'Eğitim', clothing: 'Giyim', other: 'Diğer', income: 'Harçlık' };

// --- BAŞLANGIÇ ---
function init() {
    setupEventListeners();
    checkAuth();
    setTodayDates(); // Sayfa açılınca tarihi 'bugün' yap
}

// --- YARDIMCI: TARİHLERİ BUGÜNE AYARLA ---
function setTodayDates() {
    const today = new Date();
    // Yerel saat dilimine göre YYYY-MM-DD formatı oluştur
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const todayStr = `${year}-${month}-${day}`;

    // Harcama ve Gelir tarih kutularını doldur
    if (document.getElementById('date')) document.getElementById('date').value = todayStr;
    if (document.getElementById('income-date')) document.getElementById('income-date').value = todayStr;
}

// --- KİMLİK DOĞRULAMA ---
function checkAuth() {
    if (state.currentUser) {
        showApp();
    } else {
        showLogin();
    }
}

function showApp() {
    document.getElementById('auth-container').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    document.getElementById('user-display').innerText = state.currentUser;
    loadFromGoogle();
}

function showLogin() {
    document.getElementById('app-container').classList.add('hidden');
    document.getElementById('auth-container').classList.remove('hidden');
}

function logout() {
    state.currentUser = null;
    localStorage.removeItem('currentUser');
    state.transactions = [];
    showLogin();
}

async function handleAuth(e) {
    e.preventDefault();
    const btn = document.getElementById('auth-form').querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "Bekleyin...";
    btn.disabled = true;

    const username = document.getElementById('username').value.trim().toLowerCase();
    const password = document.getElementById('password').value;
    const isRegister = document.getElementById('auth-title').innerText === "Kayıt Ol";

    const packet = { tip: isRegister ? "kayit" : "giris", kullanici: username, sifre: password };

    try {
        await fetch(GOOGLE_SCRIPT_URL, {
            method: "POST", mode: "no-cors", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(packet)
        });

        if (isRegister) {
            alert("Kayıt isteği gönderildi. Giriş yapmayı deneyin.");
            toggleAuthMode();
        } else {
            state.currentUser = username;
            localStorage.setItem('currentUser', username);
            showApp();
        }
    } catch (err) { alert("Bağlantı hatası"); }
    finally { btn.innerText = originalText; btn.disabled = false; }
}

function toggleAuthMode() {
    const title = document.getElementById('auth-title');
    const text = document.getElementById('auth-toggle-text');
    const link = document.getElementById('auth-toggle-link');
    const btn = document.getElementById('auth-form').querySelector('button');

    if (title.innerText === "Giriş Yap") {
        title.innerText = "Kayıt Ol"; text.innerText = "Zaten hesabın var mı?"; link.innerText = "Giriş Yap"; btn.innerText = "Kayıt Ol";
    } else {
        title.innerText = "Giriş Yap"; text.innerText = "Hesabın yok mu?"; link.innerText = "Kayıt Ol"; btn.innerText = "Giriş Yap";
    }
}

// --- VERİ İŞLEMLERİ ---
async function loadFromGoogle() {
    const listElement = document.getElementById('expense-list');
    listElement.innerHTML = '<p style="text-align:center; color:#666;">Cüzdan Yükleniyor...</p>';
    const urlWithUser = `${GOOGLE_SCRIPT_URL}?username=${state.currentUser}`;

    try {
        const response = await fetch(urlWithUser);
        const data = await response.json();

        if (data.error) { alert("Oturum hatası."); logout(); return; }

        state.transactions = data.map(item => ({
            id: item.id,
            tarih: item.tarih,
            kategori: item.kategori,
            tutar: parseFloat(item.tutar),
            aciklama: item.aciklama
        }));

        render();
    } catch (error) {
        console.error(error);
        listElement.innerHTML = '<p style="text-align:center; color:red;">Veriler alınamadı.</p>';
    }
}

function saveTransaction(formId, type) {
    const form = document.getElementById(formId);
    const btn = form.querySelector('button[type="submit"]');
    btn.innerText = "İşleniyor...";
    btn.disabled = true;

    let amount, category, date, desc;

    if (type === 'income') {
        amount = document.getElementById('income-amount').value;
        category = 'Harçlık';
        date = document.getElementById('income-date').value;
        desc = document.getElementById('income-description').value;
    } else {
        amount = document.getElementById('amount').value;
        const categoryCode = document.getElementById('category').value;
        category = categoryLabels[categoryCode] || categoryCode;
        date = document.getElementById('date').value;
        desc = document.getElementById('description').value;
    }

    const yeniVeri = {
        tip: "harcama",
        id: Date.now().toString(),
        tarih: date,
        cocukIsmi: state.currentUser,
        kategori: category,
        tutar: amount,
        aciklama: desc,
        aktifKullanici: state.currentUser
    };

    fetch(GOOGLE_SCRIPT_URL, {
        method: "POST", mode: "no-cors", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(yeniVeri)
    }).then(() => {
        state.transactions.unshift({
            id: yeniVeri.id, tarih: yeniVeri.tarih, kategori: yeniVeri.kategori,
            tutar: parseFloat(yeniVeri.tutar), aciklama: yeniVeri.aciklama
        });
        render();
        const modal = form.closest('.modal');
        closeModal(modal);

        form.reset();
        setTodayDates(); // Form temizlendikten sonra tarihi tekrar 'bugün' yap

        alert("✅ İşlem Kaydedildi!");
    }).catch(err => alert("Hata")).finally(() => {
        btn.innerText = type === 'income' ? "Ekle (+)" : "Kaydet (-)";
        btn.disabled = false;
    });
}

function deleteTransaction(id) {
    if (!confirm("Silmek istediğinize emin misiniz?")) return;
    const eskiListe = [...state.transactions];
    state.transactions = state.transactions.filter(t => t.id !== String(id));
    render();

    const silmePaketi = { tip: "sil", id: id, aktifKullanici: state.currentUser };

    fetch(GOOGLE_SCRIPT_URL, {
        method: "POST", mode: "no-cors", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(silmePaketi)
    }).catch(err => {
        state.transactions = eskiListe; render(); alert("Silinemedi.");
    });
}

// --- RENDER (GÖRÜNTÜLEME) ---
function render() {
    // 1. Bakiye Hesaplama
    let totalBalance = 0;
    state.transactions.forEach(t => {
        if (t.kategori === 'Harçlık') totalBalance += t.tutar;
        else totalBalance -= t.tutar;
    });

    const balanceEl = document.getElementById('total-balance');
    const statusEl = document.getElementById('balance-status');

    balanceEl.textContent = formatCurrency(totalBalance);

    if (totalBalance > 0) {
        balanceEl.style.color = '#43D9AD'; // Yeşil
        statusEl.innerText = "Durumun gayet iyi! 🎉";
        statusEl.style.color = "#43D9AD";
    } else if (totalBalance === 0) {
        balanceEl.style.color = '#2D3436';
        statusEl.innerText = "Kasa boş 😐";
        statusEl.style.color = "#999";
    } else {
        balanceEl.style.color = '#FF6584'; // Kırmızı
        statusEl.innerText = "Dikkat! Eksiye düştün. 🚨";
        statusEl.style.color = "#FF6584";
    }

    // 2. Liste
    const listDiv = document.getElementById('expense-list');
    listDiv.innerHTML = '';
    const sortedTrans = [...state.transactions].sort((a, b) => new Date(b.tarih) - new Date(a.tarih));

    if (sortedTrans.length === 0) {
        listDiv.innerHTML = '<div class="empty-state"><p>Henüz işlem yok.</p></div>';
    } else {
        sortedTrans.forEach(tr => {
            const isIncome = tr.kategori === 'Harçlık';
            const icon = categoryIcons[tr.kategori] || 'fa-circle';
            const amountClass = isIncome ? 'color:#43D9AD;' : 'color:#FF6584;';
            const sign = isIncome ? '+' : '-';

            listDiv.innerHTML += `
                <div class="expense-item">
                    <div class="expense-info">
                        <div class="category-icon" style="${isIncome ? 'color:#43D9AD; background:#e0fbf4;' : ''}">
                            <i class="fa-solid ${icon}"></i>
                        </div>
                        <div class="expense-details">
                            <h4>${tr.kategori}</h4>
                            <p>${formatDate(tr.tarih)} ${tr.aciklama ? '- ' + tr.aciklama : ''}</p>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div class="expense-amount" style="${amountClass}">${sign}${formatCurrency(tr.tutar)}</div>
                        <button class="delete-btn" onclick="deleteTransaction('${tr.id}')"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>`;
        });
    }
}

function formatCurrency(num) { return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(num); }
function formatDate(str) { return new Date(str).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long' }); }
function openModal(modal) {
    modal.classList.add('active');
    modal.classList.remove('hidden');
    // Modal her açıldığında tarihi kontrol et, boşsa bugün yap
    setTodayDates();
}
function closeModal(modal) { modal.classList.remove('active'); setTimeout(() => modal.classList.add('hidden'), 300); }

function setupEventListeners() {
    document.getElementById('auth-form').addEventListener('submit', handleAuth);
    document.getElementById('auth-toggle-link').addEventListener('click', (e) => { e.preventDefault(); toggleAuthMode(); });
    document.getElementById('logout-btn').addEventListener('click', logout);

    document.getElementById('add-expense-btn').addEventListener('click', () => openModal(document.getElementById('expense-modal')));
    document.getElementById('add-income-btn').addEventListener('click', () => openModal(document.getElementById('income-modal')));
    document.querySelectorAll('.close-modal').forEach(b => b.addEventListener('click', (e) => closeModal(e.target.closest('.modal'))));

    document.getElementById('expense-form').addEventListener('submit', (e) => { e.preventDefault(); saveTransaction('expense-form', 'expense'); });
    document.getElementById('income-form').addEventListener('submit', (e) => { e.preventDefault(); saveTransaction('income-form', 'income'); });
}

window.deleteTransaction = deleteTransaction;
init();