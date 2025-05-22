import React, { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
    username: string | null;
    isStaff: boolean;
    isManager: boolean;
    login: (username: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
    username: null,
    isStaff: false,
    isManager: false,
    login: () => {},
    logout: () => {},
});

const mockUsers = [
    { username: "admin", isStaff: true, isManager: true },
    { username: "alan", isStaff: true, isManager: false },
    { username: "bob", isStaff: false, isManager: false },
];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isStaff, setIsStaff] = useState(false);
    const [isManager, setIsManager] = useState(false);

    // ✅ 每次刷新時從 localStorage 載入
    useEffect(() => {
        const savedUser = localStorage.getItem("auth_user");
        if (savedUser) {
            const { username, isStaff, isManager } = JSON.parse(savedUser);
            setUsername(username);
            setIsStaff(isStaff);
            setIsManager(isManager);
        }
    }, []);

    const login = (inputUsername: string) => {
        const user = mockUsers.find(u => u.username === inputUsername);
        if (user) {
            setUsername(user.username);
            setIsStaff(user.isStaff);
            setIsManager(user.isManager);
            localStorage.setItem("auth_user", JSON.stringify(user)); // ✅ 存入 localStorage
        } else {
            alert("無此使用者");
        }
    };

    const logout = () => {
        setUsername(null);
        setIsStaff(false);
        setIsManager(false);
        localStorage.removeItem("auth_user"); // ✅ 清除 localStorage
    };

    return (
        <AuthContext.Provider value={{ username, isStaff, isManager, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
