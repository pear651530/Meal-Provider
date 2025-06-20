import React, { createContext, useContext, useState, useEffect } from "react";
import { getApiUrl } from '../config/api';

type User = {
    username: string;
    isClerk: boolean;
    isAdmin: boolean;
    isSuperAdmin?: boolean;
    DebtNeedNotice: boolean;
};

interface Notification {
    id: number;
    user_id: number;
    message: string;
    notification_type: string;
    is_read: boolean;
    created_at: string;
}

export interface AuthContextType {
    username: string | null;
    user_id: number | null;
    isClerk: boolean;
    isAdmin: boolean;
    isSuperAdmin: boolean;
    DebtNeedNotice: boolean;
    token: string | null;
    user: User | null;
    notifications: Notification[];
    login: (accessToken: string) => Promise<User | null>;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
    username: null,
    user_id: null,
    isClerk: false,
    isAdmin: false,
    isSuperAdmin: false,
    DebtNeedNotice: false,
    token: null,
    user: null,
    notifications: [],
    login: () => Promise.resolve(null),
    logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [username, setUsername] = useState<string | null>(null);
    const [isClerk, setIsClerk] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);
    const [isSuperAdmin, setIsSuperAdmin] = useState(false);
    const [DebtNeedNotice, setDebtNeedNotice] = useState(false);
    const [token, setToken] = useState<string | null>(null);
    const [user_id, setUserId] = useState<number | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [notifications, setNotifications] = useState<Notification[]>([]);

    useEffect(() => {
        const savedUser = localStorage.getItem("auth_user");
        const savedToken = localStorage.getItem("access_token");
        if (savedUser && savedToken) {
            const userData = JSON.parse(savedUser);
            switch (userData.role) {
                case "super_admin":
                    setIsSuperAdmin(true);
                case "admin":
                    setIsAdmin(true);
                case "clerk":
                    setIsClerk(true);
                default:
                    // Default case - no special role privileges
                    break;
            }
            setUsername(userData.username);
            setUserId(userData.id);
            setUser(userData);
            setToken(savedToken);
            // 載入通知
            if (userData.user_id || userData.id) {
                const userId = userData.user_id ?? userData.id;
                fetch(getApiUrl('USER_SERVICE', `/users/${userId}/notification`), {
                    headers: { Authorization: `Bearer ${savedToken}` },
                })
                    .then((res) => (res.ok ? res.json() : []))
                    .then((data) => setNotifications(data))
                    .catch(() => setNotifications([]));
            }
            setDebtNeedNotice(userData.DebtNeedNotice || false);
        }
    }, []);

    const login = async (accessToken: string): Promise<User | null> => {
        setToken(accessToken);
        localStorage.setItem("access_token", accessToken);
        try {
            const res = await fetch(getApiUrl('USER_SERVICE', '/users/me'), {
                headers: { Authorization: `Bearer ${accessToken}` },
            });
            if (!res.ok) throw new Error("取得使用者資訊失敗");
            const userData = await res.json();
            console.log("/users/me 回傳:", userData); // log 出取得的使用者資訊
            setUsername(userData.username);
            setUserId(userData.id);
            switch (userData.role) {
                case "super_admin":
                    setIsSuperAdmin(true);
                case "admin":
                    setIsAdmin(true);
                case "clerk":
                    setIsClerk(true);
                default:
                    // Default case - no special role privileges
                    break;
            }
            setUser(userData);
            localStorage.setItem("auth_user", JSON.stringify(userData));
            // 取得通知
            const userId = userData.user_id ?? userData.id;
            if (userId) {
                try {
                    const notiRes = await fetch(
                        getApiUrl('USER_SERVICE', `/users/${userId}/notification`),
                        {
                            headers: { Authorization: `Bearer ${accessToken}` },
                        }
                    );
                    if (notiRes.ok) {
                        const notiData = await notiRes.json();
                        setNotifications(notiData);
                    } else {
                        setNotifications([]);
                    }
                } catch {
                    setNotifications([]);
                }
            } else {
                setNotifications([]);
            }
            return userData;
        } catch (e) {
            alert("登入失敗，無法取得使用者資訊");
            setToken(null);
            setUser(null);
            setUserId(null);
            setUsername(null);
            setIsClerk(false);
            setIsAdmin(false);
            setDebtNeedNotice(false);
            setNotifications([]);
            localStorage.removeItem("auth_user");
            localStorage.removeItem("access_token");
            return null;
        }
    };

    const logout = () => {
        setUsername(null);
        setUserId(null);
        setIsClerk(false);
        setIsAdmin(false);
        setIsSuperAdmin(false);
        setDebtNeedNotice(false);
        setToken(null);
        setUser(null);
        setNotifications([]);
        localStorage.removeItem("auth_user");
        localStorage.removeItem("access_token");
    };

    return (
        <AuthContext.Provider
            value={{
                username,
                user_id,
                isClerk,
                isAdmin,
                isSuperAdmin,
                DebtNeedNotice,
                login,
                logout,
                token,
                user,
                notifications,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
