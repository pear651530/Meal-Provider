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
    const { username, isStaff, isManager, DebtNeedNotice, logout } = useAuth();
    const { t, i18n } = useTranslation();

    const handleLogout = () => {
        logout(); // 清空狀態
        navigate("/"); // 導回登入頁
    };

    if (currentPath !== "/") {
        const navLinks = [
            { label: t("今日餐點"), to: "/TodayMeals" },
            { label: t("用餐紀錄"), to: "/records" },
            ...(isStaff ? [{ label: t("店員點餐"), to: "/orders" }] : []),
            ...(isManager
                ? [
                      { label: t("員工賒帳紀錄"), to: "/staff-debt" },
                      { label: t("菜單調整"), to: "/menuEditor" },
                  ]
                : []),
        ];

        return (
            <nav
                className="navbar"
                style={{ background: "#333", padding: "10px" }}
            >
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
