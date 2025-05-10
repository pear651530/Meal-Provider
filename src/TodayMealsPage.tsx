import { useEffect, useState } from "react";
import Navbar from "./NavBar";
import "./NavBar.css";

interface Comment {
  recommended: boolean;
  text: string;
}

interface TodayMeal {
  id: number;
  name: string;
  price: number;
  comments: Comment[];
}

function TodayMealsPage(): JSX.Element {
  const [meals, setMeals] = useState<TodayMeal[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // 模擬載入資料
    setTimeout(() => {
      setMeals([
        {
          id: 1,
          name: "咖哩飯",
          price: 120,
          comments: [
            { recommended: true, text: "很好吃！" },
            { recommended: false, text: "" },
          ],
        },
        {
          id: 2,
          name: "炒麵",
          price: 100,
          comments: [
            { recommended: true, text: "份量剛好" },
            { recommended: true, text: "" },
            { recommended: false, text: "太鹹了" },
          ],
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) return <p>載入中...</p>;

  return (
    <div>
      <Navbar debtAmount={0} /> {/* 這頁暫時不顯示賒帳金額 */}
      <div style={{ padding: "20px", fontFamily: "Arial" }}>
        <h2>🍽️ 今日餐點</h2>
        {meals.map((meal) => (
          <div key={meal.id} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "15px" }}>
            <h3>{meal.name} - {meal.price} 元</h3>
            <ul>
              {meal.comments.map((comment, index) => (
                <li key={index}>
                  {comment.recommended ? "👍 推薦" : "👎 不推薦"}
                  {comment.text && `：${comment.text}`}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TodayMealsPage;
