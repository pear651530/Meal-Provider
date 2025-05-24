// src/test/utils.tsx
import { ReactNode } from "react";
import { render as rtlRender } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import i18n from "../i18n";
import { AuthProvider } from "../context/AuthContext";

// 確保測試開始前重置 i18n 實例狀態
i18n.init();

export const renderWithProviders = (
    ui: React.ReactElement,
    {
        route = "/",
        initialEntries,
        ...renderOptions
    }: { route?: string; initialEntries?: string[]; [key: string]: any } = {
        initialEntries: ["/"],
    }
) => {
    const Wrapper = ({ children }: { children: ReactNode }) => (
        <I18nextProvider i18n={i18n}>
            <AuthProvider>
                <MemoryRouter initialEntries={initialEntries}>
                    <Routes>
                        <Route path="*" element={children} />
                    </Routes>
                </MemoryRouter>
            </AuthProvider>
        </I18nextProvider>
    );

    return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
};

export const i18nForTest = i18n;
