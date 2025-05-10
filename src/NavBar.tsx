import { Link, useLocation } from "react-router-dom";
import "./NavBar.css";

const linkStyle = {
    color: "white",
    marginRight: "15px",
    textDecoration: "none",
    fontWeight: "bold",
};

interface NavbarProps {
    debtAmount: number;
}

function Navbar({ debtAmount }: NavbarProps): JSX.Element {
    const location = useLocation();
    const currentPath = location.pathname;
    console.log(currentPath);

    if (currentPath === "/records") {
        return (
            <nav
                className="navbar"
                style={{ background: "#333", padding: "10px" }}
            >
                <span style={{ color: "white", marginLeft: "15px" }}>
                    賒帳金額: ${debtAmount}
                </span>
                <Link to="/login" style={linkStyle}>
                    登出
                </Link>
            </nav>
        );
    }
}

export default Navbar;
