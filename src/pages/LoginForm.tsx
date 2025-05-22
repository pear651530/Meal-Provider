import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // 匯入 context

function LoginForm() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    const navigate = useNavigate();
    const { login } = useAuth(); // 使用 context

    const handleLogin = () => {
        // 模擬帳號密碼驗證成功
        if (
            (username === "admin" || username === "alan" || username === "bob") &&
            password === "1234"
        ) {
            const user = login(username); // 設定全域登入狀態
            setMessage("登入成功！");
            setTimeout(() => {
                navigate("/TodayMeals");
                console.log(user?.DebtNeedNotice);
                if(user?.DebtNeedNotice) alert("尚有餘款未繳清!");
            }, 1000);
        } else {
            setMessage("帳號或密碼錯誤");
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
                <p>此處保留未來添加資訊</p>
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
                        員工登入
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
                        placeholder="帳號"
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
                        placeholder="密碼"
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
                            marginBottom: "20px",
                            padding: "12px",
                            backgroundColor: "#FFA500", // 亮橘色
                            color: "#ffffff",
                            border: "none",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        登入
                    </button>

                    {message && (
                        <p
                            style={{
                                marginTop: "15px",
                                color: message.includes("成功")
                                    ? "lightgreen"
                                    : "red",
                                textAlign: "center",
                            }}
                        >
                            {message}
                        </p>
                    )}

                    <div style={{ marginTop: "30px", textAlign: "center" }}>
                        <button
                            onClick={handleRegister}
                            style={{
                                marginRight: "10px",
                                padding: "10px 20px",
                                backgroundColor: "#6c757d",
                                color: "#ffffff",
                                border: "none",
                                borderRadius: "8px",
                                cursor: "pointer",
                            }}
                        >
                            註冊帳號
                        </button>
                        <button
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
                            忘記密碼
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginForm;
