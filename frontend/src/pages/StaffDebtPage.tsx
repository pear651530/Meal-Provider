import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import "datatables.net";
import "datatables.net-dt/css/dataTables.dataTables.css";
import $ from "jquery";
import "./StaffDebtPage.css";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext"; // Import useAuth

interface StaffDebt {
    id: number;
    name: string;
    debt: number;
}

const StaffDebtPage: React.FC = () => {
    const { t, i18n } = useTranslation();
    const [staffDebts, setStaffDebts] = useState<StaffDebt[]>([]);
    const { token } = useAuth(); // Get token from useAuth

    useEffect(() => {
        // 取得賒帳狀況資料
        const fetchStaffDebts = async () => {
            try {
                const res = await fetch("http://localhost:8002/users/unpaid", {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                if (!res.ok) throw new Error("無法取得賒帳資料");
                const data = await res.json();
                console.log("Staff debts data:", data);
                // 依據 API 回傳格式 mapping
                // [{ user_id, user_name, unpaidAmount }]
                setStaffDebts(
                    data
                        .filter((staff: any) => staff.unpaidAmount > 0)
                        .map((staff: any) => ({
                            id: staff.user_id,
                            name: staff.user_name,
                            debt: staff.unpaidAmount,
                        }))
                );
            } catch (err) {
                setStaffDebts([]);
                alert(t("載入賒帳資料失敗"));
            }
        };
        fetchStaffDebts();
    }, [token]);

    useEffect(() => {
        // 初始化 DataTable
        if (staffDebts.length > 0) {
            $("#staffDebtTable").DataTable({
                ordering: true, // 啟用排序功能（全局）
                columnDefs: [
                    { orderable: true, targets: 0, className: "text-center" }, // 員工ID
                    { orderable: true, targets: 1, className: "text-left" }, // 員工名稱
                    { orderable: true, targets: 2, className: "text-left" }, // 賒帳金額
                ],
                order: [], // 禁用預設排序（不顯示箭頭）
            });
        }

        // 清理 DataTable（避免重複初始化）
        return () => {
            if ($.fn.DataTable.isDataTable("#staffDebtTable")) {
                $("#staffDebtTable").DataTable().destroy();
            }
        };
    }, [staffDebts]);

    return (
        <div style={{ width: "100vw", marginTop: "60px" }}>
            <Navbar />
            <div style={{ padding: "20px", width: "80vw", margin: "0 auto" }}>
                <h1>{t("員工賒帳狀況")}</h1>
                <table
                    id="staffDebtTable"
                    className="display"
                    style={{ width: "100%" }}
                >
                    <thead>
                        <tr>
                            <th>{t("員工ID")}</th>
                            <th>{t("員工名稱")}</th>
                            <th>{t("賒帳金額")}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {staffDebts.map((staff) => (
                            <tr key={staff.id}>
                                <td>{staff.id}</td>
                                <td>{staff.name}</td>
                                <td>${staff.debt}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button
                    onClick={async () => {
                        try {
                            const res = await fetch(
                                "http://localhost:8002/billing-notifications/send",
                                {
                                    method: "POST",
                                    headers: {
                                        Authorization: `Bearer ${token}`,
                                    },
                                }
                            );
                            if (!res.ok) throw new Error("通知發送失敗");
                            alert(t("已發送通知給所有員工"));
                        } catch (err) {
                            alert(t("通知發送失敗，請稍後再試"));
                        }
                    }}
                    style={{
                        marginTop: "10px",
                        padding: "10px 20px",
                        backgroundColor: "red",
                        color: "white",
                        border: "none",
                        cursor: "pointer",
                    }}
                >
                    {t("一鍵通知所有員工")}
                </button>
            </div>
        </div>
    );
};

export default StaffDebtPage;
