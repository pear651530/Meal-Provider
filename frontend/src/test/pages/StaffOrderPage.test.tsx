import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { I18nextProvider } from "react-i18next";
import StaffOrderPage from "../../pages/StaffOrderPage";
import { AuthContext, AuthContextType } from "../../context/AuthContext";
import i18n from "../../i18n";
import { vi } from "vitest";
import { MemoryRouter } from "react-router-dom";

const mockMeals = [
    {
        id: 1,
        zh_name: "咖哩飯",
        en_name: "Curry Rice",
        price: 120,
        url: "https://image.com/curry.jpg",
        is_available: true,
    },
    {
        id: 2,
        zh_name: "炒麵",
        en_name: "Fried Noodles",
        price: 100,
        url: "https://image.com/noodles.jpg",
        is_available: false,
    },
    {
        id: 3,
        zh_name: "燒肉丼",
        en_name: "Pork Rice Bowl",
        price: 150,
        url: "https://image.com/pork.jpg",
        is_available: true,
    },
];

// ✅ 模擬 auth context
const mockAuthContextValue: AuthContextType = {
    username: "testuser",
    user_id: 1,
    isClerk: false,
    isAdmin: true,
    isSuperAdmin: false,
    DebtNeedNotice: false,
    token: "fake-token",
    user: {
        username: "testuser",
        isClerk: false,
        isAdmin: true,
        DebtNeedNotice: false,
    },
    notifications: [],
    login: vi.fn(),
    logout: vi.fn(),
};

describe("StaffOrderPage", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        global.fetch = vi.fn().mockImplementation((url, options) => {
            if ((url as string).includes("/menu-items/")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockMeals),
                });
            }

            if ((url as string).includes("/orders/") && options?.method === "POST") {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve({ success: true }),
                });
            }

            return Promise.reject(new Error("Unhandled fetch"));
        });

        vi.spyOn(window, "alert").mockImplementation(() => { });
        vi.spyOn(console, "error").mockImplementation(() => { });
    });

    it("should load and display available meals", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <AuthContext.Provider value={mockAuthContextValue}>
                        <StaffOrderPage />
                    </AuthContext.Provider>
                </I18nextProvider>
            </MemoryRouter>
        );

        expect(screen.getByText("載入中...")).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText("咖哩飯")).toBeInTheDocument();
            expect(screen.getByText("燒肉丼")).toBeInTheDocument();
            expect(screen.queryByText("炒麵")).not.toBeInTheDocument(); // 不應顯示 unavailable
        });
    });

    it("should allow selecting a meal, inputting ID, and submitting order", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <AuthContext.Provider value={mockAuthContextValue}>
                        <StaffOrderPage />
                    </AuthContext.Provider>
                </I18nextProvider>
            </MemoryRouter>
        );

        await waitFor(() => screen.getByText("咖哩飯"));

        // 選擇餐點
        const buttons = screen.getAllByText("選擇") as HTMLElement[]; // 明確告訴 TS：這是陣列
        fireEvent.click(buttons[0]);

        // 切換成賒帳
        fireEvent.click(screen.getByLabelText("賒帳"));

        // 輸入員工 ID
        fireEvent.change(screen.getByPlaceholderText("請輸入員工 ID"), {
            target: { value: "123" },
        });

        // 送出訂單
        fireEvent.click(screen.getByText("送出訂單"));

        await waitFor(() => {
            expect(window.alert).toHaveBeenCalledWith("訂單已送出！");
        });
    });

    it("should alert if employee ID or meal is missing", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <AuthContext.Provider value={mockAuthContextValue}>
                        <StaffOrderPage />
                    </AuthContext.Provider>
                </I18nextProvider>
            </MemoryRouter>
        );

        await waitFor(() => screen.getByText("咖哩飯"));

        // 嘗試送出但沒輸入 ID 也沒選餐
        fireEvent.click(screen.getByText("送出訂單"));

        expect(window.alert).toHaveBeenCalledWith("請輸入員工 ID 並選擇一項餐點");
    });
});
