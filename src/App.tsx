import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./LoginForm";
import TodayMealsPage from "./TodayMealsPage";
import RecordsPage from "./RecordsPage";
import StaffOrderPage from "./StaffOrderPage";
import MenuEditorPage from "./MenuEditorPage";
import StaffDebtPage from "./StaffDebtPage";
import Register from "./Register";
import ForgotPassword from "./ForgotPassword";
import "./NavBar.css";

function App() {
    return (
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
    );
}

export default App;
