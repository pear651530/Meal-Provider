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
        vi.useFakeTimers();

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
        expect(screen.getByText("驗證員工號")).toBeInTheDocument();
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
    it("未驗證員工號時應顯示錯誤訊息", async () => {
        renderWithProviders(<Register />);

        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP001");
        await user.type(screen.getByPlaceholderText("密碼"), "password123");
        await user.type(screen.getByPlaceholderText("確認密碼"), "password123");

        const registerButton = screen.getByText("註冊");
        await user.click(registerButton);

        expect(screen.getByText("請先驗證員工號")).toBeInTheDocument();
        await waitFor(() => {});
    }, 5000);
    it("驗證員工號成功的情況", async () => {
        // 模擬成功的 API 回應
        vi.mocked(global.fetch).mockResolvedValueOnce({
            json: async () => ({ exists: true }),
        } as Response);

        renderWithProviders(<Register />);

        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP001");

        const verifyButton = screen.getByText("驗證員工號");
        await user.click(verifyButton);

        await waitFor(() => {
            expect(screen.getByText("員工號驗證成功！")).toBeInTheDocument();
        });
        await waitFor(() => {});
    }, 5000);
    it("驗證員工號失敗的情況", async () => {
        // 模擬失敗的 API 回應
        vi.mocked(global.fetch).mockResolvedValueOnce({
            json: async () => ({ exists: false }),
        } as Response);

        renderWithProviders(<Register />);

        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP999");

        const verifyButton = screen.getByText("驗證員工號");
        await user.click(verifyButton);

        await waitFor(() => {
            expect(
                screen.getByText("無效的員工號，請確認後重試")
            ).toBeInTheDocument();
        });
        await waitFor(() => {});
    }, 5000);
    it("註冊成功應導航至登入頁面", async () => {
        // 模擬驗證成功
        vi.mocked(global.fetch).mockResolvedValueOnce({
            json: async () => ({ exists: true }),
        } as Response);

        renderWithProviders(<Register />);

        // 驗證員工號
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("員工號"), "EMP001");
        await user.click(screen.getByText("驗證員工號"));

        await waitFor(() => {
            expect(screen.getByText("員工號驗證成功！")).toBeInTheDocument();
        });

        // 填寫其餘表單
        await user.type(screen.getByPlaceholderText("密碼"), "password123");
        await user.type(screen.getByPlaceholderText("確認密碼"), "password123");

        // 點擊註冊
        await user.click(screen.getByText("註冊"));

        expect(
            screen.getByText("註冊成功！即將跳轉至登入頁面")
        ).toBeInTheDocument();

        // 前進計時器
        vi.advanceTimersByTime(2000);

        expect(mockNavigate).toHaveBeenCalledWith("/Login");
        await waitFor(() => {});
    }, 5000);
    it("點擊返回按鈕應導航至登入頁面", async () => {
        renderWithProviders(<Register />);

        const backButton = screen.getByText("返回登入頁");
        fireEvent.click(backButton);

        expect(mockNavigate).toHaveBeenCalledWith("/Login");
        await waitFor(() => {});
    }, 5000);
});
