import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // 匯入 context
import LanguageSwitcher from "../components/LanguageSwitcher"; // 匯入語言切換器
import { useTranslation } from "react-i18next";

function LoginForm() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const { t, i18n } = useTranslation();

    const navigate = useNavigate();
    const { login } = useAuth(); // 使用 context

    const handleLogin = async () => {
        if (!username || !password) {
            setMessage(t("請輸入帳號和密碼"));
            return;
        }
        try {
            const response = await fetch("http://localhost:8000/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username,
                    password,
                }),
            });
            if (!response.ok) {
                setMessage(t("帳號或密碼錯誤"));
                return;
            }
            const data = await response.json();
            localStorage.setItem("access_token", data.access_token);
            setMessage(t("登入成功！"));
            setTimeout(() => {
                navigate("/TodayMeals");
            }, 1000);
        } catch (error) {
            setMessage(t("登入時發生錯誤"));
        }
    };

    const handleRegister = () => {
        navigate("/Register"); // 導向註冊頁
    };

    const handleForgotPassword = () => {
        navigate("/ForgotPassword"); // 導向忘記密碼頁
    };

    return (
        <div
            style={{
                display: "flex",
                height: "100vh",
                width: "100vw",
                fontFamily: "Arial",
            }}
        >
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
            {/* 左側區域 */}
            <div
                style={{
                    flex: 2,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    borderRight: "1px solid #ccc",
                    backgroundColor: "#555555",
                }}
            >
                <p>{t("此處保留未來添加資訊")}</p>
            </div>

            {/* 右側登入區域 */}
            <div
                style={{
                    flex: 1,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    backgroundColor: "#333333",
                }}
            >
                <div
                    style={{
                        padding: "40px",
                        width: "100%",
                        color: "#ffffff",
                    }}
                >
                    <div style={{ marginBottom: "80px" }}></div>
                    <h2
                        style={{
                            textAlign: "center",
                            color: "#ffffff",
                            fontWeight: "bold",
                            letterSpacing: "10px",
                        }}
                    >
                        {t("員工登入")}
                    </h2>
                    <div style={{ marginBottom: "10px" }}></div>
                    <hr
                        style={{
                            border: "none",
                            borderTop: "2px solid #ffffff",
                            marginBottom: "40px",
                        }}
                    />

                    <input
                        type="text"
                        placeholder={t("帳號")}
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        style={{
                            display: "block",
                            marginBottom: "20px",
                            width: "100%",
                            padding: "12px",
                            border: "1px solid #555555",
                            borderRadius: "8px",
                            backgroundColor: "#444444",
                            color: "#ffffff",
                        }}
                    />

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
                            border: "1px solid #555555",
                            borderRadius: "8px",
                            backgroundColor: "#444444",
                            color: "#ffffff",
                        }}
                    />

                    <button
                        onClick={handleLogin}
                        style={{
                            width: "100%",
                            marginBottom: "10px",
                            padding: "12px",
                            backgroundColor: "#FFA500", // 亮橘色
                            color: "#ffffff",
                            border: "none",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        {t("登入")}
                    </button>
                    <button
                        onClick={handleRegister}
                        style={{
                            width: "100%",
                            marginBottom: "20px",
                            padding: "12px",
                            backgroundColor: "#6c757d",
                            color: "#ffffff",
                            border: "none",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        {t("註冊帳號")}
                    </button>

                    {message && (
                        <p
                            style={{
                                marginTop: "15px",
                                color: message.includes(t("成功"))
                                    ? "lightgreen"
                                    : "red",
                                textAlign: "center",
                            }}
                        >
                            {message}
                        </p>
                    )}

                    <div style={{ marginTop: "30px", textAlign: "center" }}>
                        {/*<button
                            onClick={handleForgotPassword}
                            style={{
                                padding: "10px 20px",
                                backgroundColor: "#6c757d",
                                color: "#ffffff",
                                border: "none",
                                borderRadius: "8px",
                                cursor: "pointer",
                            }}
                        >
                            {t("忘記密碼")}
                        </button>*/}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginForm;
