import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./pages/LoginForm";
import TodayMealsPage from "./pages/TodayMealsPage";
import RecordsPage from "./pages/RecordsPage";
import StaffOrderPage from "./pages/StaffOrderPage";
import MenuEditorPage from "./pages/MenuEditorPage";
import StaffDebtPage from "./pages/StaffDebtPage";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import { AuthProvider } from "./context/AuthContext";

function App() {
    return (
        <AuthProvider>
        <>
            <Routes>
                <Route path="/" element={<LoginForm />} />
                <Route path="/login" element={<Navigate to="/" replace />} />
                <Route path="/register" element={<Register />} />
                <Route path="/ForgotPassword" element={<ForgotPassword />} />
                <Route path="/TodayMeals" element={<TodayMealsPage />} />
                <Route path="/records" element={<RecordsPage />} />
                <Route path="/orders" element={<StaffOrderPage />} />
                <Route path="/menuEditor" element={<MenuEditorPage />} />
                <Route path="/staff-debt" element={<StaffDebtPage />} />
            </Routes>
        </>
        </AuthProvider>
    );
}

export default App;
