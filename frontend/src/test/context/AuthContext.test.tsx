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
        expect(result.current.isStaff).toBe(false);
        expect(result.current.isManager).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
    }, 20000);
    it("應該能夠登入一般使用者", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            const user = result.current.login("bob");
            expect(user).toEqual({
                username: "bob",
                isStaff: false,
                isManager: false,
                DebtNeedNotice: true,
            });
        });

        expect(result.current.username).toBe("bob");
        expect(result.current.isStaff).toBe(false);
        expect(result.current.isManager).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(true);
        expect(localStorage.setItem).toHaveBeenCalledWith(
            "auth_user",
            JSON.stringify({
                username: "bob",
                isStaff: false,
                isManager: false,
                DebtNeedNotice: true,
            })
        );
    }, 20000);
    it("應該能夠登入店員", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            const user = result.current.login("alan");
            expect(user).toEqual({
                username: "alan",
                isStaff: true,
                isManager: false,
                DebtNeedNotice: false,
            });
        });

        expect(result.current.username).toBe("alan");
        expect(result.current.isStaff).toBe(true);
        expect(result.current.isManager).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
    }, 20000);
    it("應該能夠登入管理員", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            const user = result.current.login("admin");
            expect(user).toEqual({
                username: "admin",
                isStaff: true,
                isManager: true,
                DebtNeedNotice: true,
            });
        });

        expect(result.current.username).toBe("admin");
        expect(result.current.isStaff).toBe(true);
        expect(result.current.isManager).toBe(true);
        expect(result.current.DebtNeedNotice).toBe(true);
    }, 20000);
    it("登入不存在的使用者應返回 null", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        act(() => {
            const user = result.current.login("nonexistent");
            expect(user).toBeNull();
        });

        expect(window.alert).toHaveBeenCalledWith("無此使用者");
        expect(result.current.username).toBeNull();
    }, 20000);
    it("應該能夠登出", () => {
        const { result } = renderHook(() => useAuth(), { wrapper });

        // 先登入
        act(() => {
            result.current.login("admin");
        });

        expect(result.current.username).toBe("admin");

        // 再登出
        act(() => {
            result.current.logout();
        });

        expect(result.current.username).toBeNull();
        expect(result.current.isStaff).toBe(false);
        expect(result.current.isManager).toBe(false);
        expect(result.current.DebtNeedNotice).toBe(false);
        expect(localStorage.removeItem).toHaveBeenCalledWith("auth_user");
    }, 20000);
    it("應該從 localStorage 載入使用者資訊", () => {
        // 模擬 localStorage 已有使用者
        mockLocalStorage["auth_user"] = JSON.stringify({
            username: "admin",
            isStaff: true,
            isManager: true,
            DebtNeedNotice: true,
        });

        const { result } = renderHook(() => useAuth(), { wrapper });

        // 應自動載入使用者資訊
        expect(result.current.username).toBe("admin");
        expect(result.current.isStaff).toBe(true);
        expect(result.current.isManager).toBe(true);
        expect(result.current.DebtNeedNotice).toBe(true);
    }, 20000);
});
