"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Lock } from "lucide-react";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        // Call the Google Apps Script API
        import("@/lib/api").then(async ({ verifyLogin }) => {
            const result = await verifyLogin(username, password);

            if (result.success && result.user) {
                // Determine role based on API response or override for admin
                const userRole = result.user.role === "admin" ? "admin" : "panelist";

                // Store full user object including name
                login(result.user.username, userRole);
            } else {
                alert(result.message || "Giriş başarısız. Lütfen bilgilerinizi kontrol ediniz.");
            }
            setLoading(false);
        });
    };

    return (
        <div className="flex h-screen w-full items-center justify-center bg-gray-50">
            <Card className="w-[350px] shadow-lg">
                <CardHeader className="text-center">
                    <div className="mx-auto mb-4 flex h-20 w-auto items-center justify-center">
                        <img src="/logo.png" alt="Logo" className="h-full w-auto object-contain" />
                    </div>
                    <CardTitle className="text-2xl font-bold text-tubitak-dark">Panel Girişi</CardTitle>
                    <CardDescription>
                        Devam etmek için lütfen giriş yapınız
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleLogin}>
                        <div className="grid w-full items-center gap-4">
                            <div className="flex flex-col space-y-1.5">
                                <Label htmlFor="username">Kullanıcı Adı</Label>
                                <Input
                                    id="username"
                                    placeholder="Kullanıcı adınız"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="flex flex-col space-y-1.5">
                                <Label htmlFor="password">Şifre</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    placeholder="******"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                        <Button className="mt-6 w-full bg-tubitak-red hover:bg-tubitak-red/90" type="submit" disabled={loading}>
                            {loading ? "Giriş Yapılıyor..." : "Giriş Yap"}
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <p className="text-xs text-slate-400">ZİRT-AK Panel Simülasyonu</p>
                </CardFooter>
            </Card>
        </div>
    );
}
