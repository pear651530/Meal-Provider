import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import $ from "jquery";
import "datatables.net";
import "datatables.net-dt/css/dataTables.dataTables.css";
import { useTranslation } from "react-i18next";

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
    const [records, setRecords] = useState<Record[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [activeRecordId, setActiveRecordId] = useState<number | null>(null);
    const [showCommentModal, setShowCommentModal] = useState(false);
    const [currentComment, setCurrentComment] = useState("");

    useEffect(() => {
        // 模擬載入資料
        setTimeout(() => {
            setRecords([
                {
                    id: 1,
                    date: "2023-10-01",
                    meal: "咖哩飯",
                    price: 120,
                    paid: true,
                    rating: "like",
                },
                {
                    id: 2,
                    date: "2023-10-02",
                    meal: "便當",
                    price: 100,
                    paid: false,
                },
                {
                    id: 3,
                    date: "2023-10-03",
                    meal: "燒肉丼",
                    price: 150,
                    paid: true,
                    rating: "dislike",
                },
            ]);
            setLoading(false);
        }, 1000);
    }, []);

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
                                onClick={() => {
                                    // 儲存評論到對應的 record
                                    if (activeRecordId !== null) {
                                        setRecords((records) =>
                                            records.map((r) =>
                                                r.id === activeRecordId
                                                    ? {
                                                          ...r,
                                                          comment:
                                                              currentComment,
                                                      }
                                                    : r
                                            )
                                        );
                                    }
                                    setShowCommentModal(false);
                                }}
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
                                                {record.rating ? (
                                                    <>
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
                                                                padding:
                                                                    "5px 10px",
                                                                borderRadius:
                                                                    "5px",
                                                            }}
                                                            onClick={() => {
                                                                const updatedRecords =
                                                                    records.map(
                                                                        (r) =>
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
                                                                padding:
                                                                    "5px 10px",
                                                                borderRadius:
                                                                    "5px",
                                                            }}
                                                            onClick={() => {
                                                                const updatedRecords =
                                                                    records.map(
                                                                        (r) =>
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
                                                            }}
                                                            title={t("不喜歡")}
                                                        >
                                                            👎
                                                        </button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button
                                                            style={{
                                                                backgroundColor:
                                                                    "#f1f1f1",
                                                                color: "black",
                                                                border: "none",
                                                                padding:
                                                                    "5px 10px",
                                                                borderRadius:
                                                                    "5px",
                                                            }}
                                                            onClick={() => {
                                                                const updatedRecords =
                                                                    records.map(
                                                                        (r) =>
                                                                            r.id ===
                                                                            record.id
                                                                                ? {
                                                                                      ...r,
                                                                                      rating: "like" as "like",
                                                                                  }
                                                                                : r
                                                                    );
                                                                setRecords(
                                                                    updatedRecords
                                                                );
                                                            }}
                                                            title={t("喜歡")}
                                                        >
                                                            👍
                                                        </button>
                                                        <button
                                                            style={{
                                                                backgroundColor:
                                                                    "#f1f1f1",
                                                                color: "black",
                                                                border: "none",
                                                                padding:
                                                                    "5px 10px",
                                                                borderRadius:
                                                                    "5px",
                                                            }}
                                                            onClick={() => {
                                                                const updatedRecords =
                                                                    records.map(
                                                                        (r) =>
                                                                            r.id ===
                                                                            record.id
                                                                                ? {
                                                                                      ...r,
                                                                                      rating: "dislike" as "dislike",
                                                                                  }
                                                                                : r
                                                                    );
                                                                setRecords(
                                                                    updatedRecords
                                                                );
                                                            }}
                                                            title={t("不喜歡")}
                                                        >
                                                            👎
                                                        </button>
                                                    </>
                                                )}
                                            </div>
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
                                                    // Show comment modal for this record
                                                    setActiveRecordId(
                                                        record.id
                                                    );
                                                    setShowCommentModal(true);
                                                    setCurrentComment(
                                                        record.comment || ""
                                                    );
                                                }}
                                            >
                                                {record.comment
                                                    ? t("已填寫")
                                                    : t("填寫評論")}
                                            </button>
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
