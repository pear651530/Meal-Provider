import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import Navbar from "../components/NavBar";
import "./TodayMealsPage.css";
import { useAuth } from "../context/AuthContext";

interface Comment {
    recommended: string;
    text: string;
}

interface TodayMeal {
    id: number;
    name: string;
    englishName?: string;
    price: number;
    image: string;
    todayMeal: boolean;
    comments: Comment[];
}

function TodayMealsPage(): React.ReactElement {
    const { t } = useTranslation();
    const [meals, setMeals] = useState<TodayMeal[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [expandedMeals, setExpandedMeals] = useState<Record<number, boolean>>({});
    const { token } = useAuth();

    // useEffect(() => {
    //     setTimeout(() => {
    //         setMeals([
    //             {
    //                 id: 1,
    //                 name: "咖哩飯",
    //                 price: 120,
    //                 image: "https://th.bing.com/th/id/OIP.vI5uFSdV9ZVyKuRVwWwEcgHaD4?w=294&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
    //                 todayMeal: true,
    //                 comments: [
    //                     { recommended: true, text: "很好吃！" },
    //                     { recommended: false, text: "" },
    //                     { recommended: true, text: "很好吃！" },
    //                     { recommended: true, text: "很好吃！" },
    //                     { recommended: true, text: "很好吃！" },
    //                     { recommended: true, text: "很好吃！" },
    //                     { recommended: true, text: "很好吃！" },
    //                 ],
    //             },
    //             {
    //                 id: 2,
    //                 name: "炒麵",
    //                 price: 100,
    //                 image: "https://th.bing.com/th/id/OIP.hlmjCiCqOGAmzUDobwU5YAHaFj?w=227&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
    //                 todayMeal: false,
    //                 comments: [
    //                     { recommended: true, text: "份量剛好" },
    //                     { recommended: true, text: "" },
    //                     { recommended: false, text: "太鹹了" },
    //                 ],
    //             },
    //             {
    //                 id: 3,
    //                 name: "燒肉丼",
    //                 price: 150,
    //                 image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180&c=7&r=0&o=7&cb=iwp2&pid=1.7&rm=3",
    //                 todayMeal: true,
    //                 comments: [
    //                     { recommended: true, text: "份量超多" },
    //                     { recommended: false, text: "份量太多" },
    //                 ],
    //             },
    //         ]);
    //         setLoading(false);
    //     }, 1000);
    // }, []);
    useEffect(() => {
        const fetchMealsWithRatings = async () => {
            setLoading(true);
            
            try {
                const res = await fetch("http://localhost:8002/menu-items/", {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                if (!res.ok) throw new Error("無法取得餐點列表");

                const menuItems = await res.json();

                //const availableItems = menuItems.filter((item: any) => item.is_available || !item.is_available);

                // 並行取得每個餐點的評論資料
                const mealsWithComments = await Promise.all(
                    menuItems.map(async (item: any) => {
                        let comments: Comment[] = [];
                        
                        try {
                            const commentRes = await fetch(`http://localhost:8000/reviews/${item.id}`, {
                                method: "GET",
                                headers: {
                                    Authorization: `Bearer ${token}`,
                                },
                            });

                            if (commentRes.ok) {
                                const commentData = await commentRes.json();
                                console.log(`取得 ${item.id} 的評論成功: `, commentData);
                                comments = commentData.map((c: any) => ({
                                    recommended: c.rating,
                                    text: c.comment,
                                }));
                            } else {
                                //console.warn(`無法取得 ${item.id} 的評論`);
                            }
                        } catch (err) {
                            console.warn(`取得 ${item.id} 的評論時發生錯誤`, err);
                        }

                        return {
                            id: item.id,
                            name: item.zh_name,
                            englishName: item.en_name,
                            price: item.price,
                            image: item.url,
                            todayMeal: item.is_available, // 或根據別的 API 判斷
                            comments,
                        } as TodayMeal;
                    })
                );

                setMeals(mealsWithComments);
            } catch (err) {
                console.error(err);
                alert(t("載入餐點失敗"));
            } finally {
                setLoading(false);
            }
        };

        fetchMealsWithRatings();
    }, []);

    const calculateRecommendationRate = (comments: Comment[]): string => {
        if (comments.length === 0) return "None";
        const recommendedCount = comments.filter((c) => c.recommended == "good").length;
        const percentage = Math.round((recommendedCount / comments.length) * 100);
        return `${percentage}%`;
    };

    const toggleComments = (id: number) => {
        setExpandedMeals((prev) => ({
            ...prev,
            [id]: !prev[id],
        }));
    };

    if (loading) return <p className="loading">{t("載入中...")}</p>;

    return (
        <div>
            <Navbar />
            <div className="page-content">
                <h2 className="page-title">{t("今日餐點")}</h2>
                <div className="meal-list">
                    {meals
                        .filter((meal) => meal.todayMeal)
                        .map((meal) => (
                            <div key={meal.id} className="today-meal-card">
                                <img
                                    src={meal.image}
                                    alt={meal.name}
                                    className="meal-image"
                                />
                                <div className="meal-info">
                                    <h3>
                                        {meal.name}{" "}
                                        <span className="meal-price">
                                            {meal.price} {t("元")}
                                        </span>
                                    </h3>
                                    <p>{t("推薦比例")}：{calculateRecommendationRate(meal.comments)}</p>

                                    {expandedMeals[meal.id] && (
                                        <div className="comment-list-wrapper">
                                            <ul className="comment-list">
                                                {meal.comments
                                                    .filter((comment) => comment.text.trim() !== "")
                                                    .map((comment, index) => (
                                                        <li
                                                            key={index}
                                                            className={
                                                                comment.recommended == "good"
                                                                    ? "recommended"
                                                                    : "not-recommended"
                                                            }
                                                        >
                                                            {comment.recommended == "good" ? t("👍 推薦") : t("👎 不推薦")}
                                                            {`：${comment.text}`}
                                                        </li>
                                                    ))}
                                            </ul>
                                        </div>
                                    )}
                                    <button
                                        className="toggle-comments-btn"
                                        onClick={() =>
                                            setExpandedMeals((prev) => ({
                                                ...prev,
                                                [meal.id]: !prev[meal.id],
                                            }))
                                        }
                                    >
                                        {expandedMeals[meal.id] ? t("收合評論") : t("查看評論")}
                                    </button>
                                </div>

                            </div>
                        ))}
                </div>
            </div>
        </div>
    );
}

export default TodayMealsPage;
