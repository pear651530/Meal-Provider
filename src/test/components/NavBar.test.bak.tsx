// 新的 NavBar.test.tsx 檔案
import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, render, fireEvent, within } from "@testing-library/react";
import NavBar from "../../components/NavBar";
import { i18nForTest } from "../utils";
import { I18nextProvider } from "react-i18next";
import { MemoryRouter } from "react-router-dom";

// 模擬 navigate 函數
const mockNavigate = vi.fn();
const mockLogout = vi.fn();

// 創建一個自定義的渲染函數
const renderNavBar = (options = {}) => {
    const {
        pathname = "/TodayMeals",
        username = "user",
        isStaff = false,
        isManager = false,
    } = options;

    // 模擬 react-router-dom
    vi.mock("react-router-dom", () => {
        const actual = require("react-router-dom");
        return {
            ...actual,
            useLocation: () => ({ pathname }),
            useNavigate: () => mockNavigate,
        };
    });

    // 模擬 AuthContext
    vi.mock("../../context/AuthContext", () => {
        return {
            useAuth: () => ({
                username,
                isStaff,
                isManager,
                DebtNeedNotice: false,
                login: vi.fn(),
                logout: mockLogout,
            }),
        };
    });

    return render(
        <I18nextProvider i18n={i18nForTest}>
            <MemoryRouter initialEntries={[pathname]}>
                <NavBar />
            </MemoryRouter>
        </I18nextProvider>
    );
};

describe("NavBar 組件", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.setItem("language", "zh");
        i18nForTest.changeLanguage("zh");
    });

    it("一般使用者應該看到基本的導航選項", () => {
        renderNavBar();

        // 檢查一般使用者可見的連結
        expect(screen.getByText("今日餐點")).toBeInTheDocument();
        expect(screen.getByText("用餐紀錄")).toBeInTheDocument();
        expect(screen.getByText("登出")).toBeInTheDocument();

        // 檢查店員專用選項不可見
        expect(screen.queryByText("店員點餐")).not.toBeInTheDocument();

        // 檢查管理員專用選項不可見
        expect(screen.queryByText("員工賒帳紀錄")).not.toBeInTheDocument();
        expect(screen.queryByText("菜單調整")).not.toBeInTheDocument();
    });

    it("店員應該看到店員點餐選項", () => {
        renderNavBar({ isStaff: true });

        expect(screen.getByText("店員點餐")).toBeInTheDocument();
    });

    it("管理員應該看到所有管理選項", () => {
        renderNavBar({ isStaff: true, isManager: true });

        expect(screen.getByText("員工賒帳紀錄")).toBeInTheDocument();
        expect(screen.getByText("菜單調整")).toBeInTheDocument();
    });

    it("點擊登出按鈕應該調用登出方法並導航至首頁", () => {
        renderNavBar();

        const logoutButton = screen.getByText("登出");
        fireEvent.click(logoutButton);

        expect(mockLogout).toHaveBeenCalled();
        expect(mockNavigate).toHaveBeenCalledWith("/");
    });

    it("在登入頁應該不渲染導航欄", () => {
        const { container } = renderNavBar({ pathname: "/" });
        expect(container.firstChild).toBeNull();
    });

    it("語言切換按鈕應該在導航欄中呈現", () => {
        renderNavBar();

        try {
            const navbar = screen.getByRole("navigation");
            expect(navbar).toBeInTheDocument();

            // 查找語言切換按鈕
            const languageSwitcher = within(navbar).getByRole("button");
            expect(languageSwitcher).toBeInTheDocument();
        } catch (error) {
            console.error("無法找到導航欄，頁面內容:", screen.debug());
            throw error;
        }
    });
});
