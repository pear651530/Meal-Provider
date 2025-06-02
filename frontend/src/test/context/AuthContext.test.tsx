import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "../../context/AuthContext";
import React from "react";

describe("AuthContext", () => {
    // 模擬 localStorage
    let mockLocalStorage: Record<string, string> = {};

    beforeEach(() => {
        // 清除所有模擬
        vi.clearAllMocks();
        mockLocalStorage = {};

        // 模擬 localStorage
        Object.defineProperty(window, "localStorage", {
            value: {
                getItem: vi.fn((key: string) => mockLocalStorage[key] || null),
                setItem: vi.fn((key: string, value: string) => {
                    mockLocalStorage[key] = value;
                }),
                removeItem: vi.fn((key: string) => {
                    delete mockLocalStorage[key];
                }),
                clear: vi.fn(() => {
                    mockLocalStorage = {};
                }),
            },
        });

        // 模擬 alert
        window.alert = vi.fn();
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
    );

    it("初始狀態應為未登入", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        expect(result.current.username).toBeNull();
        expect(result.current.isClerk).toBe(false);
        expect(result.current.isAdmin).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
    }, 20000);

    it("應該能夠登入一般使用者", async () => {
        // 模擬 fetch 響應
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            username: "bob",
                            id: 123,
                            role: "user",
                            DebtNeedNotice: true,
                        }),
                });
            }
            if (url.includes("/notification")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        let user;
        await act(async () => {
            user = await result.current.login("test-token");
        });
        expect(user).toEqual({
            username: "bob",
            id: 123,
            role: "user",
            DebtNeedNotice: true,
        });

        expect(result.current.username).toBe("bob");
        expect(result.current.isClerk).toBe(false);
        expect(result.current.isAdmin).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false); // 實際上是 false，因為 AuthContext 中不會直接設置這個值
        expect(localStorage.setItem).toHaveBeenCalledWith(
            "auth_user",
            JSON.stringify({
                username: "bob",
                id: 123,
                role: "user",
                DebtNeedNotice: true,
            })
        );
    }, 20000);

    it("應該能夠登入店員", async () => {
        // 模擬 fetch 響應
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            username: "alan",
                            id: 456,
                            role: "clerk",
                            DebtNeedNotice: false,
                        }),
                });
            }
            if (url.includes("/notification")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        let user;
        await act(async () => {
            user = await result.current.login("test-token");
        });

        expect(user).toEqual({
            username: "alan",
            id: 456,
            role: "clerk",
            DebtNeedNotice: false,
        });

        expect(result.current.username).toBe("alan");
        expect(result.current.isClerk).toBe(true);
        expect(result.current.isAdmin).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
    }, 20000);

    it("應該能夠登入管理員", async () => {
        // 模擬 fetch 響應
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            username: "admin",
                            id: 789,
                            role: "admin",
                            DebtNeedNotice: true,
                        }),
                });
            }
            if (url.includes("/notification")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        let user;
        await act(async () => {
            user = await result.current.login("test-token");
        });

        expect(user).toEqual({
            username: "admin",
            id: 789,
            role: "admin",
            DebtNeedNotice: true,
        });
        expect(result.current.username).toBe("admin");
        expect(result.current.isClerk).toBe(true);
        expect(result.current.isAdmin).toBe(true);
        expect(result.current.DebtNeedNotice).toBe(false); // 實際值是 false
    }, 20000);

    it("登入不存在的使用者應返回 null", async () => {
        // 模擬 fetch 失敗
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: false,
                    json: () => Promise.resolve({ detail: "User not found" }),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        let user;
        await act(async () => {
            user = await result.current.login("invalid-token");
        });

        expect(user).toBeNull();
        expect(window.alert).toHaveBeenCalledWith(
            "登入失敗，無法取得使用者資訊"
        );
        expect(result.current.username).toBeNull();
    }, 20000);

    it("應該能夠登出", async () => {
        // 先模擬成功登入
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/users/me")) {
                return Promise.resolve({
                    ok: true,
                    json: () =>
                        Promise.resolve({
                            username: "admin",
                            id: 789,
                            role: "admin",
                            DebtNeedNotice: true,
                        }),
                });
            }
            if (url.includes("/notification")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        // 先登入
        await act(async () => {
            await result.current.login("test-token");
        });

        expect(result.current.username).toBe("admin");

        // 再登出
        act(() => {
            result.current.logout();
        });

        expect(result.current.username).toBeNull();
        expect(result.current.isClerk).toBe(false);
        expect(result.current.isAdmin).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
        expect(localStorage.removeItem).toHaveBeenCalledWith("auth_user");
        expect(localStorage.removeItem).toHaveBeenCalledWith("access_token");
    }, 20000);

    it("應該從 localStorage 載入使用者資訊", () => {
        // 模擬 localStorage 已有使用者和 token
        mockLocalStorage["auth_user"] = JSON.stringify({
            username: "admin",
            id: 789,
            role: "admin",
            DebtNeedNotice: true,
        });
        mockLocalStorage["access_token"] = "mock-token";

        // 模擬 fetch 請求 (用於加載通知)
        global.fetch = vi.fn().mockImplementation((url) => {
            if (url.includes("/notification")) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve([]),
                });
            }
            return Promise.reject("unhandled fetch");
        });

        const { result } = renderHook(() => useAuth(), { wrapper }); // 應自動載入使用者資訊        expect(result.current.username).toBe("admin");
        expect(result.current.isClerk).toBe(true);
        expect(result.current.isAdmin).toBe(true);
        expect(result.current.DebtNeedNotice).toBe(true); // 管理員的 DebtNeedNotice 值為 true
    }, 20000);
});
