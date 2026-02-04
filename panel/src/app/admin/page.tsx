"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { LogOut, RefreshCw, Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

// Mock Data Types (Updated)
type Score = {
    panelistId: string;
    panelistName: string;
    ozgun_deger: number;
    yontem: number;
    proje_yonetimi: number;
    yaygin_etki: number;
};

const CRITERIA_LIST = [
    { id: "ozgun_deger", label: "Özgün Değer" },
    { id: "yontem", label: "Yöntem" },
    { id: "proje_yonetimi", label: "Proje Yönetimi" },
    { id: "yaygin_etki", label: "Yaygın Etki" },
];

const MOCK_SCORES: Score[] = [];

export default function AdminPage() {
    const { user, logout } = useAuth();
    const [showNames, setShowNames] = useState(false);
    const [scores, setScores] = useState<Score[]>(MOCK_SCORES);
    const [loading, setLoading] = useState(true);

    // Game State
    const [activeCriteria, setActiveCriteria] = useState<string[]>([]);
    const [resultsPublished, setResultsPublished] = useState(false);

    useEffect(() => {
        // Fetch scores and game state
        Promise.all([
            import("@/lib/api").then(m => m.getScores()),
            import("@/lib/api").then(m => m.getGameState())
        ]).then(([scoresData, gameState]) => {
            setScores(scoresData);
            setActiveCriteria(gameState.activeCriteria || []);
            setResultsPublished(gameState.resultsPublished || false);
            setLoading(false);
        });
    }, []);

    const toggleCriteria = (id: string) => {
        let newCriteria;
        if (activeCriteria.includes(id)) {
            newCriteria = activeCriteria.filter(c => c !== id);
        } else {
            newCriteria = [...activeCriteria, id];
        }

        setActiveCriteria(newCriteria);
        import("@/lib/api").then(m => m.updateGameState(newCriteria, resultsPublished));
    };

    const togglePublish = () => {
        const newState = !resultsPublished;
        setResultsPublished(newState);
        import("@/lib/api").then(m => m.updateGameState(activeCriteria, newState));
    };

    // Calculate Averages
    const calculateAverage = (field: keyof Omit<Score, "panelistId" | "panelistName">) => {
        if (scores.length === 0) return "0";
        const sum = scores.reduce((acc, curr) => acc + (curr[field] || 0), 0);
        return (sum / scores.length).toFixed(1);
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
        if (scores.length === 0) return 0;
        const totalSum = scores.reduce((acc, curr) => acc + calculateWeightedScore(curr), 0);
        return (totalSum / scores.length).toFixed(2);
    };

    if (loading) return <div className="flex h-screen items-center justify-center">Yükleniyor...</div>;

    return (
        <div className="min-h-screen bg-gray-50 pb-10">
            {/* Header */}
            <header className="bg-slate-900 text-white sticky top-0 z-10 shadow-md">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <img src="/logo.png" alt="Logo" className="h-10 w-auto bg-white rounded p-1 object-contain" />
                        <span className="font-semibold">Panel Yönetici Ekranı</span>
                    </div>
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" className="text-white hover:bg-slate-800" size="sm" onClick={() => window.location.reload()}>
                            <RefreshCw className="h-4 w-4 mr-2" /> Yenile
                        </Button>
                        <Button variant="destructive" size="sm" onClick={logout}>
                            <LogOut className="h-4 w-4 mr-2" /> Çıkış
                        </Button>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 mt-8">

                {/* Control Panel */}
                <Card className="mb-6 border-slate-200 shadow-sm">
                    <CardHeader className="bg-slate-50 border-b py-3">
                        <CardTitle className="text-base font-semibold text-slate-700">Değerlendirme Kontrol Paneli</CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                        <div className="flex flex-wrap gap-4 items-center">
                            <span className="text-sm font-medium text-slate-600">Aktif Kriterler:</span>
                            {CRITERIA_LIST.map(c => (
                                <Button
                                    key={c.id}
                                    variant={activeCriteria.includes(c.id) ? "default" : "outline"}
                                    onClick={() => toggleCriteria(c.id)}
                                    className={activeCriteria.includes(c.id) ? "bg-blue-600 hover:bg-blue-700" : ""}
                                    size="sm"
                                >
                                    {c.label} {activeCriteria.includes(c.id) ? "(Açık)" : "(Kapalı)"}
                                </Button>
                            ))}

                            <div className="h-8 w-px bg-slate-200 mx-2"></div>

                            <Button
                                variant={resultsPublished ? "destructive" : "secondary"}
                                onClick={togglePublish}
                                className={resultsPublished ? "bg-red-600 hover:bg-red-700" : "bg-emerald-600 text-white hover:bg-emerald-700"}
                                size="sm"
                            >
                                {resultsPublished ? "Sonuçları Yayından Kaldır" : "SONUÇLARI YAYINLA"}
                            </Button>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">
                            * Kriterleri sırasıyla açarak panelistlerin oylamasını sağlayabilirsiniz. "Sonuçları Yayınla" dediğinizde panelistler ortalamaları görebilir.
                        </p>
                    </CardContent>
                </Card>

                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-slate-900">Proje 5005: Fındık Hasat Makinaları İçin Temizleme Ünitesi Geliştirilmesi</h1>
                    <Button
                        variant="outline"
                        onClick={() => setShowNames(!showNames)}
                        className="flex items-center gap-2"
                    >
                        {showNames ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        {showNames ? "İsimleri Gizle" : "İsimleri Göster"}
                    </Button>
                </div>

                {/* Score Table */}
                <Card className="overflow-hidden">
                    <CardHeader className="bg-slate-50 border-b">
                        <CardTitle>Puan Tablosu</CardTitle>
                        <CardDescription>Ağırlıklı Puanlamaya Göre Değerlendirme Sonuçları</CardDescription>
                    </CardHeader>
                    <div className="overflow-x-auto">
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
                                {scores.map((score, index) => (
                                    <tr key={score.panelistId} className="bg-white border-b hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-left">
                                            {showNames ? score.panelistName : `Panelist ${index + 1}`}
                                        </td>
                                        <td className="px-6 py-4">{score.ozgun_deger}</td>
                                        <td className="px-6 py-4">{score.yontem}</td>
                                        <td className="px-6 py-4">{score.proje_yonetimi}</td>
                                        <td className="px-6 py-4">{score.yaygin_etki}</td>
                                        <td className="px-6 py-4"></td>
                                    </tr>
                                ))}

                                {/* Averages Row */}
                                <tr className="bg-tubitak-red/10 border-t-2 border-tubitak-red/20 font-bold text-tubitak-dark">
                                    <td className="px-6 py-4 text-left">GENEL ORTALAMA</td>
                                    <td className="px-6 py-4">{calculateAverage("ozgun_deger")}</td>
                                    <td className="px-6 py-4">{calculateAverage("yontem")}</td>
                                    <td className="px-6 py-4">{calculateAverage("proje_yonetimi")}</td>
                                    <td className="px-6 py-4">{calculateAverage("yaygin_etki")}</td>
                                    <td className="px-6 py-4 text-tubitak-red text-lg">
                                        {(parseFloat(calculateAverage("ozgun_deger")) +
                                            parseFloat(calculateAverage("yontem")) +
                                            parseFloat(calculateAverage("proje_yonetimi")) +
                                            parseFloat(calculateAverage("yaygin_etki"))).toFixed(1)}
                                    </td>
                                </tr>
                                <tr className="bg-tubitak-red/5 border-t border-tubitak-red/10 font-semibold text-tubitak-dark/80 text-sm">
                                    <td className="px-6 py-4 text-left">AĞIRLIKLI ORTALAMA</td>
                                    <td className="px-6 py-4">{(parseFloat(calculateAverage("ozgun_deger")) * 0.35).toFixed(2)}</td>
                                    <td className="px-6 py-4">{(parseFloat(calculateAverage("yontem")) * 0.25).toFixed(2)}</td>
                                    <td className="px-6 py-4">{(parseFloat(calculateAverage("proje_yonetimi")) * 0.20).toFixed(2)}</td>
                                    <td className="px-6 py-4">{(parseFloat(calculateAverage("yaygin_etki")) * 0.20).toFixed(2)}</td>
                                    <td className="px-6 py-4 text-tubitak-red font-bold text-lg">
                                        {((parseFloat(calculateAverage("ozgun_deger")) * 0.35) +
                                            (parseFloat(calculateAverage("yontem")) * 0.25) +
                                            (parseFloat(calculateAverage("proje_yonetimi")) * 0.20) +
                                            (parseFloat(calculateAverage("yaygin_etki")) * 0.20)).toFixed(2)}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </Card>
            </main>
        </div>
    );
}
