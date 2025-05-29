import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import MenuEditorPage from "../../pages/MenuEditorPage";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n"; // 假設你有設定 i18n
import { MemoryRouter } from "react-router-dom";

// Mock API 回應
vi.mock("../api/meals", () => ({
    fetchMeals: vi.fn(),
}));

describe("MenuEditorPage", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it("renders loading state initially", () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );
        expect(screen.getByText(/載入中.../i)).toBeInTheDocument();
    });

    it("renders meals after loading", async () => {
        // 提供假資料
        const mockMeals = [
            { id: 1, name: "咖哩飯" },
            { id: 2, name: "炒麵" },
            { id: 3, name: "燒肉丼" },
        ];
        (fetchMeals as jest.Mock).mockResolvedValue(mockMeals);

        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );

        // 等待畫面渲染完成
        await waitFor(() => {
            expect(screen.getByText("咖哩飯")).toBeInTheDocument();
            expect(screen.getByText("炒麵")).toBeInTheDocument();
            expect(screen.getByText("燒肉丼")).toBeInTheDocument();
        });
    });

    // it("allows adding a new meal", async () => {
    //     render(
    //         <MemoryRouter>
    //             <I18nextProvider i18n={i18n}>
    //                 <MenuEditorPage />
    //             </I18nextProvider>
    //         </MemoryRouter>
    //     );

    //     vi.runAllTimers();

    //     await waitFor(() => {
    //         fireEvent.click(screen.getByText(/新增餐點/i));
    //     });

    //     const nameInput = screen.getByPlaceholderText(/餐點名稱/i);
    //     const priceInput = screen.getByPlaceholderText(/價格/i);
    //     const imageInput = screen.getByPlaceholderText(/圖片連結/i);

    //     fireEvent.change(nameInput, { target: { value: "新餐點" } });
    //     fireEvent.change(priceInput, { target: { value: "200" } });
    //     fireEvent.change(imageInput, { target: { value: "https://example.com/image.jpg" } });

    //     fireEvent.click(screen.getByText(/送出新增/i));

    //     await waitFor(() => {
    //         expect(screen.getByText("新餐點")).toBeInTheDocument();
    //     });
    // });

    // it("allows editing a meal", async () => {
    //     render(
    //         <MemoryRouter>
    //             <I18nextProvider i18n={i18n}>
    //                 <MenuEditorPage />
    //             </I18nextProvider>
    //         </MemoryRouter>
    //     );

    //     vi.runAllTimers();

    //     await waitFor(() => {
    //         fireEvent.click(screen.getAllByText("✏️")[0]);
    //     });

    //     const nameInput = screen.getByDisplayValue("咖哩飯");
    //     fireEvent.change(nameInput, { target: { value: "修改後的咖哩飯" } });

    //     fireEvent.click(screen.getByText(/儲存/i));

    //     await waitFor(() => {
    //         expect(screen.getByText("修改後的咖哩飯")).toBeInTheDocument();
    //     });
    // });

    // it("allows deleting a meal", async () => {
    //     render(
    //         <MemoryRouter>
    //             <I18nextProvider i18n={i18n}>
    //                 <MenuEditorPage />
    //             </I18nextProvider>
    //         </MemoryRouter>
    //     );

    //     vi.runAllTimers();

    //     await waitFor(() => {
    //         fireEvent.click(screen.getAllByText("✏️")[0]);
    //     });

    //     fireEvent.click(screen.getByText(/刪除/i));

    //     await waitFor(() => {
    //         expect(screen.queryByText("咖哩飯")).not.toBeInTheDocument();
    //     });
    // });
});