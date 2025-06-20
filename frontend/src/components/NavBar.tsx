import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";
import "./NavBar.css";
import { getApiUrl } from '../config/api';

const baseLinkStyle = {
    color: "white",
    marginRight: "15px",
    textDecoration: "none",
    fontWeight: "bold",
    opacity: 1,
};

interface Notification {
    id: number;
    message: string;
    notification_type: string;
    is_read: boolean;
}

function Navbar(): React.ReactElement | null {
    const location = useLocation();
    const navigate = useNavigate();
    const currentPath = location.pathname;
    const { username, user_id, isClerk, isAdmin, isSuperAdmin, DebtNeedNotice, logout, token } =
        useAuth();

    //console.log("auth :", useAuth());
    const { t, i18n } = useTranslation();
    const [notifications, setNotifications] = useState<Notification[]>([]);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const res = await fetch(getApiUrl('USER_SERVICE', `/users/${user_id}/notifications`), {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!res.ok) throw new Error("Failed to fetch notifications");

                const data = await res.json();
                const unread = data.filter((n: Notification) => !n.is_read && n.notification_type == "billing");
                setNotifications(unread);
            } catch (err) {
                console.error("通知載入失敗", err);
            }
        };

        fetchNotifications();
    }, [user_id, token]);

    const handleMarkAsRead = async (id: number) => {
        try {
            const res = await fetch(getApiUrl('USER_SERVICE', `/notifications/${id}/read`), {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) throw new Error("標記通知失敗");

            setNotifications((prev) => prev.filter((n) => n.id !== id));
        } catch (err) {
            console.error("無法標記通知為已讀", err);
        }
    };

    const handleLogout = () => {
        logout(); // 清空狀態
        navigate("/"); // 導回登入頁
    };

    if (currentPath !== "/") {
        const navLinks = [
            { label: t("今日餐點"), to: "/TodayMeals" },
            { label: t("用餐紀錄"), to: "/records" },
            ...(isClerk ? [{ label: t("店員點餐"), to: "/orders" }] : []),
            ...(isAdmin
                ? [
                    { label: t("員工賒帳紀錄"), to: "/staff-debt" },
                    { label: t("菜單調整"), to: "/menuEditor" },
                ]
                : []),
            ...(isSuperAdmin
                ? [{ label: t("員工管理"), to: "/staff-management" }]
                : []),
        ];

        return (
            <>
                <nav
                    className="navbar"
                    style={{ background: "#333", padding: "10px" }}
                >
                    <span style={{ color: "white", marginRight: "20px", fontWeight: "bold" }}>
                        {t("ID")}：{user_id}
                    </span>

                    {navLinks.map(({ label, to }) => (
                        <Link
                            key={to}
                            to={to}
                            style={{
                                ...baseLinkStyle,
                                opacity: currentPath === to ? 0.4 : 1,
                                pointerEvents: currentPath === to ? "none" : "auto",
                            }}
                        >
                            {label}
                        </Link>
                    ))}

                    <LanguageSwitcher />

                    <span
                        onClick={handleLogout}
                        style={{ ...baseLinkStyle, cursor: "pointer" }}
                    >
                        {t("登出")}
                    </span>

                </nav>



                {
                    notifications.length > 0 && (
                        <div className="notification-panel">
                            {notifications.map((n) => (
                                <div key={n.id} className="notification">
                                    <button
                                        className="close-btn"
                                        onClick={() => handleMarkAsRead(n.id)}
                                    >
                                        ×
                                    </button>
                                    <p>{t("請盡速繳費!")}</p>
                                </div>
                            ))}
                        </div>
                    )
                }
            </>
        );
    }

    return null;
}

export default Navbar;
