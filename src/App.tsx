import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./LoginForm";
import TodayMealsPage from "./TodayMealsPage";
import RecordsPage from "./RecordsPage";
import StaffOrderPage from "./StaffOrderPage";
import "./NavBar.css";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<LoginForm />} />
                <Route path="/TodayMeals" element={<TodayMealsPage />} />
                <Route path="/records" element={<RecordsPage />} />
                <Route path="/orders" element={<StaffOrderPage />} />
            </Routes>
        </>
    );
}

export default App;
