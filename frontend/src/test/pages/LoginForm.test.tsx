import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginForm from "../../pages/LoginForm";
import { renderWithProviders } from "../utils";
import { useAuth } from "../../context/AuthContext";

// 模擬 navigate 函數
const mockNavigate = vi.fn();

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
        useNavigate: () => mockNavigate,
    };
});

describe("LoginForm 組件", () => {
    const mockLogin = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();

        // 模擬 alert
        window.alert = vi.fn();

        // 模擬 setTimeout
        vi.useFakeTimers();

        // 預設 login 行為
        mockLogin.mockReturnValue({
            username: "",
            isStaff: false,
            isManager: false,
            DebtNeedNotice: false,
        });
        vi.mocked(useAuth).mockReturnValue({
            username: "",
            isStaff: false,
            isManager: false,
            DebtNeedNotice: false,
            login: mockLogin,
            logout: vi.fn(),
        });
    });

    afterEach(() => {
        vi.useRealTimers();
    });
    it("應該正確渲染登入表單", () => {
        renderWithProviders(<LoginForm />);
        expect(
            screen.getByRole("heading", { name: /員工登入/i })
        ).toBeInTheDocument();
        expect(screen.getByPlaceholderText("帳號")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("密碼")).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /登入/i })
        ).toBeInTheDocument();
        expect(screen.getByText(/註冊帳號/i)).toBeInTheDocument();
        expect(screen.getByText(/忘記密碼/i)).toBeInTheDocument();
    }, 5000);
    it("使用者輸入應該更新表單狀態", async () => {
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        const usernameInput = screen.getByPlaceholderText("帳號");
        const passwordInput = screen.getByPlaceholderText("密碼");
        await user.type(usernameInput, "admin");
        await user.type(passwordInput, "1234");
        expect(usernameInput).toHaveValue("admin");
        expect(passwordInput).toHaveValue("1234");
        await waitFor(() => {});
    }, 5000);
    it("登入成功時應該顯示成功訊息並導向首頁", async () => {
        // 模擬登入成功
        mockLogin.mockReturnValue({
            username: "admin",
            isStaff: true,
            isManager: false,
            DebtNeedNotice: false,
        });
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("帳號"), "admin");
        await user.type(screen.getByPlaceholderText("密碼"), "1234");
        const loginButton = screen.getByRole("button", { name: /登入/i });
        await user.click(loginButton);
        expect(screen.getByText("登入成功！")).toBeInTheDocument();
        expect(mockLogin).toHaveBeenCalledWith("admin");
        vi.runAllTimers();
        expect(mockNavigate).toHaveBeenCalledWith("/TodayMeals");
        await waitFor(() => {});
    }, 5000);
    it("登入失敗時應該顯示錯誤訊息", async () => {
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("帳號"), "wronguser");
        await user.type(screen.getByPlaceholderText("密碼"), "wrongpass");
        const loginButton = screen.getByRole("button", { name: /登入/i });
        await user.click(loginButton);
        expect(screen.getByText("帳號或密碼錯誤")).toBeInTheDocument();
        expect(mockNavigate).not.toHaveBeenCalled();
        await waitFor(() => {});
    }, 5000);
    it("當用戶有未清償債務時應該顯示提醒", async () => {
        // 模擬有債務的登入
        mockLogin.mockReturnValue({
            username: "alan",
            isStaff: true,
            isManager: false,
            DebtNeedNotice: true,
        });
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("帳號"), "alan");
        await user.type(screen.getByPlaceholderText("密碼"), "1234");
        const loginButton = screen.getByRole("button", { name: /登入/i });
        await user.click(loginButton);
        vi.runAllTimers();
        expect(window.alert).toHaveBeenCalledWith("尚有餘款未繳清!");
        await waitFor(() => {});
    }, 5000);
    it("點擊忘記密碼應該導航到忘記密碼頁面", async () => {
        renderWithProviders(<LoginForm />);
        const forgotPasswordLink = screen.getByText(/忘記密碼/i);
        fireEvent.click(forgotPasswordLink);
        expect(mockNavigate).toHaveBeenCalledWith("/ForgotPassword");
        await waitFor(() => {});
    }, 5000);
    it("點擊註冊帳號應該導航到註冊頁面", async () => {
        renderWithProviders(<LoginForm />);
        const registerLink = screen.getByText(/註冊帳號/i);
        fireEvent.click(registerLink);
        expect(mockNavigate).toHaveBeenCalledWith("/Register");
        await waitFor(() => {});
    }, 5000);
});
