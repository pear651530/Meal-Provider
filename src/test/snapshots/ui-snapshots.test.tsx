import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import LanguageSwitcher from "../../components/LanguageSwitcher";
import NavBar from "../../components/NavBar";
import { renderWithProviders } from "../utils";
import { useAuth } from "../../context/AuthContext";

// 模擬 AuthContext
vi.mock("../../context/AuthContext", async () => {
    const actual = await vi.importActual("../../context/AuthContext");
    return {
        ...actual,
        useAuth: vi.fn(),
    };
});

// 模擬 react-router-dom
vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useLocation: () => ({ pathname: "/TodayMeals" }),
        useNavigate: () => vi.fn(),
    };
});

// 模擬 twemoji 以避免快照中的問題
vi.mock("twemoji", () => ({
    default: {
        parse: vi.fn(),
    },
}));

describe("UI 快照測試", () => {
    beforeEach(() => {
        vi.clearAllMocks();

        // 模擬路由
        vi.mock("react-router-dom", async () => {
            const actual = await vi.importActual("react-router-dom");
            return {
                ...actual,
                useLocation: () => ({ pathname: "/TodayMeals" }),
                useNavigate: () => vi.fn(),
            };
        });
    });
    it("LanguageSwitcher 組件快照測試", () => {
        const { container } = renderWithProviders(<LanguageSwitcher />);
        expect(container).toMatchSnapshot();
    }, 20000);
    it("一般用戶的 NavBar 組件快照測試", () => {
        vi.mocked(useAuth).mockReturnValue({
            username: "regular-user",
            isStaff: false,
            isManager: false,
            DebtNeedNotice: false,
            login: vi.fn(),
            logout: vi.fn(),
        });

        const { container } = renderWithProviders(<NavBar />);
        expect(container).toMatchSnapshot();
    }, 20000);
    it("店員的 NavBar 組件快照測試", () => {
        vi.mocked(useAuth).mockReturnValue({
            username: "staff-user",
            isStaff: true,
            isManager: false,
            DebtNeedNotice: false,
            login: vi.fn(),
            logout: vi.fn(),
        });

        const { container } = renderWithProviders(<NavBar />);
        expect(container).toMatchSnapshot();
    }, 20000);
    it("管理員的 NavBar 組件快照測試", () => {
        vi.mocked(useAuth).mockReturnValue({
            username: "manager-user",
            isStaff: true,
            isManager: true,
            DebtNeedNotice: false,
            login: vi.fn(),
            logout: vi.fn(),
        });

        const { container } = renderWithProviders(<NavBar />);
        expect(container).toMatchSnapshot();
    }, 20000);
});
