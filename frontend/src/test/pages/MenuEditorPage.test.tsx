// MenuEditorPage.test.tsx
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import MenuEditorPage from "../../pages/MenuEditorPage";
import { vi } from "vitest";
import { AuthContext } from "../../context/AuthContext";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n"; // 假設你有初始化好的 i18n 實例

const mockToken = "test-token";

const customRender = (ui: React.ReactElement) =>
    render(
        <AuthContext.Provider
            value={{
                username: "testuser",
                user_id: 1,
                isClerk: false,
                isAdmin: true,
                isSuperAdmin: false,
                DebtNeedNotice: false,
                token: "test-token",
                user: {
                    username: "testuser",
                    isClerk: false,
                    isAdmin: true,
                    isSuperAdmin: false,
                    DebtNeedNotice: false,
                },
                notifications: [],
                login: async () => null,
                logout: () => { },
            }}
        >
            <MenuEditorPage />
        </AuthContext.Provider>
    );

describe("MenuEditorPage", () => {
    beforeEach(() => {
        // Mock fetch
        vi.stubGlobal("fetch", vi.fn());
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it("should render loading state", async () => {
        (fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => [],
        });

        customRender(<MenuEditorPage />);
        expect(screen.getByText(/載入中/i)).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.queryByText(/載入中/i)).not.toBeInTheDocument();
        });
    });

    it("should fetch and display meals", async () => {
        (fetch as any)
            .mockResolvedValueOnce({
                ok: true,
                json: async () => [
                    { id: 1, zh_name: "飯", en_name: "Rice", price: 50, url: "image.jpg", is_available: true },
                ],
            })
            .mockResolvedValueOnce({
                ok: true,
                json: async () => ({ total_reviews: 2, good_reviews: 1 }),
            });

        customRender(<MenuEditorPage />);
        await screen.findByText("飯");
        expect(screen.getByText("飯")).toBeInTheDocument();
        expect(screen.getByText(/推薦比例/i)).toBeInTheDocument();
    });

    it("can open and fill the add meal form", async () => {
        (fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => [],
        });

        customRender(<MenuEditorPage />);
        await waitFor(() => expect(screen.queryByText(/載入中/i)).not.toBeInTheDocument());

        const addButton = screen.getByRole("button", { name: /新增餐點/i });
        fireEvent.click(addButton);

        const nameInput = screen.getByPlaceholderText(/餐點名稱/i);
        fireEvent.change(nameInput, { target: { value: "新餐點" } });

        const priceInput = screen.getByPlaceholderText(/價格/i);
        fireEvent.change(priceInput, { target: { value: "100" } });

        const imageInput = screen.getByPlaceholderText(/圖片連結/i);
        fireEvent.change(imageInput, { target: { value: "http://example.com/image.jpg" } });

        const submit = screen.getByRole("button", { name: /送出新增/i });
        expect(submit).toBeInTheDocument();
    });

    it("can toggle download form", async () => {
        (fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => [],
        });

        customRender(<MenuEditorPage />);
        const downloadBtn = await screen.findByRole("button", { name: /下載報表/i });

        fireEvent.click(downloadBtn);
        expect(await screen.findByText(/選擇報表期間/)).toBeInTheDocument();
    });
});
