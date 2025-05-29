import React, { createContext, useContext, useState, useEffect } from "react";

type User = {
    username: string;
    isStaff: boolean;
    isManager: boolean;
    DebtNeedNotice: boolean;
};

interface AuthContextType {
    username: string | null;
    isStaff: boolean;
    isManager: boolean;
    DebtNeedNotice: boolean;
    token: string | null;
    user: User | null;
    login: (accessToken: string) => Promise<User | null>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
    username: null,
    isStaff: false,
    isManager: false,
    DebtNeedNotice: false,
    token: null,
    user: null,
    login: () => Promise.resolve(null),
    logout: () => {},
});

const mockUsers = [
    { username: "admin", isStaff: true, isManager: true, DebtNeedNotice: true },
    {
        username: "alan",
        isStaff: true,
        isManager: false,
        DebtNeedNotice: false,
    },
    { username: "bob", isStaff: false, isManager: false, DebtNeedNotice: true },
];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isStaff, setIsStaff] = useState(false);
    const [isManager, setIsManager] = useState(false);
    const [DebtNeedNotice, setDebtNeedNotice] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        const savedUser = localStorage.getItem("auth_user");
        const savedToken = localStorage.getItem("access_token");
        if (savedUser && savedToken) {
            const userObj = JSON.parse(savedUser);
            setUsername(userObj.username);
            setIsStaff(userObj.isStaff);
            setIsManager(userObj.isManager);
            setDebtNeedNotice(userObj.DebtNeedNotice);
            setUser(userObj);
            setToken(savedToken);
        }
    }, []);

    const login = async (accessToken: string): Promise<User | null> => {
        setToken(accessToken);
        localStorage.setItem("access_token", accessToken);
        try {
            const res = await fetch("http://localhost:8000/users/me", {
                headers: { Authorization: `Bearer ${accessToken}` },
            });
            if (!res.ok) throw new Error("取得使用者資訊失敗");
            const userData = await res.json();
            console.log("/users/me 回傳:", userData); // log 出取得的使用者資訊
            setUsername(userData.username);
            setIsStaff(userData.isStaff);
            setIsManager(userData.isManager);
            setDebtNeedNotice(userData.DebtNeedNotice);
            setUser(userData);
            localStorage.setItem("auth_user", JSON.stringify(userData));
            return userData;
        } catch (e) {
            alert("登入失敗，無法取得使用者資訊");
            setToken(null);
            setUser(null);
            setUsername(null);
            setIsStaff(false);
            setIsManager(false);
            setDebtNeedNotice(false);
            localStorage.removeItem("auth_user");
            localStorage.removeItem("access_token");
            return null;
        }
    };

    const logout = () => {
        setUsername(null);
        setIsStaff(false);
        setIsManager(false);
        setDebtNeedNotice(false);
        setToken(null);
        setUser(null);
        localStorage.removeItem("auth_user");
        localStorage.removeItem("access_token");
    };

    return (
        <AuthContext.Provider
            value={{
                username,
                isStaff,
                isManager,
                DebtNeedNotice,
                login,
                logout,
                token,
                user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
