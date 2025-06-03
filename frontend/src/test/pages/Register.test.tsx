import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Register from "../../pages/Register";
import { renderWithProviders } from "../utils";

// 模擬 navigate 函數
const mockNavigate = vi.fn();

// 模擬路由和導航
vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

// 模擬 fetch API
global.fetch = vi.fn();

describe("Register 頁面", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // 不需要 fake timers，除非有 setTimeout 導航
        // vi.useFakeTimers();
        // 重置 fetch 模擬
        vi.mocked(global.fetch).mockReset();
    });

    afterEach(() => {
        vi.useRealTimers();
    });
    it("應該正確渲染註冊頁面", () => {
        renderWithProviders(<Register />);

        expect(screen.getByText("註冊帳號")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("員工號")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("密碼")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("確認密碼")).toBeInTheDocument();
        expect(screen.getByText("註冊")).toBeInTheDocument();
        expect(screen.getByText("返回登入頁")).toBeInTheDocument();
    }, 5000);
    it("應該能夠輸入表單資料", async () => {
        renderWithProviders(<Register />);

        const user = userEvent.setup();
        const employeeIdInput = screen.getByPlaceholderText("員工號");
        const passwordInput = screen.getByPlaceholderText("密碼");
        const confirmPasswordInput = screen.getByPlaceholderText("確認密碼");

        await user.type(employeeIdInput, "EMP001");
        await user.type(passwordInput, "password123");
        await user.type(confirmPasswordInput, "password123");

        expect(employeeIdInput).toHaveValue("EMP001");
        expect(passwordInput).toHaveValue("password123");
        expect(confirmPasswordInput).toHaveValue("password123");
        await waitFor(() => {});
    }, 5000);
    it("未填寫所有欄位時應顯示錯誤訊息", async () => {
        renderWithProviders(<Register />);

        const registerButton = screen.getByText("註冊");
        fireEvent.click(registerButton);

        expect(screen.getByText("請填寫所有欄位")).toBeInTheDocument();
        await waitFor(() => {});
    }, 5000);
    it("密碼不匹配時應顯示錯誤訊息", async () => {
        renderWithProviders(<Register />);

        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP001");
        await user.type(screen.getByPlaceholderText("密碼"), "password123");
        await user.type(screen.getByPlaceholderText("確認密碼"), "password456");

        const registerButton = screen.getByText("註冊");
        await user.click(registerButton);

        expect(screen.getByText("密碼與確認密碼不一致")).toBeInTheDocument();
        await waitFor(() => {});
    }, 5000);
    it("註冊成功應導航至登入頁面", async () => {
        renderWithProviders(<Register />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP001");
        await user.type(screen.getByPlaceholderText("密碼"), "password123");
        await user.type(screen.getByPlaceholderText("確認密碼"), "password123");

        // 註冊 API
        vi.mocked(global.fetch).mockResolvedValueOnce({
            ok: true,
            json: async () => ({}),
        } as Response);

        // 點擊註冊
        await user.click(screen.getByText("註冊"));

        expect(
            await screen.findByText("註冊成功！即將跳轉至登入頁面")
        ).toBeInTheDocument();

        // 直接等 setTimeout 導航
        await waitFor(
            () => {
                expect(mockNavigate).toHaveBeenCalledWith("/Login");
            },
            { timeout: 3000 }
        );
    }, 10000);
    it("點擊返回按鈕應導航至登入頁面", async () => {
        renderWithProviders(<Register />);

        const backButton = screen.getByText("返回登入頁");
        fireEvent.click(backButton);

        expect(mockNavigate).toHaveBeenCalledWith("/Login");
        await waitFor(() => {});
    }, 5000);
});
