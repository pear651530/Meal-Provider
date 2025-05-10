import { useEffect, useState } from "react";
import Navbar from "./NavBar";
import "./NavBar.css";
import "./TodayMealsPage.css";

interface Comment {
  recommended: boolean;
  text: string;
}

interface TodayMeal {
  id: number;
  name: string;
  price: number;
  image: string;
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
          image: "https://th.bing.com/th/id/OIP.vI5uFSdV9ZVyKuRVwWwEcgHaD4?w=294&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          comments: [
            { recommended: true, text: "很好吃！" },
            { recommended: false, text: "" },
          ],
        },
        {
          id: 2,
          name: "炒麵",
          price: 100,
          image: "https://th.bing.com/th/id/OIP.hlmjCiCqOGAmzUDobwU5YAHaFj?w=227&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          comments: [
            { recommended: true, text: "份量剛好" },
            { recommended: true, text: "" },
            { recommended: false, text: "太鹹了" },
          ],
        },
        {
          id: 3,
          name: "燒肉丼",
          price: 150,
          image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          comments: [
            { recommended: true, text: "份量超多" },
            { recommended: false, text: "份量太多" },
          ],
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) return <p>載入中...</p>;

  return (
    <div>
      <Navbar debtAmount={0} /> {}
      <div className="page-content"> {}
        <h2>🍽️ 今日餐點</h2>
        {meals.map((meal) => (
          <div
            key={meal.id}
            style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "15px" }}
          >
            <img src={meal.image} alt={meal.name} style={{ width: "100%", height: "auto", marginBottom: "10px" }} />
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
