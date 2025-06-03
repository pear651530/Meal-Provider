import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import TodayMealsPage from "../../pages/TodayMealsPage";
import { AuthContext, AuthContextType } from "../../context/AuthContext";
import i18n from "../../i18n";
import { vi } from "vitest";

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

describe("TodayMealsPage", () => {
    beforeEach(() => {
        vi.resetAllMocks();

        global.fetch = vi.fn().mockImplementation((url: string) => {
            if (url.includes("/menu-items/")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve([
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
                        ]),
                });
            }

            if (url.includes("/reviews/1")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve([
                            { rating: "good", comment: "很好吃！" },
                            { rating: "bad", comment: "太辣了" },
                            { rating: "good", comment: "" },
                        ]),
                });
            }

            if (url.includes("/reviews/2")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }

            return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
        });
    });

    it("should display today's meals and allow viewing comments", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <AuthContext.Provider value={mockAuthContextValue}>
                        <TodayMealsPage />
                    </AuthContext.Provider>
                </I18nextProvider>
            </MemoryRouter>
        );

        // 檢查 loading 字樣
        expect(screen.getByText("載入中...")).toBeInTheDocument();

        // 等待餐點加載完成
        await waitFor(() => expect(screen.getByText("咖哩飯")).toBeInTheDocument());

        expect(screen.getByText("120 元")).toBeInTheDocument();
        expect(screen.getByText("推薦比例：67%")).toBeInTheDocument(); // 2/3 評論是 good

        // 點擊展開評論
        fireEvent.click(screen.getByText("查看評論"));

        expect(await screen.findByText("👍 推薦：很好吃！")).toBeInTheDocument();
        expect(screen.getByText("👎 不推薦：太辣了")).toBeInTheDocument();

        // 點擊收合評論
        fireEvent.click(screen.getByText("收合評論"));

        await waitFor(() => {
            expect(screen.queryByText("👍 推薦：很好吃！")).not.toBeInTheDocument();
        });
    });
});
