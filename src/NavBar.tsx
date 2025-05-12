import { Link, useLocation } from "react-router-dom";
import "./NavBar.css";

const baseLinkStyle = {
    color: "white",
    marginRight: "15px",
    textDecoration: "none",
    fontWeight: "bold",
    opacity: 1,
};

interface NavbarProps {
    debtAmount: number;
}

function Navbar({ debtAmount }: NavbarProps): JSX.Element | null {
    const location = useLocation();
    const currentPath = location.pathname;
    //console.log(currentPath);

    if (currentPath != "/") {
        const navLinks = [
            { label: "今日餐點", to: "/TodayMeals" },
            { label: "用餐紀錄", to: "/records" },
            { label: "賒帳紀錄", to: "/debt-records" },
            { label: "店員點餐", to: "/orders" },
            { label: "員工賒帳紀錄", to: "/staff-debt" },
            { label: "菜單調整", to: "/menu-edit" },
        ];

        return (
            <nav className="navbar" style={{ background: "#333", padding: "10px" }}>
                {/*<span style={{ color: "white", marginLeft: "15px", marginRight: "auto" }}>
                    賒帳金額: ${debtAmount}
                </span>*/}

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

                <Link to="/login" style={baseLinkStyle}>
                    登出
                </Link>
            </nav>
        );
    }

    return null;
}

export default Navbar;
