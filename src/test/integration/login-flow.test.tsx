import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginForm from "../../pages/LoginForm";
import { renderWithProviders } from "../utils";
import { AuthProvider } from "../../context/AuthContext";

// 模擬 navigate 函數
const mockNavigate = vi.fn();

// 模擬路由和導航
vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useNavigate: () => mockNavigate,
        useLocation: () => ({ pathname: "/" }),
    };
});

describe("登入流程集成測試", () => {
    let alertSpy: any;

    beforeEach(() => {
        vi.clearAllMocks();
        // 模擬 alert
        alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
        // 模擬 localStorage
        localStorage.clear();
        // 模擬計時器
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
        alertSpy.mockRestore();
    });
    it("成功登入與導航流程", async () => {
        const { container } = renderWithProviders(<LoginForm />);
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime }); // 輸入有效的使用者憑證
        await user.type(screen.getByPlaceholderText(/帳號/i), "admin");
        await user.type(screen.getByPlaceholderText(/密碼/i), "1234");

        // 點擊登入按鈕
        await user.click(screen.getByRole("button", { name: /登入/i }));
        // 檢查是否顯示成功訊息
        expect(screen.getByText("登入成功！")).toBeInTheDocument();

        // 前進計時器，模擬等待導航
        vi.advanceTimersByTime(1000);

        // 驗證導航
        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith("/TodayMeals");
        });
        await waitFor(() => {});
    }, 5000);

    it("登入與切換語言的功能整合", async () => {
        const { container } = renderWithProviders(<LoginForm />);
        const user = userEvent.setup();

        // 找到語言切換按鈕並點擊它
        const languageSwitcher = screen.getByRole("button", {
            name: /繁體中文/i,
        });
        await user.click(languageSwitcher);

        // 切換到英文
        await user.click(screen.getByText("English"));

        // 確認界面元素已切換為英文
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /Staff Login/i })
            ).toBeInTheDocument();
            expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
            expect(
                screen.getByRole("button", { name: /Login/i })
            ).toBeInTheDocument();
        });
        // 嘗試登入
        await user.type(screen.getByPlaceholderText(/Username/i), "admin");
        await user.type(screen.getByPlaceholderText(/Password/i), "1234");
        await user.click(screen.getByRole("button", { name: /Login/i }));

        // 確認登入成功訊息為英文
        expect(screen.getByText("Login successful!")).toBeInTheDocument();
        await waitFor(() => {});
    }, 5000);
    it("導航到忘記密碼頁面並返回", async () => {
        const { container } = renderWithProviders(<LoginForm />);
        const user = userEvent.setup(); // 點擊忘記密碼連結
        await user.click(screen.getByText(/忘記密碼/i));

        expect(mockNavigate).toHaveBeenCalledWith("/ForgotPassword");
        await waitFor(() => {});
    }, 5000);
});
