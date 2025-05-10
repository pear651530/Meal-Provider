import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./LoginForm";
import TodayMealsPage from "./TodayMealsPage";
import RecordsPage from "./RecordsPage";
import "./NavBar.css";

function App() {
    return (
        <>
            <Routes>
                <Route path="/" element={<LoginForm />} />
                <Route path="/TodayMeals" element={<TodayMealsPage />} />
                <Route path="/records" element={<RecordsPage />} />
            </Routes>
        </>
    );
}

export default App;
