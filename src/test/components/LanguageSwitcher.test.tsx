import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import LanguageSwitcher from "../../components/LanguageSwitcher";
import { renderWithProviders, i18nForTest } from "../utils";
import twemoji from "twemoji";

describe("LanguageSwitcher 組件", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.setItem("language", "zh"); // 預設為中文
        i18nForTest.changeLanguage("zh");
    });
    it("應該正確渲染語言切換按鈕", () => {
        renderWithProviders(<LanguageSwitcher />);

        // 檢查按鈕是否存在
        const switchButton = screen.getByRole("button", { name: /繁體中文/i });
        expect(switchButton).toBeInTheDocument();

        // 檢查台灣國旗表情符號是否存在
        const taiwanFlag = screen.getByText("🇹🇼");
        expect(taiwanFlag).toBeInTheDocument();
    }, 20000);
    it("點擊按鈕時應該顯示語言下拉選單", () => {
        renderWithProviders(<LanguageSwitcher />);

        // 點擊切換按鈕
        const switchButton = screen.getByRole("button");
        fireEvent.click(switchButton);

        // 檢查下拉選單是否出現
        const dropdown = screen.getByTestId("language-dropdown");
        expect(dropdown).toBeInTheDocument();

        const englishOption = screen.getByText("English");
        expect(englishOption).toBeInTheDocument();
    }, 20000);
    it("選擇英文時應該切換語言", async () => {
        renderWithProviders(<LanguageSwitcher />);

        // 點擊切換按鈕
        const switchButton = screen.getByRole("button");
        fireEvent.click(switchButton);

        // 點擊英文選項
        const englishOption = screen.getByText("English");
        fireEvent.click(englishOption);

        // 驗證語言已切換
        await waitFor(() => {
            expect(i18nForTest.language).toBe("en");
            const usFlag = screen.getByText("🇺🇸");
            expect(usFlag).toBeInTheDocument();
            expect(localStorage.getItem("language")).toBe("en");
        });
    }, 20000);
    it("應該調用 twemoji.parse 來處理表情符號", () => {
        renderWithProviders(<LanguageSwitcher />);

        // 驗證 twemoji.parse 被調用
        expect(twemoji.parse).toHaveBeenCalled();
    }, 20000);
});
