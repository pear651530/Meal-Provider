import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginForm from "./pages/LoginForm";
import TodayMealsPage from "./pages/TodayMealsPage";
import RecordsPage from "./pages/RecordsPage";
import StaffOrderPage from "./pages/StaffOrderPage";
import MenuEditorPage from "./pages/MenuEditorPage";
import StaffDebtPage from "./pages/StaffDebtPage";
import StaffManagementPage from "./pages/StaffManagementPage";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
    return (
        <AuthProvider>
            <>
                <Routes>
                    <Route path="/" element={<LoginForm />} />
                    <Route
                        path="/login"
                        element={<Navigate to="/" replace />}
                    />
                    <Route path="/register" element={<Register />} />
                    <Route
                        path="/ForgotPassword"
                        element={<ForgotPassword />}
                    />
                    <Route
                        path="/TodayMeals"
                        element={
                            <ProtectedRoute>
                                <TodayMealsPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/records"
                        element={
                            <ProtectedRoute>
                                <RecordsPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/orders"
                        element={
                            <ProtectedRoute>
                                <StaffOrderPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/menuEditor"
                        element={
                            <ProtectedRoute>
                                <MenuEditorPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/staff-debt"
                        element={
                            <ProtectedRoute>
                                <StaffDebtPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/staff-management"
                        element={
                            <ProtectedRoute>
                                <StaffManagementPage />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </>
        </AuthProvider>
    );
}

export default App;
