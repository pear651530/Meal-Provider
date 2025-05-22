import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./NavBar.css";

const baseLinkStyle = {
    color: "white",
    marginRight: "15px",
    textDecoration: "none",
    fontWeight: "bold",
    opacity: 1,
};

function Navbar(): JSX.Element | null {
    const location = useLocation();
    const navigate = useNavigate();
    const currentPath = location.pathname;
    const { username, isStaff, isManager, logout } = useAuth();

    const handleLogout = () => {
        logout();           // 清空狀態
        navigate("/");      // 導回登入頁
    };

    if (currentPath !== "/") {
        console.log(username + " " + isStaff + " " + isManager);
        const navLinks = [
            { label: "今日餐點", to: "/TodayMeals" },
            { label: "用餐紀錄", to: "/records" },
            ...(isStaff ? [{ label: "店員點餐", to: "/orders" }] : []),
            ...(isManager ? [
                { label: "員工賒帳紀錄", to: "/staff-debt" },
                { label: "菜單調整", to: "/menuEditor" },
            ] : []),
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

                <span
                    onClick={handleLogout}
                    style={{ ...baseLinkStyle, cursor: "pointer" }}
                >
                    登出
                </span>
            </nav>
        );
    }

    return null;
}

export default Navbar;
