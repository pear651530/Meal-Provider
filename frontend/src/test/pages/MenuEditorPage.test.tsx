import { render, screen } from "@testing-library/react";
import { AuthContext, AuthContextType } from "../../context/AuthContext";
import MenuEditorPage from "../../pages/MenuEditorPage";
import React from "react";
import { vi } from "vitest";
import i18n from "../../i18n";
import { MemoryRouter } from "react-router-dom";

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

// ✅ 測試前 mock fetch
beforeEach(() => {
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/menu-items")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                id: 1,
                zh_name: "白飯",   // 這裡是 zh_name，不是 name
                en_name: "Rice",
                url: "https://via.placeholder.com/100",
                price: 30,
                is_available: true,
              },
            ]),
        });
      }
  
      if (url.includes("/ratings/")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              total_reviews: 3,
              good_reviews: 2,
            }),
        });
      }
  
      // default mock response
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      });
    });
  });
  

afterEach(() => {
    vi.resetAllMocks();
});

test("should fetch and display meals", async () => {
    render(
        <MemoryRouter>
            <AuthContext.Provider value={mockAuthContextValue}>
                <MenuEditorPage />
            </AuthContext.Provider>
        </MemoryRouter>
    );

    // ✅ 等待餐點名稱出現
    const meal = await screen.findByText("白飯");
    expect(meal).toBeInTheDocument();
});
