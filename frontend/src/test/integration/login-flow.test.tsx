import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginForm from "../../pages/LoginForm";
import { renderWithProviders } from "../utils";

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

let fetchMock: any;

describe("登入流程集成測試", () => {
    let alertSpy: any;

    beforeEach(() => {
        vi.clearAllMocks();
        // 模擬 alert
        alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
        // 模擬 localStorage
        localStorage.clear();
        fetchMock = vi.fn();
        global.fetch = fetchMock;
    });

    afterEach(() => {
        alertSpy.mockRestore();
    });
    it("成功登入與導航流程", async () => {
        fetchMock.mockImplementation((url: string) => {
            if (url.includes("/token")) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ access_token: "valid-token-admin" }),
                });
            }
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({
                        username: "admin",
                        id: 1,
                        role: "admin",
                    }),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        await user.type(screen.getByPlaceholderText(/帳號/i), "admin");
        await user.type(screen.getByPlaceholderText(/密碼/i), "1234");
        await user.click(screen.getByRole("button", { name: /登入/i }));
        // 等待登入成功訊息
        expect(await screen.findByText("登入成功！")).toBeInTheDocument();
        // 等待導航
        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith("/TodayMeals", {
                replace: true,
            });
        });
    }, 5000);

    it("登入與切換語言的功能整合", async () => {
        fetchMock.mockImplementation((url: string) => {
            if (url.includes("/token")) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({ access_token: "valid-token-admin" }),
                });
            }
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: async () => ({
                        username: "admin",
                        id: 1,
                        role: "admin",
                    }),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        renderWithProviders(<LoginForm />);
        const user = userEvent.setup();

        // 切換語言到英文
        const languageSwitcher = screen.getByRole("button", {
            name: /繁體中文/i,
        });
        await user.click(languageSwitcher);
        await user.click(screen.getByText("English"));

        // 確認界面元素已切換為英文
        await waitFor(() => {
            expect(
                screen.getByRole("heading", { name: /Staff Login/i })
            ).toBeInTheDocument();
            expect(
                screen.getByPlaceholderText(/Username/i)
            ).toBeInTheDocument();
            expect(
                screen.getByPlaceholderText(/Password/i)
            ).toBeInTheDocument();
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
    }, 5000);
});
