import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, render, fireEvent, within } from "@testing-library/react";
import NavBar from "../../components/NavBar";
import { i18nForTest } from "../utils";
import { I18nextProvider } from "react-i18next";
import { MemoryRouter } from "react-router-dom";

// 模擬 navigate 函數
const mockNavigate = vi.fn();
const mockLogout = vi.fn();

// 設置全局模擬
vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useLocation: vi.fn(() => ({ pathname: "/TodayMeals" })),
        useNavigate: () => mockNavigate,
    };
});

// 模擬 AuthContext
let dynamicAuthMock: any = {};
vi.mock("../../context/AuthContext", () => {
    return {
        useAuth: vi.fn(() => dynamicAuthMock),
    };
});

// 創建一個自定義的渲染函數
interface RenderOptions {
    pathname?: string;
    username?: string;
    isClerk?: boolean;
    isAdmin?: boolean;
    user_id?: number;
    isSuperAdmin?: boolean;
}

// 設置模擬
// beforeEach 只做清理，不再重複 mock
beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("language", "zh");
    i18nForTest.changeLanguage("zh");
});

const renderNavBar = (options: RenderOptions = {}) => {
    const {
        pathname = "/TodayMeals",
        username = "user",
        isClerk = false,
        isAdmin = false,
        user_id = 123,
        isSuperAdmin = false,
    } = options;

    // 依據參數動態設置 mock
    dynamicAuthMock = {
        username,
        user_id,
        isClerk,
        isAdmin,
        isSuperAdmin,
        DebtNeedNotice: false,
        login: vi.fn(),
        logout: mockLogout,
        token: "test-token",
        notifications: [],
    };

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
        renderNavBar({ isClerk: true });

        expect(screen.getByText("店員點餐")).toBeInTheDocument();
    });

    it("管理員應該看到所有管理選項", () => {
        renderNavBar({ isClerk: true, isAdmin: true });

        expect(screen.getByText("員工賒帳紀錄")).toBeInTheDocument();
        expect(screen.getByText("菜單調整")).toBeInTheDocument();
    });

    it("登出按鈕應該調用 logout 函數", async () => {
        renderNavBar();

        const logoutButton = screen.getByText("登出");
        fireEvent.click(logoutButton);

        expect(mockLogout).toHaveBeenCalled();
    });
    it("應該能根據當前路徑高亮顯示導航項", () => {
        renderNavBar({ pathname: "/TodayMeals" });

        // 檢查當前路徑對應的導航項是否有特殊樣式
        const todayMealsLink = screen.getByText("今日餐點").closest("a");
        expect(todayMealsLink, "找不到「今日餐點」的 a 元素").not.toBeNull();
        if (todayMealsLink) {
            expect(todayMealsLink).toHaveStyle("opacity: 0.4");
        }
    });

    it("點擊登出按鈕應該調用登出方法並導航至首頁", () => {
        renderNavBar();

        const logoutButton = screen.getByText("登出");
        fireEvent.click(logoutButton);

        expect(mockLogout).toHaveBeenCalled();
        expect(mockNavigate).toHaveBeenCalledWith("/");
    });

    it("語言切換按鈕應該在導航欄中呈現", () => {
        renderNavBar();

        const navbar = screen.getByRole("navigation");
        expect(navbar).toBeInTheDocument();

        // 查找語言切換按鈕
        const languageSwitcher = within(navbar).getByRole("button");
        expect(languageSwitcher).toBeInTheDocument();
    });
});
