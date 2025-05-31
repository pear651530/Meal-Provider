import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import $ from "jquery";
import "datatables.net";
import "datatables.net-dt/css/dataTables.dataTables.css";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";

interface Record {
    id: number;
    date: string; // Add date field
    meal: string;
    price: number;
    paid: boolean;
    rating?: "like" | "dislike"; // 評價欄位
    comment?: string; // 評價內容
}

function RecordsPage(): React.ReactElement {
    const { t, i18n } = useTranslation();
    const { user, token } = useAuth();
    const [records, setRecords] = useState<Record[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [activeRecordId, setActiveRecordId] = useState<number | null>(null);
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [currentComment, setCurrentComment] = useState("");

    // 嘗試從 user 物件中取得 user_id（後端 /users/me 回傳應有 user_id）
    useEffect(() => {
        if (!user || !token) return;
        // 兼容 user_id 或 id
        const userId = (user as any).user_id ?? (user as any).id;
        if (!userId) return;
        setLoading(true);
        fetch(`http://localhost:8000/users/${userId}/dining-records/`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                if (!res.ok) throw new Error("取得用餐紀錄失敗");
                return res.json();
            })
            .then(async (data) => {
                console.log("[DEBUG] dining-records API 回傳：", data); // 新增 log
                // 並行取得每筆紀錄的評論
                const recordsWithReviews = await Promise.all(
                    data.map(async (item: any) => {
                        let rating: "like" | "dislike" | undefined = undefined;
                        let comment: string | undefined = undefined;
                        try {
                            const res = await fetch(
                                `http://localhost:8000/dining-records/${item.order_id}/reviews/`,
                                {
                                    headers: {
                                        Authorization: `Bearer ${token}`,
                                    },
                                }
                            );
                            if (res.ok) {
                                const review = await res.json();
                                if (review.rating === "good") rating = "like";
                                if (review.rating === "bad") rating = "dislike";
                                comment = review.comment;
                            }
                        } catch (e) {
                            // 沒有評論或 API 失敗可忽略
                        }
                        return {
                            id: item.order_id,
                            date: new Date(
                                item.dining_date.endsWith("Z")
                                    ? item.dining_date
                                    : item.dining_date + "Z"
                            ).toLocaleString(undefined, {
                                year: "numeric",
                                month: "2-digit",
                                day: "2-digit",
                                hour: "2-digit",
                                minute: "2-digit",
                                hour12: false,
                            }),
                            meal: item.menu_item_name,
                            price: item.total_amount,
                            paid: item.payment_status === "paid",
                            rating,
                            comment,
                        };
                    })
                );
                setRecords(recordsWithReviews.sort((a, b) => b.id - a.id)); // 依 id 由大到小排序，最新在上
            })
            .catch((err) => {
                setRecords([]);
                alert("載入用餐紀錄失敗");
            })
            .finally(() => setLoading(false));
    }, [user, token]);

    useEffect(() => {
        // 初始化 DataTable
        if (records.length > 0) {
            $("#recordsTable").DataTable({
                ordering: true,
                columnDefs: [
                    {
                        orderable: true,
                        targets: 0,
                        className: "dt-center",
                        width: "20%",
                    }, // 點餐日期
                    {
                        orderable: true,
                        targets: 1,
                        className: "dt-center",
                        width: "30%",
                    }, // 餐點
                    {
                        orderable: true,
                        targets: 2,
                        className: "dt-center",
                        width: "20%",
                    }, // 價格
                    {
                        orderable: true,
                        targets: 3,
                        className: "dt-center",
                        width: "30%",
                    }, // 付款狀況
                    {
                        orderable: false,
                        targets: 4,
                        className: "dt-center",
                        width: "20%",
                    }, // 我的評價
                ],
                order: [], // 禁用預設排序
            });
        }

        // 清理 DataTable（避免重複初始化）
        return () => {
            if ($.fn.DataTable.isDataTable("#recordsTable")) {
                $("#recordsTable").DataTable().destroy();
            }
        };
    }, [records]);

    const debtAmount = records.reduce((sum, record) => {
        return record.paid ? sum : sum + record.price;
    }, 0);

    const nextPaymentDeadline = "2025-05-31"; // 假設下一次結帳期限

    const handleImmediatePayment = () => {
        alert(t("馬上結帳功能尚未實作！"));
    };

    // 修改 handleSaveComment，根據是否已有評論決定 POST/PUT，並讓 like/dislike 按鈕也能正確更新
    const handleSaveComment = async (
        id?: number,
        ratingType?: "like" | "dislike",
        commentText?: string
    ) => {
        const recordId = id ?? activeRecordId;
        if (recordId === null) return;
        const record = records.find((r) => r.id === recordId);
        if (!record) return;
        const rating =
            ratingType === "like"
                ? "good"
                : ratingType === "dislike"
                ? "bad"
                : record.rating === "like"
                ? "good"
                : record.rating === "dislike"
                ? "bad"
                : undefined;
        if (!rating) {
            alert(t("請先選擇喜歡或不喜歡"));
            return;
        }
        // 判斷是否已有評論（有評論就 PUT，否則 POST）
        const method =
            record.comment !== undefined && record.comment !== null
                ? "PUT"
                : "POST";
        const url = `http://localhost:8000/dining-records/${recordId}/reviews/`;
        try {
            const res = await fetch(url, {
                method,
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    rating,
                    comment: commentText ?? currentComment,
                }),
            });
            if (!res.ok) throw new Error("儲存評論失敗");
            const data = await res.json();
            setRecords((prev) =>
                prev.map((r) =>
                    r.id === recordId
                        ? {
                              ...r,
                              rating:
                                  data.rating === "good"
                                      ? "like"
                                      : data.rating === "bad"
                                      ? "dislike"
                                      : undefined,
                              comment: data.comment,
                          }
                        : r
                )
            );
            setShowCommentModal(false);
        } catch (err) {
            alert(t("儲存評論失敗"));
        }
    };

    if (loading) return <p>{t("載入中...")}</p>;

    return (
        <div>
            {showCommentModal && (
                <div
                    style={{
                        position: "fixed",
                        top: 0,
                        left: 0,
                        width: "100vw",
                        height: "100vh",
                        background: "rgba(0,0,0,0.3)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        zIndex: 9999,
                    }}
                    onClick={() => setShowCommentModal(false)}
                >
                    <div
                        style={{
                            background: "white",
                            padding: "24px",
                            borderRadius: "8px",
                            minWidth: "300px",
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3>{t("填寫評論")}</h3>
                        <textarea
                            value={currentComment}
                            onChange={(e) => setCurrentComment(e.target.value)}
                            rows={4}
                            style={{ width: "100%", marginBottom: "16px" }}
                        />
                        <div style={{ textAlign: "right" }}>
                            <button
                                onClick={() => setShowCommentModal(false)}
                                style={{ marginRight: "8px" }}
                            >
                                {t("取消")}
                            </button>
                            <button
                                onClick={() => handleSaveComment()}
                                style={{
                                    background: "#007bff",
                                    color: "white",
                                }}
                            >
                                {t("儲存")}
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <Navbar />
            <div
                style={{
                    padding: "20px",
                    fontFamily: "Arial",
                    marginTop: "60px",
                    width: "100vw",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                }}
            >
                <div style={{ width: "80vw" }}>
                    <h2>{t("歷史用餐紀錄")}</h2>
                    <table
                        id="recordsTable"
                        className="display"
                        style={{ width: "100%" }}
                    >
                        <thead>
                            <tr>
                                <th>{t("點餐日期")}</th>
                                <th>{t("餐點")}</th>
                                <th>{t("價格")}</th>
                                <th>{t("付款狀況")}</th>
                                <th>{t("我的評價")}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records.map((record) => (
                                <tr key={record.id}>
                                    <td>{record.date}</td>
                                    <td>{record.meal}</td>
                                    <td>
                                        {record.price} {t("元")}
                                    </td>
                                    <td
                                        style={{
                                            color: record.paid
                                                ? "green"
                                                : "red",
                                        }}
                                    >
                                        {record.paid
                                            ? t("已付款")
                                            : t("未付款")}
                                    </td>
                                    <td>
                                        <div
                                            style={{
                                                display: "flex",
                                                gap: "5px",
                                                justifyContent: "center",
                                                flexDirection: "column",
                                                alignItems: "center",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    display: "flex",
                                                    gap: "5px",
                                                    marginBottom: "5px",
                                                }}
                                            >
                                                <button
                                                    style={{
                                                        backgroundColor:
                                                            record.rating ===
                                                            "like"
                                                                ? "#4CAF50"
                                                                : "#f1f1f1",
                                                        color:
                                                            record.rating ===
                                                            "like"
                                                                ? "white"
                                                                : "black",
                                                        border: "none",
                                                        padding: "5px 10px",
                                                        borderRadius: "5px",
                                                    }}
                                                    onClick={async () => {
                                                        const updatedRecords =
                                                            records.map((r) =>
                                                                r.id ===
                                                                record.id
                                                                    ? {
                                                                          ...r,
                                                                          rating:
                                                                              r.rating ===
                                                                              "like"
                                                                                  ? undefined
                                                                                  : ("like" as "like"),
                                                                      }
                                                                    : r
                                                            );
                                                        setRecords(
                                                            updatedRecords
                                                        );
                                                        // 只有選擇 like 時才送出
                                                        if (
                                                            record.rating !==
                                                            "like"
                                                        ) {
                                                            await handleSaveComment(
                                                                record.id,
                                                                "like",
                                                                ""
                                                            );
                                                        }
                                                    }}
                                                    title={t("喜歡")}
                                                >
                                                    👍
                                                </button>
                                                <button
                                                    style={{
                                                        backgroundColor:
                                                            record.rating ===
                                                            "dislike"
                                                                ? "#f44336"
                                                                : "#f1f1f1",
                                                        color:
                                                            record.rating ===
                                                            "dislike"
                                                                ? "white"
                                                                : "black",
                                                        border: "none",
                                                        padding: "5px 10px",
                                                        borderRadius: "5px",
                                                    }}
                                                    onClick={async () => {
                                                        const updatedRecords =
                                                            records.map((r) =>
                                                                r.id ===
                                                                record.id
                                                                    ? {
                                                                          ...r,
                                                                          rating:
                                                                              r.rating ===
                                                                              "dislike"
                                                                                  ? undefined
                                                                                  : ("dislike" as "dislike"),
                                                                      }
                                                                    : r
                                                            );
                                                        setRecords(
                                                            updatedRecords
                                                        );
                                                        // 只有選擇 dislike 時才送出
                                                        if (
                                                            record.rating !==
                                                            "dislike"
                                                        ) {
                                                            await handleSaveComment(
                                                                record.id,
                                                                "dislike",
                                                                ""
                                                            );
                                                        }
                                                    }}
                                                    title={t("不喜歡")}
                                                >
                                                    👎
                                                </button>
                                            </div>
                                            {/* 只有選擇 like 或 dislike 才顯示填寫評論按鈕 */}
                                            {(record.rating === "like" ||
                                                record.rating ===
                                                    "dislike") && (
                                                <button
                                                    style={{
                                                        backgroundColor:
                                                            record.comment
                                                                ? "#4CAF50"
                                                                : "#007bff",
                                                        color: "white",
                                                        border: "none",
                                                        padding: "5px 10px",
                                                        borderRadius: "5px",
                                                        fontSize: "12px",
                                                        cursor: "pointer",
                                                        width: "100%",
                                                    }}
                                                    onClick={() => {
                                                        setActiveRecordId(
                                                            record.id
                                                        );
                                                        setShowCommentModal(
                                                            true
                                                        );
                                                        setCurrentComment(
                                                            record.comment || ""
                                                        );
                                                    }}
                                                >
                                                    {record.comment
                                                        ? t("已填寫")
                                                        : t("填寫評論")}
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
            {/* 固定在畫面下方的 bar */}
            <div
                style={{
                    position: "fixed",
                    bottom: 0,
                    left: 0,
                    width: "100%",
                    backgroundColor: "#333",
                    color: "white",
                    padding: "10px 20px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    boxShadow: "0 -2px 5px rgba(0, 0, 0, 0.2)",
                }}
            >
                <span>
                    {t("賒帳總額")}：${debtAmount}
                </span>
                <span>
                    {t("下一次結帳期限")}：{nextPaymentDeadline}
                </span>
                <button
                    onClick={handleImmediatePayment}
                    style={{
                        backgroundColor: "#ff5722",
                        color: "white",
                        border: "none",
                        padding: "10px 20px",
                        borderRadius: "5px",
                        cursor: "pointer",
                    }}
                >
                    {t("馬上結帳")}
                </button>
            </div>
        </div>
    );
}

export default RecordsPage;
