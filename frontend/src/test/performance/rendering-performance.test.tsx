import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginForm from "../../pages/LoginForm";
import { renderWithProviders } from "../utils";
import { performance } from "perf_hooks";

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

describe("性能測試", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // 不要用 fake timers，效能測試需 real timers
    });

    afterEach(() => {
        vi.useRealTimers();
    });
    it("測量語言切換效能", async () => {
        const { container } = renderWithProviders(<LoginForm />);
        const user = userEvent.setup();
        // 找到含有繁體中文的 button（忽略 emoji 與 dropdown）
        const languageSwitcher = Array.from(screen.getAllByRole("button")).find(
            (btn) => btn.textContent && btn.textContent.includes("繁體中文")
        );
        expect(languageSwitcher).toBeTruthy();
        const start = performance.now();
        await user.click(languageSwitcher!);
        // 等待英文出現，代表 UI render 完成
        await screen.findByText("English");
        const end = performance.now();
        const duration = end - start;
        console.log(`語言切換並 render 英文 UI 耗時: ${duration}ms`);
        expect(duration).toBeLessThan(5000);
    }, 10000);
    it("測量登入表單渲染效能", () => {
        const start = performance.now();
        renderWithProviders(<LoginForm />);
        const end = performance.now();
        const duration = end - start;
        console.log(`登入表單渲染耗時: ${duration}ms`);
        expect(duration).toBeLessThan(5000);
    }, 5000);
});
