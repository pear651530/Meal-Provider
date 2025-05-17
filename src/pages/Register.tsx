import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
    const [employeeId, setEmployeeId] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [verificationCode, setVerificationCode] = useState("");
    const [generatedCode, setGeneratedCode] = useState("");
    const [message, setMessage] = useState("");
    const [isVerified, setIsVerified] = useState(false);

    const navigate = useNavigate();

    const handleSendVerificationCode = () => {
        if (!email) {
            setMessage("請輸入電子郵件以接收驗證碼");
            return;
        }

        const code = Math.floor(100000 + Math.random() * 900000).toString();
        setGeneratedCode(code);
        setMessage(`驗證碼已發送至 ${email}`);
        console.log(`驗證碼: ${code}`);
    };

    const handleVerifyCode = () => {
        if (verificationCode === generatedCode) {
            setIsVerified(true);
            setMessage("電子郵件驗證成功！");
        } else {
            setMessage("驗證碼錯誤，請重新輸入");
        }
    };

    const handleRegister = () => {
        if (!employeeId || !email || !password || !confirmPassword) {
            setMessage("請填寫所有欄位");
            return;
        }

        if (password !== confirmPassword) {
            setMessage("密碼與確認密碼不一致");
            return;
        }

        if (!isVerified) {
            setMessage("請先完成電子郵件驗證");
            return;
        }

        setMessage("註冊成功！即將跳轉至登入頁面");
        setTimeout(() => {
            navigate("/Login");
        }, 2000);
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
                backgroundColor: "#1e1e1e", // Dark background
                color: "#e0e0e0", // Light text for dark background
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
                    color: "#ff8c00", // Keeping orange accent
                    cursor: "pointer",
                    fontSize: "16px",
                }}
            >
                返回登入頁
            </button>

            <div
                style={{
                    padding: "40px",
                    width: "100%",
                    maxWidth: "400px",
                    backgroundColor: "#2d2d2d", // Dark card background
                    borderRadius: "8px",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.3)",
                }}
            >
                <h2
                    style={{
                        textAlign: "center",
                        color: "#ff8c00", // Keeping orange accent
                        fontWeight: "bold",
                        marginBottom: "20px",
                    }}
                >
                    註冊帳號
                </h2>

                <input
                    type="text"
                    placeholder="員工號"
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a", // Dark input background
                        color: "#e0e0e0", // Light text
                    }}
                />

                <input
                    type="email"
                    placeholder="電子郵件"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a", // Dark input background
                        color: "#e0e0e0", // Light text
                    }}
                />

                <div style={{ display: "flex", marginBottom: "20px" }}>
                    <input
                        type="text"
                        placeholder="驗證碼"
                        value={verificationCode}
                        onChange={(e) => setVerificationCode(e.target.value)}
                        style={{
                            flex: 1.618,
                            padding: "8px",
                            border: "1px solid #444444",
                            borderRadius: "8px",
                            marginRight: "10px",
                            backgroundColor: "#3a3a3a", // Dark input background
                            color: "#e0e0e0", // Light text
                        }}
                    />
                    <button
                        onClick={handleSendVerificationCode}
                        style={{
                            flex: 1,
                            padding: "8px",
                            backgroundColor: "#ff8c00", // Keeping orange accent
                            color: "#ffffff",
                            border: "none",
                            borderRadius: "8px",
                            cursor: "pointer",
                        }}
                    >
                        發送驗證碼
                    </button>
                </div>

                <button
                    onClick={handleVerifyCode}
                    style={{
                        width: "100%",
                        marginBottom: "20px",
                        padding: "12px",
                        backgroundColor: "#4a4a4a", // Darker button
                        color: "#e0e0e0", // Light text
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                    }}
                >
                    驗證電子郵件
                </button>

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
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a", // Dark input background
                        color: "#e0e0e0", // Light text
                    }}
                />

                <input
                    type="password"
                    placeholder="確認密碼"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #444444",
                        borderRadius: "8px",
                        backgroundColor: "#3a3a3a", // Dark input background
                        color: "#e0e0e0", // Light text
                    }}
                />

                <button
                    onClick={handleRegister}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#ff8c00", // Keeping orange accent
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                    }}
                >
                    註冊
                </button>

                {message && (
                    <p
                        style={{
                            marginTop: "15px",
                            color: message.includes("成功")
                                ? "#6dff6d" // Lighter green for dark theme
                                : "#ff6b6b", // Lighter red for dark theme
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
