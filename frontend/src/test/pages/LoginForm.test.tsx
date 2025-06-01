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

// mock fetch
let fetchMock: any;

describe("LoginForm 組件", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        window.alert = vi.fn();
        // 不需要 fake timers for input test
        fetchMock = vi.fn();
        global.fetch = fetchMock;
        // 只 mock context 需要的屬性
        vi.mocked(useAuth).mockReturnValue({
            username: "",
            isClerk: false,
            isAdmin: false,
            isSuperAdmin: false,
            DebtNeedNotice: false,
            token: null,
            user: null,
            user_id: null,
            notifications: [],
            login: vi.fn(async (accessToken: string) => {
                if (accessToken === "valid-token-admin") {
                    return {
                        username: "admin",
                        isClerk: false,
                        isAdmin: true,
                        DebtNeedNotice: false,
                    };
                }
                if (accessToken === "valid-token-alan") {
                    return {
                        username: "alan",
                        isClerk: true,
                        isAdmin: false,
                        DebtNeedNotice: true,
                    };
                }
                return null;
            }),
            logout: vi.fn(),
        });
    });

    afterEach(() => {
        vi.useRealTimers();
    });
    it("應該正確渲染登入表單", async () => {
        renderWithProviders(<LoginForm />);
        expect(
            screen.getByRole("heading", { name: /員工登入/i })
        ).toBeInTheDocument();
        expect(screen.getByPlaceholderText("帳號")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("密碼")).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /登入/i })
        ).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /註冊帳號/i })
        ).toBeInTheDocument();
    }, 5000);
    it("使用者輸入應該更新表單狀態", async () => {
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        const usernameInput = screen.getByPlaceholderText("帳號");
        const passwordInput = screen.getByPlaceholderText("密碼");
        await user.type(usernameInput, "admin");
        await user.type(passwordInput, "1234");
        await waitFor(() => {
            expect(usernameInput).toHaveValue("admin");
            expect(passwordInput).toHaveValue("1234");
        });
    }, 5000);
    // it("登入成功時應該顯示成功訊息並導向首頁", async () => {
    //     fetchMock.mockImplementation((url: string) => {
    //         if (url.includes("/token")) {
    //             return Promise.resolve({
    //                 ok: true,
    //                 json: () =>
    //                     Promise.resolve({ access_token: "valid-token-admin" }),
    //             });
    //         }
    //         if (url.includes("/users/me")) {
    //             return Promise.resolve({
    //                 ok: true,
    //                 json: () =>
    //                     Promise.resolve({
    //                         username: "admin",
    //                         id: 1,
    //                         role: "admin",
    //                     }),
    //             });
    //         }
    //         return Promise.reject("unhandled fetch");
    //     });
    //     renderWithProviders(<LoginForm />);
    //     const user = userEvent.setup();
    //     await user.type(screen.getByPlaceholderText("帳號"), "admin");
    //     await user.type(screen.getByPlaceholderText("密碼"), "1234");
    //     const loginButton = screen.getByRole("button", { name: /登入/i });
    //     await user.click(loginButton);
    //     expect(await screen.findByText("登入成功！")).toBeInTheDocument();
    //     await waitFor(() => {
    //         expect(mockNavigate).toHaveBeenCalledWith("/TodayMeals");
    //     });
    // }, 10000);
    it("登入失敗時應該顯示錯誤訊息", async () => {
        fetchMock.mockImplementation((url: string) => {
            if (url.includes("/token")) {
                return Promise.resolve({ ok: false });
            }
            return Promise.reject("unhandled fetch");
        });
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("帳號"), "wronguser");
        await user.type(screen.getByPlaceholderText("密碼"), "wrongpass");
        const loginButton = screen.getByRole("button", { name: /登入/i });
        await user.click(loginButton);
        expect(await screen.findByText("帳號或密碼錯誤")).toBeInTheDocument();
        expect(mockNavigate).not.toHaveBeenCalled();
    }, 10000);
    it("點擊註冊帳號應該導航到註冊頁面", async () => {
        renderWithProviders(<LoginForm />);
        const registerBtn = screen.getByRole("button", { name: /註冊帳號/i });
        fireEvent.click(registerBtn);
        expect(mockNavigate).toHaveBeenCalledWith("/Register");
    });
    it("API 請求異常時應顯示錯誤提示", async () => {
        fetchMock.mockImplementation(() =>
            Promise.reject(new Error("Network error"))
        );
        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText("帳號"), "admin");
        await user.type(screen.getByPlaceholderText("密碼"), "1234");
        const loginButton = screen.getByRole("button", { name: /登入/i });
        await user.click(loginButton);
        expect(await screen.findByText("登入時發生錯誤")).toBeInTheDocument();
        expect(mockNavigate).not.toHaveBeenCalled();
    });
});
