import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "./StaffManagementPage.css";
import Navbar from "../components/NavBar";

interface User {
    id: number;
    username: string;
    role: string;
    created_at: string;
}

function StaffManagementPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { isSuperAdmin, token } = useAuth();
    const navigate = useNavigate();
    const { t } = useTranslation();

    useEffect(() => {
        // 獲取所有用戶
        const fetchUsers = async () => {
            try {
                const response = await fetch(
                    "http://localhost:8000/users/all",
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                // 過濾掉 super_admin 角色的用戶
                const filteredData = data.filter(
                    (user: User) => user.role !== "super_admin"
                );
                setUsers(filteredData);
                setLoading(false);
            } catch (err) {
                setError(err instanceof Error ? err.message : "發生未知錯誤");
                setLoading(false);
            }
        };

        fetchUsers();
    }, [isSuperAdmin, navigate, token]);

    const handleRoleChange = async (userId: number, newRole: string) => {
        try {
            const response = await fetch(
                `http://localhost:8000/users/${userId}/role?new_role=${newRole}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // 更新本地狀態
            setUsers(
                users.map((user) =>
                    user.id === userId ? { ...user, role: newRole } : user
                )
            );
        } catch (err) {
            setError(err instanceof Error ? err.message : "更新角色時發生錯誤");
        }
    };

    if (loading) {
        return (
            <>
                <Navbar />
                <div className="staff-management-container">
                    {t("載入中...")}
                </div>
            </>
        );
    }

    if (error) {
        return (
            <>
                <Navbar />
                <div className="staff-management-container">
                    {t("錯誤")}: {error}
                </div>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <div className="staff-management-container">
                <h1>{t("員工權限管理")}</h1>
                <table className="staff-table">
                    <thead>
                        <tr>
                            <th>{t("使用者名稱")}</th>
                            <th>{t("角色")}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id}>
                                <td>{user.username}</td>
                                <td>
                                    <select
                                        value={user.role}
                                        onChange={(e) =>
                                            handleRoleChange(
                                                user.id,
                                                e.target.value
                                            )
                                        }
                                        className="role-select"
                                    >
                                        <option value="employee">
                                            {t("一般員工")}
                                        </option>
                                        <option value="clerk">
                                            {t("店員")}
                                        </option>
                                        <option value="admin">
                                            {t("管理員")}
                                        </option>
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </>
    );
}

export default StaffManagementPage;
