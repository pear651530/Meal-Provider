import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import MenuEditorPage from "../../pages/MenuEditorPage";
import { I18nextProvider } from "react-i18next";
import i18n from "../../i18n";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { MemoryRouter } from "react-router-dom";

beforeEach(() => {
    vi.useFakeTimers(); // ✅ 使用 fake timer
    vi.spyOn(window, "alert").mockImplementation(() => { });
    vi.spyOn(window, "confirm").mockImplementation(() => true);
});

afterEach(() => {
    vi.useRealTimers(); // ✅ 恢復真實時間
    vi.restoreAllMocks();
});

describe("MenuEditorPage", () => {
    it("顯示載入中畫面，之後顯示菜單", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );

        // 等待菜單載入顯示
        await waitFor(() => expect(screen.getByText(/菜單/i)).toBeInTheDocument(), { timeout: 15000 });

        expect(screen.getByText("載入中...")).toBeInTheDocument();

        vi.runAllTimers(); // ⏱️ 快轉 setTimeout

        await waitFor(() => {
            expect(screen.getByText("咖哩飯")).toBeInTheDocument();
            expect(screen.getByText("燒肉丼")).toBeInTheDocument();
            expect(screen.getByText("炒麵")).toBeInTheDocument();
        });
    });

    it("可新增餐點", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );

        // 等待菜單載入顯示
        await waitFor(() => expect(screen.getByText(/菜單/i)).toBeInTheDocument(), { timeout: 15000 });

        vi.runAllTimers();

        await waitFor(() => screen.getByText("咖哩飯"));

        fireEvent.click(screen.getByText("新增餐點"));
        await waitFor(() => screen.getByText("新增餐點資訊"));

        fireEvent.change(screen.getByPlaceholderText("餐點名稱 (必填)"), {
            target: { value: "測試餐點" },
        });
        fireEvent.change(screen.getByPlaceholderText("餐點英文名稱 (非必填)"), {
            target: { value: "Test Meal" },
        });
        fireEvent.change(screen.getByPlaceholderText("價格 (必填)"), {
            target: { value: "200" },
        });
        fireEvent.change(screen.getByPlaceholderText("圖片連結 (必填)"), {
            target: { value: "https://test.jpg" },
        });

        fireEvent.click(screen.getByText("送出新增"));

        await waitFor(() => {
            expect(screen.getByText("測試餐點")).toBeInTheDocument();
        });
    });

    it("點擊編輯按鈕會出現編輯視窗", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );

        // 等待菜單載入顯示
        await waitFor(() => expect(screen.getByText(/菜單/i)).toBeInTheDocument(), { timeout: 15000 });

        vi.runAllTimers();
        await waitFor(() => screen.getByText("咖哩飯"));
        fireEvent.click(screen.getAllByText("✏️")[0]);

        await waitFor(() => {
            expect(screen.getByText("編輯餐點資訊")).toBeInTheDocument();
        });
    });

    it("確認修改按鈕可觸發 alert", async () => {
        render(
            <MemoryRouter>
                <I18nextProvider i18n={i18n}>
                    <MenuEditorPage />
                </I18nextProvider>
            </MemoryRouter>
        );

        // 等待菜單載入顯示
        await waitFor(() => expect(screen.getByText(/菜單/i)).toBeInTheDocument(), { timeout: 15000 });

        vi.runAllTimers();
        await waitFor(() => screen.getByText("確認修改"));
        fireEvent.click(screen.getByText("確認修改"));

        expect(window.alert).toHaveBeenCalledWith("餐點已更新！");
    });
});
