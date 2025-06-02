import { useState } from "react";
import { useNavigate } from "react-router-dom";
import LanguageSwitcher from "../components/LanguageSwitcher";
import { useTranslation } from "react-i18next"; // 匯入 translation hook
import { getApiUrl } from '../config/api';

function Register() {
    const { t } = useTranslation(); // 使用 translation hook
    const [employeeId, setEmployeeId] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    // const [isValidEmployee, setIsValidEmployee] = useState(false);

    const navigate = useNavigate();

    // const handleCheckEmployeeId = async () => {
    //     if (!employeeId) {
    //         setMessage(t("請輸入員工號"));
    //         return;
    //     }

    //     try {
    //         // Replace with your actual API endpoint
    //         const response = await fetch(
    //             `http://localhost:8000/api/check-employee/${employeeId}`,
    //             {
    //                 method: "GET",
    //                 headers: {
    //                     "Content-Type": "application/json",
    //                 },
    //             }
    //         );
    //         const data = await response.json();

    //         if (data.exists) {
    //             setIsValidEmployee(true);
    //             setMessage(t("員工號驗證成功！"));
    //         } else {
    //             setMessage(t("無效的員工號，請確認後重試"));
    //             setIsValidEmployee(false);
    //         }
    //     } catch (error) {
    //         console.error(t("驗證員工號時出錯:"), error);
    //         setMessage(t("驗證員工號時發生錯誤，請稍後再試"));
    //     }
    // };

    const handleRegister = async () => {
        if (!employeeId || !password || !confirmPassword) {
            setMessage(t("請填寫所有欄位"));
            return;
        }

        if (password !== confirmPassword) {
            setMessage(t("密碼與確認密碼不一致"));
            return;
        }

        // if (!isValidEmployee) {
        //     setMessage(t("請先驗證員工號"));
        //     return;
        // }

        try {
            const response = await fetch(getApiUrl('USER_SERVICE', '/users/'), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    username: employeeId,
                    password: password,
                }),
            });
            if (!response.ok) {
                setMessage(t("註冊失敗，請稍後再試"));
                return;
            }
            setMessage(t("註冊成功！即將跳轉至登入頁面"));
            setTimeout(() => {
                navigate("/Login");
            }, 2000);
        } catch (error) {
            setMessage(t("註冊時發生錯誤"));
        }
    };

    // 登入取得 token
    const handleGetToken = async () => {
        if (!employeeId || !password) {
            setMessage(t("請輸入員工號和密碼"));
            return;
        }
        try {
            const response = await fetch(getApiUrl('USER_SERVICE', '/token'), {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username: employeeId,
                    password: password,
                }),
            });
            if (!response.ok) {
                setMessage(t("登入失敗，請檢查帳號密碼"));
                return;
            }
            const data = await response.json();
            setMessage("Token: " + data.access_token);
            // 你可以把 token 存到 localStorage 或 context
            // localStorage.setItem('token', data.access_token);
        } catch (error) {
            setMessage(t("取得 token 時發生錯誤"));
        }
    };

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100vh",
                width: "100vw",
                fontFamily: "Arial",
                backgroundColor: "#1e1e1e",
                color: "#e0e0e0",
            }}
        >
            <button
                onClick={() => navigate("/Login")}
                style={{
                    position: "absolute",
                    top: "20px",
                    left: "20px",
                    background: "none",
                    border: "none",
                    color: "#ff8c00",
                    cursor: "pointer",
                    fontSize: "16px",
                }}
            >
                {t("返回登入頁")}
            </button>

            {/* 語言切換器 */}
            <div
                style={{
                    position: "absolute",
                    top: "20px",
                    right: "20px",
                    zIndex: 1000,
                }}
            >
                <LanguageSwitcher />
            </div>

            <div
                style={{
                    padding: "40px",
                    width: "100%",
                    maxWidth: "400px",
                    backgroundColor: "#2d2d2d",
                    borderRadius: "8px",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
                }}
            >
                <h2
                    style={{
                        textAlign: "center",
                        color: "#ff8c00",
                        fontWeight: "bold",
                        marginBottom: "20px",
                    }}
                >
                    {t("註冊帳號")}
                </h2>

                <div style={{ display: "flex", marginBottom: "20px" }}>
                    <input
                        type="text"
                        placeholder={t("員工號")}
                        value={employeeId}
                        onChange={(e) => setEmployeeId(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "12px",
                            border: "1px solid #444444",
                            borderRadius: "8px",
                            // marginRight: "10px",
                            backgroundColor: "#3a3a3a",
                            color: "#e0e0e0",
                        }}
                    />
                    {/*
                    <button
                        // onClick={handleCheckEmployeeId}
                        style={{
                            width: "35%",
                            padding: "8px",
                            backgroundColor: "#ff8c00",
                            color: "#ffffff",
                            border: "none",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        {t("驗證員工號")}
                    </button>
                    */}
                </div>

                <input
                    type="password"
                    placeholder={t("密碼")}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a",
                        color: "#e0e0e0",
                    }}
                />

                <input
                    type="password"
                    placeholder={t("確認密碼")}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a",
                        color: "#e0e0e0",
                    }}
                />

                <button
                    onClick={handleRegister}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#ff8c00",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                    }}
                >
                    {t("註冊")}
                </button>
                {/*<button
                    onClick={handleGetToken}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#007bff",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                        marginTop: "10px",
                    }}
                >
                    取得 Token (測試)
                </button>
                <button
                    onClick={async () => {
                        if (!employeeId || !password) {
                            setMessage(t("請輸入員工號和密碼"));
                            return;
                        }
                        try {
                            const response = await fetch(
                                "http://localhost:8000/users/",
                                {
                                    method: "POST",
                                    headers: {
                                        "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify({
                                        username: employeeId,
                                        password: password,
                                    }),
                                }
                            );
                            if (!response.ok) {
                                setMessage(t("建立帳號失敗"));
                                return;
                            }
                            setMessage(t("建立帳號成功"));
                        } catch (error) {
                            setMessage(t("建立帳號時發生錯誤"));
                        }
                    }}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#28a745",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                        marginTop: "10px",
                    }}
                >
                    建立帳號 (測試)
                </button>*/}

                {message && (
                    <p
                        style={{
                            marginTop: "15px",
                            color: message.includes(t("成功"))
                                ? "#6dff6d"
                                : "#ff6b6b",
                            textAlign: "center",
                        }}
                    >
                        {message}
                    </p>
                )}
            </div>
        </div>
    );
}

export default Register;