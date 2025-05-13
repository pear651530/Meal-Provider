import { useEffect, useState } from "react";
import Navbar from "./NavBar";
import $ from "jquery";
import "datatables.net";
import "datatables.net-dt/css/dataTables.dataTables.css";
import "./NavBar.css";

interface Record {
    id: number;
    date: string; // Add date field
    meal: string;
    price: number;
    paid: boolean;
}

function RecordsPage(): JSX.Element {
    const [records, setRecords] = useState<Record[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

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
        alert("馬上結帳功能尚未實作！");
    };

    if (loading) return <p>載入中...</p>;

    return (
        <div>
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
                    <h2>🍱 歷史用餐紀錄</h2>
                    <table
                        id="recordsTable"
                        className="display"
                        style={{ width: "100%" }}
                    >
                        <thead>
                            <tr>
                                <th>點餐日期</th>
                                <th>餐點</th>
                                <th>價格</th>
                                <th>付款狀況</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records.map((record) => (
                                <tr key={record.id}>
                                    <td>{record.date}</td>
                                    <td>{record.meal}</td>
                                    <td>{record.price} 元</td>
                                    <td>
                                        {record.paid
                                            ? "✅ 已付款"
                                            : "❌ 未付款"}
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
                <span>賒帳總額：${debtAmount}</span>
                <span>下一次結帳期限：{nextPaymentDeadline}</span>
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
                    馬上結帳
                </button>
            </div>
        </div>
    );
}

export default RecordsPage;
