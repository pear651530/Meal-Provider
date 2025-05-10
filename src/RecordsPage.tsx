import { useEffect, useState } from "react";
import Navbar from "./NavBar";
import "./NavBar.css";

interface Record {
    id: number;
    meal: string;
    price: number;
    paid: boolean;
}

function RecordsPage(): JSX.Element {
    const [records, setRecords] = useState<Record[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        setTimeout(() => {
            setRecords([
                { id: 1, meal: "咖哩飯", price: 120, paid: true },
                { id: 2, meal: "便當", price: 100, paid: false },
                { id: 3, meal: "燒肉丼", price: 150, paid: true },
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const debtAmount = records.reduce((sum, record) => {
        return record.paid ? sum : sum + record.price;
    }, 0);

    if (loading) return <p>載入中...</p>;

    return (
        <div>
            <Navbar debtAmount={debtAmount} />
            <div style={{ padding: "20px", fontFamily: "Arial" }}>
                <h2>🍱 歷史用餐紀錄</h2>
                <table border={1} cellPadding="10">
                    <thead>
                        <tr>
                            <th>餐點</th>
                            <th>價格</th>
                            <th>付款狀況</th>
                        </tr>
                    </thead>
                    <tbody>
                        {records.map((record) => (
                            <tr key={record.id}>
                                <td>{record.meal}</td>
                                <td>{record.price} 元</td>
                                <td>
                                    {record.paid ? "✅ 已付款" : "❌ 未付款"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default RecordsPage;
