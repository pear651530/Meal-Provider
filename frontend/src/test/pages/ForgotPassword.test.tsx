import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ForgotPassword from "../../pages/ForgotPassword";
import { renderWithProviders } from "../utils";
import i18n from "../../i18n";

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

describe("ForgotPassword 頁面", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // 模擬 console.log
        console.log = vi.fn();
    });
    it("應該正確渲染忘記密碼頁面", () => {
        renderWithProviders(<ForgotPassword />);
        expect(screen.getByText("找回密碼")).toBeInTheDocument();
        expect(
            screen.getByText(
                "請輸入您的電子郵件地址，我們將發送一封包含重設密碼連結的郵件給您。"
            )
        ).toBeInTheDocument();
        expect(screen.getByPlaceholderText("電子郵件")).toBeInTheDocument();
        expect(screen.getByText("發送重設密碼連結")).toBeInTheDocument();
        expect(screen.getByText("返回登入頁")).toBeInTheDocument();
    }, 5000);
    it("當未輸入電子郵件時應顯示錯誤訊息", async () => {
        renderWithProviders(<ForgotPassword />);
        const sendButton = screen.getByText("發送重設密碼連結");
        fireEvent.click(sendButton);
        expect(screen.getByText("請輸入電子郵件地址")).toBeInTheDocument();
        await waitFor(() => {});
    }, 5000);
    it("應該能夠輸入電子郵件並發送重設連結", async () => {
        renderWithProviders(<ForgotPassword />);
        const user = userEvent.setup();
        const emailInput = screen.getByPlaceholderText("電子郵件");
        await user.type(emailInput, "test@example.com");
        expect(emailInput).toHaveValue("test@example.com");
        const sendButton = screen.getByText("發送重設密碼連結");
        await user.click(sendButton);
        expect(
            screen.getByText("重設密碼的連結已發送至 test@example.com")
        ).toBeInTheDocument();
        expect(console.log).toHaveBeenCalledWith(
            "重設密碼連結已發送至: test@example.com"
        );
        await waitFor(() => {});
    }, 5000);
    it("點擊返回按鈕應導航至登入頁面", async () => {
        renderWithProviders(<ForgotPassword />);
        const backButton = screen.getByText("返回登入頁");
        fireEvent.click(backButton);
        expect(mockNavigate).toHaveBeenCalledWith("/Login");
        await waitFor(() => {});
    }, 5000);
    it("應該支援不同語言", async () => {
        const { container } = renderWithProviders(<ForgotPassword />);
        const i18nInstance = i18n;
        expect(screen.getByText("找回密碼")).toBeInTheDocument();
        await i18nInstance.changeLanguage("en");
        await waitFor(() => {
            expect(screen.getByText("Forgot Password")).toBeInTheDocument();
            expect(
                screen.getByText(
                    "Please enter your email address. We will send you an email with a link to reset your password."
                )
            ).toBeInTheDocument();
            expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
            expect(screen.getByText("Send Reset Link")).toBeInTheDocument();
            expect(screen.getByText("Back to Login")).toBeInTheDocument();
        });
        await waitFor(() => {});
    }, 5000);
});
