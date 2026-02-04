"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { LogOut, Save, RefreshCw } from "lucide-react";
import { getGameState, submitVote, getScores } from "@/lib/api";

// Mock Project Data
const MOCK_PROJECT = {
    id: "5005",
    title: "Fındık Hasat Makinaları İçin Temizleme Ünitesi Geliştirilmesi",
    content: "Bu proje, sensör verilerini kullanarak sulama işlemini optimize etmeyi amaçlamaktadır...",
    presenter: "Araş. Gör. Kübra Meriç UĞURLUTEPE"
};

// Types
type Score = {
    panelistId: string;
    panelistName: string;
    ozgun_deger: number;
    yontem: number;
    proje_yonetimi: number;
    yaygin_etki: number;
};

// Scoring Definitions
const SCORING_DEFINITIONS = [
    { score: 6, label: "İyi", desc: "Proje önerisi ilgili kriteri tüm boyutlarıyla karşılamaktadır. Eksiklik yok denecek kadar azdır." },
    { score: 5, label: "İyi", desc: "Proje önerisi ilgili kriteri iyi derecede karşılamaktadır. Önerinin kabul edilebilir seviyede eksiklikleri bulunmaktadır." },
    { score: 4, label: "Geliştirilebilir", desc: "Proje önerisi ilgili kriteri genel hatlarıyla karşılamakla birlikte, önerinin iyileştirme ve geliştirmeye açık noktaları bulunmaktadır." },
    { score: 3, label: "Geliştirilebilir", desc: "Proje önerisi, ilgili kriteri orta derecede karşılamaktadır. Öneride iyileştirilmesi ve geliştirilmesi gereken önemli hususlar bulunmaktadır." },
    { score: 2, label: "Yetersiz", desc: "Proje önerisi ilgili kriteri yeterli derecede karşılamamaktadır. Öneride önemli eksiklikler bulunmaktadır." },
    { score: 1, label: "Yetersiz", desc: "Proje önerisi ilgili kriteri karşılamamaktadır. Proje önerisinde ciddi eksiklikler/zayıflıklar söz konusudur." },
];

const CRITERIA = [
    { id: "ozgun_deger", label: "Özgün Değer", weight: 35 },
    { id: "yontem", label: "Yöntem", weight: 25 },
    { id: "proje_yonetimi", label: "Proje Yönetimi", weight: 20 },
    { id: "yaygin_etki", label: "Yaygın Etki", weight: 20 },
];

