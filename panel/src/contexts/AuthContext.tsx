"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type UserRole = "admin" | "panelist" | null;

interface User {
    username: string;
    role: UserRole;
    name?: string;
}

interface AuthContextType {
    user: User | null;
    login: (username: string, role: UserRole) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();

    useEffect(() => {
        // Check local storage for persisted session
        const storedUser = localStorage.getItem("panel_sim_user");
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
    }, []);

    const login = (username: string, role: UserRole) => {
        const newUser = { username, role, name: username }; // Mock name as username for now
        setUser(newUser);
        localStorage.setItem("panel_sim_user", JSON.stringify(newUser));

        if (role === "admin") {
            router.push("/admin");
        } else {
            router.push("/panelist");
        }
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem("panel_sim_user");
        router.push("/auth/login");
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
