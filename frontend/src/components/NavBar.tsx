import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LanguageSwitcher from "./LanguageSwitcher";
import { useTranslation } from "react-i18next";
import "./NavBar.css";

const baseLinkStyle = {
    color: "white",
    marginRight: "15px",
    textDecoration: "none",
    fontWeight: "bold",
    opacity: 1,
};
function Navbar(): React.ReactElement | null {
    const location = useLocation();
    const navigate = useNavigate();
    const currentPath = location.pathname;
    const { username, user_id, isClerk, isAdmin, isSuperAdmin, DebtNeedNotice, logout } =
        useAuth();

    //console.log("auth :", useAuth());
    const { t, i18n } = useTranslation();

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
        );
    }

    return null;
}

export default Navbar;
