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
    login: (username: string) => User | null;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
    username: null,
    isStaff: false,
    isManager: false,
    DebtNeedNotice: false,
    login: () => null,
    logout: () => {},
});

const mockUsers = [
    { username: "admin", isStaff: true, isManager: true, DebtNeedNotice: true },
    { username: "alan", isStaff: true, isManager: false, DebtNeedNotice: false },
    { username: "bob", isStaff: false, isManager: false, DebtNeedNotice: true},
];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isStaff, setIsStaff] = useState(false);
    const [isManager, setIsManager] = useState(false);
    const [DebtNeedNotice, setDebtNeedNotice] = useState(false);

    // ✅ 每次刷新時從 localStorage 載入
    useEffect(() => {
        const savedUser = localStorage.getItem("auth_user");
        if (savedUser) {
            const { username, isStaff, isManager, DebtNeedNotice } = JSON.parse(savedUser);
            setUsername(username);
            setIsStaff(isStaff);
            setIsManager(isManager);
            setDebtNeedNotice(DebtNeedNotice)
        }
    }, []);

    const login = (inputUsername: string): User | null => {
        const user = mockUsers.find(u => u.username === inputUsername);
        if (user) {
            setUsername(user.username);
            setIsStaff(user.isStaff);
            setIsManager(user.isManager);
            setDebtNeedNotice(user.DebtNeedNotice)
            localStorage.setItem("auth_user", JSON.stringify(user)); // ✅ 存入 localStorage
            return user;
        } else {
            alert("無此使用者");
            return null;
        }
    };

    const logout = () => {
        setUsername(null);
        setIsStaff(false);
        setIsManager(false);
        setDebtNeedNotice(false)
        localStorage.removeItem("auth_user"); // ✅ 清除 localStorage
    };

    return (
        <AuthContext.Provider value={{ username, isStaff, isManager, DebtNeedNotice, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
