import { describe, it, expect, vi, beforeEach } from "vitest";
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
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });
    it("測量語言切換效能", async () => {
        const { container } = renderWithProviders(<LoginForm />);
        const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
        const languageSwitcher = screen.getByRole("button", {
            name: /繁體中文/i,
        });
        const start = performance.now();
        await user.click(languageSwitcher);
        const end = performance.now();
        const duration = end - start;
        console.log(`語言切換按鈕點擊耗時: ${duration}ms`);
        expect(duration).toBeLessThan(5000);
        await waitFor(() => {});
    }, 5000);
    it("測量登入表單渲染效能", () => {
        const start = performance.now();
        renderWithProviders(<LoginForm />);
        const end = performance.now();
        const duration = end - start;
        console.log(`登入表單渲染耗時: ${duration}ms`);
        expect(duration).toBeLessThan(5000);
    }, 5000);
});
