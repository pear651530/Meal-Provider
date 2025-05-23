import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next"; // 引入 i18n 的 hook
import LanguageSwitcher from "../components/LanguageSwitcher"; // 匯入語言切換器

function ForgotPassword() {
    const [email, setEmail] = useState("");
    const [message, setMessage] = useState("");
    const { t, i18n } = useTranslation();

    const navigate = useNavigate();

    const handleSendResetLink = () => {
        if (!email) {
            setMessage(t("請輸入電子郵件地址"));
            return;
        }

        // 模擬發送重設密碼連結
        setMessage(t("重設密碼的連結已發送至 {{email}}", { email }));
        console.log(t("重設密碼連結已發送至: {{email}}", { email })); // 模擬發送
    };

    return (
        <div
            style={{
                display: "flex",
                height: "100vh",
                width: "100vw",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: "Arial",
                backgroundColor: "#333333",
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
                    backgroundColor: "#ffffff",
                    borderRadius: "8px",
                    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
                }}
            >
                <h2
                    style={{
                        textAlign: "center",
                        color: "#333333",
                        fontWeight: "bold",
                        marginBottom: "20px",
                    }}
                >
                    {t("找回密碼")}
                </h2>

                <p
                    style={{
                        textAlign: "center",
                        color: "#666666",
                        marginBottom: "20px",
                    }}
                >
                    {t(
                        "請輸入您的電子郵件地址，我們將發送一封包含重設密碼連結的郵件給您。"
                    )}
                </p>

                <input
                    type="email"
                    placeholder={t("電子郵件")}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                        display: "block",
                        marginBottom: "20px",
                        width: "100%",
                        padding: "12px",
                        border: "1px solid #ccc",
                        borderRadius: "8px",
                    }}
                />

                <button
                    onClick={handleSendResetLink}
                    style={{
                        width: "100%",
                        padding: "12px",
                        backgroundColor: "#FFA500", // 亮橘色
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "8px",
                        cursor: "pointer",
                    }}
                >
                    {t("發送重設密碼連結")}
                </button>

                {message && (
                    <p
                        style={{
                            marginTop: "15px",
                            color: message.includes("已發送")
                                ? "lightgreen"
                                : "red",
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

export default ForgotPassword;
