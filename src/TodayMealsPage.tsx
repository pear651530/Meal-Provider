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
  todayMeal: boolean;
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
          todayMeal: true,
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
          todayMeal: false,
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
          todayMeal: true,
          comments: [
            { recommended: true, text: "份量超多" },
            { recommended: false, text: "份量太多" },
          ],
        },
        {
          id: 4,
          name: "燒肉丼",
          price: 150,
          image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          todayMeal: true,
          comments: [
            { recommended: true, text: "份量超多" },
            { recommended: false, text: "份量太多" },
          ],
        },
        {
          id: 5,
          name: "燒肉丼",
          price: 150,
          image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          todayMeal: true,
          comments: [
            { recommended: true, text: "份量超多" },
            { recommended: false, text: "份量太多" },
          ],
        },
        {
          id: 6,
          name: "燒肉丼",
          price: 150,
          image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
          todayMeal: true,
          comments: [
            { recommended: true, text: "份量超多" },
            { recommended: false, text: "份量太多" },
          ],
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) return <p className="loading">載入中...</p>;

  return (
    <div>
      <Navbar debtAmount={0}/>
      <div className="page-content">
        <h2 className="page-title">🍽️ 今日餐點</h2>
        <div className="meal-list">
          {meals
            .filter((meal) => meal.todayMeal)
            .map((meal) => (
              <div key={meal.id} className="today-meal-card">
                <img src={meal.image} alt={meal.name} className="meal-image" />
                <div className="meal-info">
                  <h3>{meal.name} <span className="meal-price">{meal.price} 元</span></h3>
                  <ul className="comment-list">
                    {meal.comments.map((comment, index) => (
                      <li key={index} className={comment.recommended ? "recommended" : "not-recommended"}>
                        {comment.recommended ? "👍 推薦" : "👎 不推薦"}
                        {comment.text && `：${comment.text}`}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

export default TodayMealsPage;