export default function PanelistPage() {
    const { user, logout } = useAuth();
    const [scores, setScores] = useState<Record<string, number>>({
        ozgun_deger: 1,
        yontem: 1,
        proje_yonetimi: 1,
        yaygin_etki: 1
    });
    const [submitted, setSubmitted] = useState(false);

    // Game State
    const [activeCriteria, setActiveCriteria] = useState<string[]>([]);
    const [resultsPublished, setResultsPublished] = useState(false);
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    // Results Data (for when published)
    const [resultData, setResultData] = useState<Score[]>([]);
    const [loadingResults, setLoadingResults] = useState(false);

    // Poll Game State
    useEffect(() => {
        const interval = setInterval(() => {
            setRefreshTrigger(p => p + 1);
        }, 3000); // Poll every 3 seconds
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        getGameState().then(state => {
            setActiveCriteria(state.activeCriteria || []);
            setResultsPublished(state.resultsPublished || false);
        });
    }, [refreshTrigger]);

    // Fetch results when published
    useEffect(() => {
        if (resultsPublished) {
            setLoadingResults(true);
            getScores().then(data => {
                setResultData(data);
                setLoadingResults(false);
            });
        }
    }, [resultsPublished]);

    const handleScoreChange = (criteriaId: string, value: number) => {
        setScores(prev => ({ ...prev, [criteriaId]: value }));
    };

    const handleSubmit = async () => {
        const result = await submitVote(user?.username || "unknown", user?.name || "Panelist", scores);
        if (result.success) {
            setSubmitted(true);
        } else {
            alert("Hata: Puanlar kaydedilemedi.");
        }
    };

    // --- Helper Functions for Results ---
    const calculateAverage = (field: keyof Omit<Score, "panelistId" | "panelistName">) => {
        if (resultData.length === 0) return "0";
        const sum = resultData.reduce((acc, curr) => acc + (curr[field] || 0), 0);
        return (sum / resultData.length).toFixed(1);
    };

    const calculateWeightedScore = (score: Score) => {
        return (
            ((score.ozgun_deger || 0) * 0.35) +
            ((score.yontem || 0) * 0.25) +
            ((score.proje_yonetimi || 0) * 0.20) +
            ((score.yaygin_etki || 0) * 0.20)
        );
    };

    const calculateTotalAverage = () => {
        if (resultData.length === 0) return 0;
        const totalSum = resultData.reduce((acc, curr) => acc + calculateWeightedScore(curr), 0);
        return (totalSum / resultData.length).toFixed(2);
    };

    if (resultsPublished) {
        return (
            <div className="min-h-screen bg-gray-50 pb-10">
                <header className="bg-slate-900 text-white sticky top-0 z-10 shadow-md">
                    <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center text-slate-900 font-bold">S</div>
                            <span className="font-semibold">Değerlendirme Sonuçları</span>
                        </div>
                        <Button variant="destructive" size="sm" onClick={logout}>
                            <LogOut className="h-4 w-4 mr-2" /> Çıkış
                        </Button>
                    </div>
                </header>

                <main className="container mx-auto px-4 mt-8">
                    <Card className="overflow-hidden shadow-lg border-0">
                        <CardHeader className="bg-slate-50 border-b">
                            <CardTitle className="text-xl text-slate-800">Proje Değerlendirme Özeti</CardTitle>
                            <CardDescription>
                                Değerlendirme süreci tamamlanmıştır. Genel sonuçlar aşağıdadır.
                            </CardDescription>
                        </CardHeader>
                        <div className="overflow-x-auto p-0">
                            {loadingResults ? (
                                <div className="p-8 text-center text-slate-500">Sonuçlar yükleniyor...</div>
                            ) : (
                                <table className="w-full text-sm text-center">
                                    <thead className="text-xs uppercase bg-slate-100 text-slate-700 font-bold">
                                        <tr>
                                            <th className="px-6 py-4 text-left">Panelist</th>
                                            <th className="px-6 py-4">Özgün Değer <br /><span className="text-[10px] text-slate-500">(%35)</span></th>
                                            <th className="px-6 py-4">Yöntem <br /><span className="text-[10px] text-slate-500">(%25)</span></th>
                                            <th className="px-6 py-4">Proje Yön. <br /><span className="text-[10px] text-slate-500">(%20)</span></th>
                                            <th className="px-6 py-4">Yaygın Etki <br /><span className="text-[10px] text-slate-500">(%20)</span></th>
                                            <th className="px-6 py-4 bg-slate-200">TOPLAM</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {/* Row for Averages (Highlighted) */}
                                        <tr className="bg-tubitak-red/10 border-b border-tubitak-red/20 font-bold text-tubitak-dark text-base">
                                            <td className="px-6 py-6 text-left">GENEL ORTALAMA</td>
                                            <td className="px-6 py-6">{calculateAverage("ozgun_deger")}</td>
                                            <td className="px-6 py-6">{calculateAverage("yontem")}</td>
                                            <td className="px-6 py-6">{calculateAverage("proje_yonetimi")}</td>
                                            <td className="px-6 py-6">{calculateAverage("yaygin_etki")}</td>
                                            <td className="px-6 py-6 text-tubitak-red text-xl">
                                                {(parseFloat(calculateAverage("ozgun_deger")) +
                                                    parseFloat(calculateAverage("yontem")) +
                                                    parseFloat(calculateAverage("proje_yonetimi")) +
                                                    parseFloat(calculateAverage("yaygin_etki"))).toFixed(1)}
                                            </td>
                                        </tr>
                                        <tr className="bg-tubitak-red/5 border-b border-tubitak-red/10 font-semibold text-tubitak-dark/80 text-sm">
                                            <td className="px-6 py-6 text-left">AĞIRLIKLI ORTALAMA</td>
                                            <td className="px-6 py-6">{(parseFloat(calculateAverage("ozgun_deger")) * 0.35).toFixed(2)}</td>
                                            <td className="px-6 py-6">{(parseFloat(calculateAverage("yontem")) * 0.25).toFixed(2)}</td>
                                            <td className="px-6 py-6">{(parseFloat(calculateAverage("proje_yonetimi")) * 0.20).toFixed(2)}</td>
                                            <td className="px-6 py-6">{(parseFloat(calculateAverage("yaygin_etki")) * 0.20).toFixed(2)}</td>
                                            <td className="px-6 py-6 text-tubitak-red font-bold text-xl">
                                                {((parseFloat(calculateAverage("ozgun_deger")) * 0.35) +
                                                    (parseFloat(calculateAverage("yontem")) * 0.25) +
                                                    (parseFloat(calculateAverage("proje_yonetimi")) * 0.20) +
                                                    (parseFloat(calculateAverage("yaygin_etki")) * 0.20)).toFixed(2)}
                                            </td>
                                        </tr>

                                        {/* Individual Scores (Anonymized) */}
                                        {resultData.map((score, index) => (
                                            <tr key={score.panelistId} className="bg-white border-b hover:bg-slate-50 transition-colors text-slate-500">
                                                <td className="px-6 py-4 font-medium text-left">
                                                    Panelist {index + 1}
                                                </td>
                                                <td className="px-6 py-4">{score.ozgun_deger}</td>
                                                <td className="px-6 py-4">{score.yontem}</td>
                                                <td className="px-6 py-4">{score.proje_yonetimi}</td>
                                                <td className="px-6 py-4">{score.yaygin_etki}</td>
                                                <td className="px-6 py-4"></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </Card>
                </main>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 pb-10">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <img src="/logo.png" alt="Logo" className="h-10 w-auto object-contain" />
                        <span className="font-semibold text-tubitak-dark">Panel Değerlendirme</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-slate-600 hidden md:inline-block">Hoşgeldiniz, {user?.name || "Panelist"}</span>
                        <Button variant="ghost" size="icon" onClick={() => setRefreshTrigger(p => p + 1)} title="Yenile">
                            <RefreshCw className="h-4 w-4 text-slate-400" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={logout} title="Çıkış Yap">
                            <LogOut className="h-5 w-5 text-slate-500" />
                        </Button>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 mt-8 max-w-6xl">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                    {/* Project Info Column */}
                    <div className="lg:col-span-1 space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Proje Bilgileri</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <Label className="text-slate-500 text-xs uppercase">Proje No</Label>
                                    <p className="font-medium">{MOCK_PROJECT.id}</p>
                                </div>
                                <div>
                                    <Label className="text-slate-500 text-xs uppercase">Proje Başlığı</Label>
                                    <p className="font-medium text-sm">{MOCK_PROJECT.title}</p>
                                </div>
                                <div>
                                    <Label className="text-slate-500 text-xs uppercase">Yürütücü</Label>
                                    <p className="font-medium text-sm">{MOCK_PROJECT.presenter}</p>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-blue-50 border-blue-100">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm text-blue-900">Puanlama Rehberi</CardTitle>
                            </CardHeader>
                            <CardContent className="text-xs space-y-2 text-blue-800">
                                {SCORING_DEFINITIONS.map(def => (
                                    <div key={def.score} className="grid grid-cols-12 gap-1 border-b border-blue-100 last:border-0 pb-1">
                                        <span className="col-span-1 font-bold">{def.score}</span>
                                        <div className="col-span-11">
                                            <span className="font-semibold">{def.label}:</span> {def.desc}
                                        </div>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Voting Column */}
                    <div className="lg:col-span-3">
                        <Card className="h-full">
                            <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                    <span>Değerlendirme</span>
                                    {submitted && <span className="text-sm font-normal text-green-600 flex items-center gap-1"><Save className="h-4 w-4" /> Kaydedildi</span>}
                                </CardTitle>
                                <CardDescription>
                                    Lütfen sadece yönetici tarafından açılan kriterleri değerlendiriniz.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-8">
                                {activeCriteria.length === 0 ? (
                                    <div className="text-center py-10 text-slate-500">
                                        <RefreshCw className="h-8 w-8 mx-auto mb-2 animate-spin opacity-20" />
                                        <p>Henüz değerlendirmeye açılan bir kriter yok.</p>
                                        <p className="text-xs mt-1">Lütfen panel yöneticisinin kriterleri açmasını bekleyiniz.</p>
                                    </div>
                                ) : (
                                    CRITERIA.filter(c => activeCriteria.includes(c.id)).map((criterion) => (
                                        <div key={criterion.id} className="space-y-4 p-4 rounded-lg bg-slate-50 border border-slate-100 animate-in fade-in slide-in-from-bottom-4">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <Label className="text-lg font-medium text-slate-800">{criterion.label}</Label>
                                                    <span className="ml-2 text-xs font-semibold text-white bg-slate-400 px-2 py-0.5 rounded-full">%{criterion.weight}</span>
                                                </div>
                                                <span className="text-3xl font-bold text-tubitak-red w-12 text-center">{scores[criterion.id]}</span>
                                            </div>
                                            <div className="grid grid-cols-6 gap-2 py-2">
                                                {[1, 2, 3, 4, 5, 6].map((score) => (
                                                    <Button
                                                        key={score}
                                                        variant={scores[criterion.id] === score ? "default" : "outline"}
                                                        className={`h-12 text-lg font-bold transition-all ${scores[criterion.id] === score
                                                            ? "bg-tubitak-red hover:bg-tubitak-red/90 text-white ring-2 ring-tubitak-red ring-offset-2"
                                                            : "hover:bg-slate-100 text-slate-700 border-slate-200"
                                                            }`}
                                                        onClick={() => handleScoreChange(criterion.id, score)}
                                                        disabled={submitted}
                                                    >
                                                        {score}
                                                    </Button>
                                                ))}
                                            </div>
                                            <div className="flex justify-between text-xs text-slate-400 px-1 font-medium">
                                                <span>Yetersiz</span>
                                                <span>Geliştirilebilir</span>
                                                <span>İyi</span>
                                            </div>
                                            <p className="text-sm text-slate-600 italic">
                                                {SCORING_DEFINITIONS.find(d => d.score === scores[criterion.id])?.desc}
                                            </p>
                                        </div>
                                    ))
                                )}

                                {activeCriteria.length > 0 && (
                                    <div className="pt-6">
                                        <Button
                                            className="w-full bg-tubitak-red hover:bg-tubitak-red/90 text-lg py-6 shadow-md"
                                            onClick={handleSubmit}
                                            disabled={submitted}
                                        >
                                            {submitted ? "Puanlar Gönderildi" : "Puanları Kaydet/Güncelle"}
                                        </Button>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                </div>
            </main>
        </div>
    );
}
