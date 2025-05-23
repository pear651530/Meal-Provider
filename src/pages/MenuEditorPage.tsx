import { useEffect, useState, useRef } from "react";
import Navbar from "../components/NavBar";
import "./MenuEditorPage.css";
import { useTranslation } from "react-i18next";

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

function MenuEditorPage(): JSX.Element {
    const { t, i18n } = useTranslation();
    const [meals, setMeals] = useState<TodayMeal[]>([]);
    const [draggingMealId, setDraggingMealId] = useState<number | null>(null);
    const [showAddForm, setShowAddForm] = useState<boolean>(false);
    const [newMeal, setNewMeal] = useState<{
        name: string;
        price: string;
        image: string;
    }>({
        name: "",
        price: "",
        image: "",
    });
    const addFormRef = useRef<HTMLDivElement | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setTimeout(() => {
            setMeals([
                {
                    id: 1,
                    name: "咖哩飯",
                    price: 120,
                    image: "https://th.bing.com/th/id/OIP.vI5uFSdV9ZVyKuRVwWwEcgHaD4?w=294&h=180",
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
                    image: "https://th.bing.com/th/id/OIP.hlmjCiCqOGAmzUDobwU5YAHaFj?w=227&h=180",
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
                    image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180",
                    todayMeal: true,
                    comments: [
                        { recommended: true, text: "份量超多" },
                        { recommended: false, text: "份量太多" },
                    ],
                },
                // ... (other meals)
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const handleDragStart = (id: number) => {
        setDraggingMealId(id);
    };

    const handleDrop = (toTodayMeal: boolean) => {
        if (draggingMealId !== null) {
            setMeals((prev) =>
                prev.map((meal) =>
                    meal.id === draggingMealId
                        ? { ...meal, todayMeal: toTodayMeal }
                        : meal
                )
            );
            setDraggingMealId(null);
        }
    };

    const calculateRecommendationRate = (comments: Comment[]) => {
        const count = comments.length;
        const recommended = comments.filter((c) => c.recommended).length;
        return count === 0
            ? "0%"
            : `${Math.round((recommended / count) * 100)}%`;
    };

    const renderMealCard = (meal: TodayMeal) => (
        <div
            key={meal.id}
            draggable
            onDragStart={() => handleDragStart(meal.id)}
            className="MenuEditor-card"
        >
            <img
                src={meal.image}
                alt={meal.name}
                className="MenuEditor-card-image"
            />
            <h3 className="MenuEditor-card-h3">{meal.name} </h3>
            <p>
                {t("價格")}：{meal.price} {t("元")}
            </p>
            <p>
                {t("推薦比例")}：{calculateRecommendationRate(meal.comments)}
            </p>
        </div>
    );

    const todayMeals = meals.filter((m) => m.todayMeal);
    const notTodayMeals = meals.filter((m) => !m.todayMeal);

    const handleConfirm = () => {
        console.log(t("更新後餐點資料"), meals);
        alert(t("餐點已更新！"));
    };

    const handleAddMeal = () => {
        const nextId =
            meals.length === 0 ? 1 : Math.max(...meals.map((m) => m.id)) + 1;
        const { name, price, image } = newMeal;

        if (!name || !price || !image) {
            alert(t("請填寫完整資訊"));
            return;
        }

        const newItem: TodayMeal = {
            id: nextId,
            name,
            price: parseInt(price),
            image,
            todayMeal: false,
            comments: [],
        };

        setMeals((prev) => [...prev, newItem]);
        setNewMeal({ name: "", price: "", image: "" });
        setShowAddForm(false);

        console.log(t("新增的餐點資料"), newItem);
        alert(t("餐點已新增！"));
    };

    if (loading) return <p className="MenuEditor-loading">{t("載入中...")}</p>;

    return (
        <div>
            <Navbar />
            <div className="MenuEditor-page-content">
                <h2 className="MenuEditor-page-title">{t("菜單調整頁面")}</h2>

                <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => handleDrop(true)}
                    className="MenuEditor-dropzone today"
                >
                    <h3 className="MenuEditor-page-title">{t("今日餐點")}</h3>
                    <div className="MenuEditor-cards">
                        {todayMeals.map(renderMealCard)}
                    </div>
                </div>

                <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={() => handleDrop(false)}
                    className="MenuEditor-dropzone not-today"
                >
                    <h3 className="MenuEditor-page-title">{t("非今日餐點")}</h3>
                    <div className="MenuEditor-cards">
                        {notTodayMeals.map(renderMealCard)}
                    </div>
                </div>

                <div className="MenuEditor-buttons">
                    <button
                        onClick={handleConfirm}
                        className="MenuEditor-button confirm"
                    >
                        {t("確認修改")}
                    </button>

                    <button
                        onClick={() => {
                            setShowAddForm((prev) => {
                                const next = !prev;
                                if (!next) return next;
                                setTimeout(() => {
                                    addFormRef.current?.scrollIntoView({
                                        behavior: "smooth",
                                    });
                                }, 100);
                                return next;
                            });
                        }}
                        className="MenuEditor-button add"
                    >
                        {t("新增餐點")}
                    </button>
                </div>

                {showAddForm && (
                    <div ref={addFormRef} className="MenuEditor-add-form">
                        <h4>{t("新增餐點資訊")}</h4>
                        <input
                            type="text"
                            placeholder={t("餐點名稱")}
                            value={newMeal.name}
                            onChange={(e) =>
                                setNewMeal({ ...newMeal, name: e.target.value })
                            }
                        />
                        <input
                            type="number"
                            placeholder={t("價格")}
                            value={newMeal.price}
                            onChange={(e) =>
                                setNewMeal({
                                    ...newMeal,
                                    price: e.target.value,
                                })
                            }
                        />
                        <input
                            type="text"
                            placeholder={t("圖片連結")}
                            value={newMeal.image}
                            onChange={(e) =>
                                setNewMeal({
                                    ...newMeal,
                                    image: e.target.value,
                                })
                            }
                        />
                        <button onClick={handleAddMeal}>{t("送出新增")}</button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default MenuEditorPage;
