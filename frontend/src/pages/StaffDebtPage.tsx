import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import "datatables.net";
import "datatables.net-dt/css/dataTables.dataTables.css";
import $ from "jquery";
import "./StaffDebtPage.css";
import { useTranslation } from "react-i18next";

interface StaffDebt {
    id: number;
    name: string;
    debt: number;
}

const StaffDebtPage: React.FC = () => {
    const { t, i18n } = useTranslation();
    const [staffDebts, setStaffDebts] = useState<StaffDebt[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    useEffect(() => {
        // Fetch staff debt data from an API or mock data
        const fetchStaffDebts = async () => {
            const mockData: StaffDebt[] = [
                { id: 1, name: "Alice", debt: 120 },
                { id: 2, name: "Bob", debt: 80 },
                { id: 3, name: "Charlie", debt: 0 },
            ];
            // Filter out staff with zero debt before setting state
            const filteredData = mockData.filter((staff) => staff.debt > 0);
            setStaffDebts(filteredData);
        };

        fetchStaffDebts();
    }, []);

    useEffect(() => {
        // 初始化 DataTable
        if (staffDebts.length > 0) {
            $("#staffDebtTable").DataTable({
                ordering: true, // 啟用排序功能（全局）
                columnDefs: [
                    {
                        orderable: false,
                        targets: 0,
                        width: "100px",
                        className: "text-center",
                    }, // 禁用第一列的排序功能
                    { orderable: true, targets: 1, className: "text-center" }, // 員工ID
                    { orderable: true, targets: 2, className: "text-left" }, // 員工名稱
                    { orderable: true, targets: 3, className: "text-left" }, // 賒帳金額
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

    // 全選/取消全選功能
    const toggleSelectAll = () => {
        if (selectedIds.length === staffDebts.length) {
            setSelectedIds([]); // 取消全選
        } else {
            setSelectedIds(staffDebts.map((staff) => staff.id)); // 全選
        }
    };

    // 單選功能
    const toggleSelect = (id: number) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((sid) => sid !== id) : [...prev, id]
        );
    };

    // 預警選取員工功能
    const alertSelectedStaff = () => {
        alert(t("選取的員工 ID: {{ids}}", { ids: selectedIds.join(", ") }));
    };

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
                            <th>
                                <label
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "5px",
                                    }}
                                >
                                    <input
                                        type="checkbox"
                                        checked={
                                            selectedIds.length ===
                                            staffDebts.length
                                        }
                                        onChange={toggleSelectAll}
                                    />
                                    <span>{t("全選")}</span>
                                </label>
                            </th>
                            <th>{t("員工ID")}</th>
                            <th>{t("員工名稱")}</th>
                            <th>{t("賒帳金額")}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {staffDebts.map((staff) => (
                            <tr key={staff.id}>
                                <td>
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.includes(staff.id)}
                                        onChange={() => toggleSelect(staff.id)}
                                    />
                                </td>
                                <td>{staff.id}</td>
                                <td>{staff.name}</td>
                                <td>${staff.debt}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button
                    onClick={alertSelectedStaff}
                    style={{
                        marginTop: "10px",
                        padding: "10px 20px",
                        backgroundColor: "red",
                        color: "white",
                        border: "none",
                        cursor: "pointer",
                    }}
                >
                    {t("預警選取員工")}
                </button>
            </div>
        </div>
    );
};

export default StaffDebtPage;
