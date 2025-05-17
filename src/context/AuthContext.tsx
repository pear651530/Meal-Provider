import { createContext, useContext, useState } from "react";

interface AuthContextType {
    username: string | null;
    isStaff: boolean;
    isManager: boolean;
    login: (username: string) => void;
    logout: () => void;
}

// 建立 context
const AuthContext = createContext<AuthContextType>({
    username: null,
    isStaff: false,
    isManager: false,
    login: () => {},
    logout: () => {},
});

// 模擬的「使用者資料庫」
const mockUsers = [
    { username: "admin", isStaff: true, isManager: true },
    { username: "alan", isStaff: true, isManager: false },
    { username: "bob", isStaff: false, isManager: false },
];

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isStaff, setIsStaff] = useState(false);
    const [isManager, setIsManager] = useState(false);

    const login = (name: string) => {
        const user = mockUsers.find((u) => u.username === name);
        if (user) {
            setUsername(user.username);
            setIsStaff(user.isStaff);
            setIsManager(user.isManager);
        } else {
            // 查無此人則清空狀態（或你可以加入錯誤訊息）
            logout();
        }
    };

    const logout = () => {
        setUsername(null);
        setIsStaff(false);
        setIsManager(false);
    };

    return (
        <AuthContext.Provider
            value={{ username, isStaff, isManager, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
