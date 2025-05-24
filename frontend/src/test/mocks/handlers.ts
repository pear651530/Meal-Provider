// src/test/mocks/handlers.ts
// 這個文件包含測試所需的模擬處理程序

// 模擬 react-router-dom
export const mockReactRouter = () => {
    // 保存真實的 react-router-dom 模組
    const originalModule = jest.requireActual('react-router-dom');
    
    return {
        ...originalModule,
        // 模擬 useLocation，默認返回非首頁的位置
        useLocation: jest.fn().mockImplementation(() => ({
            pathname: '/TodayMeals'
        })),
        // 模擬 useNavigate
        useNavigate: jest.fn().mockImplementation(() => jest.fn())
    };
};

// 創建一個模擬 useAuth 的函數
export const mockUseAuth = (isStaff = false, isManager = false) => {
    return {
        username: "testUser",
        isStaff,
        isManager,
        DebtNeedNotice: false,
        login: jest.fn(),
        logout: jest.fn()
    };
};
