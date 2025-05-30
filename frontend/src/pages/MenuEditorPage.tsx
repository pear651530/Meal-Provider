import { useEffect, useState, useRef } from "react";
import Navbar from "../components/NavBar";
import "./MenuEditorPage.css";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
//import { console } from "inspector";

interface Comment {
    recommended: boolean;
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

interface AddMeal {
    zh_name: string;
    en_name?: string;
    price: number;
    url: string;
    is_available: boolean;
}

function MenuEditorPage() {
    const { t } = useTranslation();
    const [meals, setMeals] = useState<TodayMeal[]>([]);
    const [draggingMealId, setDraggingMealId] = useState<number | null>(null);
    const [showAddForm, setShowAddForm] = useState<boolean>(false);
    const [newMeal, setNewMeal] = useState({
        name: "",
        englishName: "",
        price: "",
        image: "",
    });
    const [editMeal, setEditMeal] = useState<TodayMeal | null>(null);
    const addFormRef = useRef<HTMLDivElement | null>(null);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    // useEffect(() => {
    //     const fetchMealsWithRatings = async () => {
    //         setLoading(true);
    //         try {
    //             const res = await fetch("http://localhost:8000/menu-items/", {
    //                 headers: {
    //                     Authorization: `Bearer ${token}`,
    //                 },
    //             });

    //             if (!res.ok) throw new Error("無法取得餐點列表");

    //             const menuItems = await res.json();

    //             // 只取 is_available === true 的餐點
    //             const availableItems = menuItems.filter((item: any) => item.is_available);

    //             // 並行取得每個餐點的評論資料
    //             const mealsWithComments = await Promise.all(
    //                 availableItems.map(async (item: any) => {
    //                     const ratingRes = await fetch(
    //                         `http://localhost:8000/ratings/${item.id}`,
    //                         {
    //                             headers: {
    //                                 Authorization: `Bearer ${token}`,
    //                             },
    //                         }
    //                     );

    //                     if (!ratingRes.ok) throw new Error(`取得 ${item.id} 評價失敗`);

    //                     const rating = await ratingRes.json();

    //                     // 模擬原始格式的 comments：good_reviews 為 true，其餘為 false
    //                     const comments: Comment[] = [];

    //                     for (let i = 0; i < rating.total_reviews; i++) {
    //                         comments.push({
    //                             recommended: i < rating.good_reviews,
    //                         });
    //                     }

    //                     return {
    //                         id: item.id,
    //                         name: item.zh_name,
    //                         englishName: item.en_name,
    //                         price: item.price,
    //                         image: item.url,
    //                         todayMeal: false, // 或根據別的 API 判斷
    //                         comments,
    //                     } as TodayMeal;
    //                 })
    //             );

    //             setMeals(mealsWithComments);
    //         } catch (err) {
    //             console.error(err);
    //             alert(t("載入餐點失敗"));
    //         } finally {
    //             setLoading(false);
    //         }
    //     };

    //     fetchMealsWithRatings();
    // }, []);


    useEffect(() => {
        setTimeout(() => {
            setMeals([
                {
                    id: 1,
                    name: "咖哩飯",
                    englishName: "Curry",
                    price: 120,
                    image: "https://th.bing.com/th/id/OIP.vI5uFSdV9ZVyKuRVwWwEcgHaD4?w=294&h=180",
                    todayMeal: true,
                    comments: [
                        { recommended: true },
                        { recommended: false },
                    ],
                },
                {
                    id: 2,
                    name: "炒麵",
                    englishName: "Fried noodle",
                    price: 100,
                    image: "https://th.bing.com/th/id/OIP.hlmjCiCqOGAmzUDobwU5YAHaFj?w=227&h=180",
                    todayMeal: false,
                    comments: [
                        { recommended: true },
                        { recommended: true },
                        { recommended: false },
                    ],
                },
                {
                    id: 3,
                    name: "燒肉丼",
                    englishName: "Yakiniku",
                    price: 150,
                    image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180",
                    todayMeal: true,
                    comments: [
                        { recommended: true },
                        { recommended: false },
                    ],
                },
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const handleDragStart = (id: number) => setDraggingMealId(id);

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
        return count === 0 ? "0%" : `${Math.round((recommended / count) * 100)}%`;
    };

    const renderMealCard = (meal: TodayMeal) => (
        <div
            key={meal.id}
            draggable
            onDragStart={() => handleDragStart(meal.id)}
            className="MenuEditor-card"
        >
            <img src={meal.image} alt={meal.name} className="MenuEditor-card-image" />
            <h3 className="MenuEditor-card-h3">{meal.name}</h3>
            <p>{t("價格")}：{meal.price} {t("元")}</p>
            <p>{t("推薦比例")}：{calculateRecommendationRate(meal.comments)}</p>
            <button
                className="MenuEditor-card-button"
                onClick={() => setEditMeal(meal)}
            >
                ✏️
            </button>
        </div>
    );

    const handleConfirm = () => {
        console.log(t("更新後餐點資料"), meals);
        alert(t("餐點已更新！"));
    };

    const handleDownloadReport = () => {
        alert(t("已下載！"));
    };

    // const handleAddMeal = () => {
    //     const nextId = meals.length === 0 ? 1 : Math.max(...meals.map((m) => m.id)) + 1;
    //     const { name, englishName, price, image } = newMeal;

    //     if (!name || !price || !image) {// || !englishName
    //         alert(t("請填寫完整資訊"));
    //         return;
    //     }

    //     const newItem: TodayMeal = {
    //         id: nextId,
    //         name,
    //         englishName,
    //         price: parseInt(price),
    //         image,
    //         todayMeal: false,
    //         comments: [],
    //     };

    //     setMeals((prev) => [...prev, newItem]);
    //     setNewMeal({ name: "", englishName: "", price: "", image: "" });
    //     setShowAddForm(false);
    //     console.log(t("新增餐點資料"), newItem);
    //     alert(t("餐點已新增！"));
    // };
    const handleAddMeal = async () => {
        const { name, englishName, price, image } = newMeal;

        if (!name || !price || !image) {
            alert(t("請填寫完整資訊"));
            return;
        }

        try {
            const res = await fetch("http://localhost:8002/menu-items/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    zh_name: name,
                    en_name: englishName || "",
                    price: parseInt(price),
                    url: image,
                    is_available: false,
                }),
            });

            if (!res.ok) {
                const errorText = await res.text();
                console.error("後端錯誤訊息:", errorText);
                console.log("token: ", token);
                throw new Error("無法新增餐點");
            }

            const data = await res.json();

            const newItem: AddMeal = {
                zh_name: data.zh_name,
                en_name: data.en_name,
                price: data.price,
                url: data.url,
                is_available: data.is_available,
            };

            //setMeals((prev) => [...prev, newItem]);
            setNewMeal({ name: "", englishName: "", price: "", image: "" });
            setShowAddForm(false);

            console.log(t("新增餐點資料"), newItem);
            alert(t("餐點已新增！"));
        } catch (error) {
            console.error(error);
            alert(t("新增餐點失敗"));
        }
    };

    const handleSaveEdit = () => {
        if (editMeal) {
            setMeals((prev) =>
                prev.map((m) => (m.id === editMeal.id ? editMeal : m))
            );
            setEditMeal(null);
            alert(t("餐點已更新！"));
        }
    };

    const handleDeleteMeal = () => {
        if (editMeal) {
            const confirmDelete = window.confirm(t("確定要刪除這個餐點嗎？"));
            if (confirmDelete) {
                setMeals((prev) => prev.filter((m) => m.id !== editMeal.id));
                setEditMeal(null);
                alert(t("餐點已刪除！"));
            }
        }
    };

    if (loading) return <p className="MenuEditor-loading">{t("載入中...")}</p>;

    const todayMeals = meals.filter((m) => m.todayMeal);
    const notTodayMeals = meals.filter((m) => !m.todayMeal);

    return (
        <div>
            <Navbar />
            <div className="MenuEditor-page-content">
                <h2 className="MenuEditor-page-title">{t("菜單調整頁面")}</h2>

                <div onDragOver={(e) => e.preventDefault()} onDrop={() => handleDrop(true)} className="MenuEditor-dropzone today">
                    <h3 className="MenuEditor-page-title">{t("今日餐點")}</h3>
                    <div className="MenuEditor-cards">{todayMeals.map(renderMealCard)}</div>
                </div>

                <div onDragOver={(e) => e.preventDefault()} onDrop={() => handleDrop(false)} className="MenuEditor-dropzone not-today">
                    <h3 className="MenuEditor-page-title">{t("非今日餐點")}</h3>
                    <div className="MenuEditor-cards">{notTodayMeals.map(renderMealCard)}</div>
                </div>

                <div className="MenuEditor-buttons">
                    <button onClick={handleConfirm} className="MenuEditor-button confirm">
                        {t("確認修改")}
                    </button>
                    <button
                        onClick={() => {
                            setShowAddForm((prev) => {
                                const next = !prev;
                                if (!next) return next;
                                setTimeout(() => {
                                    addFormRef.current?.scrollIntoView({ behavior: "smooth" });
                                }, 100);
                                return next;
                            });
                        }}
                        className="MenuEditor-button add"
                    >
                        {t("新增餐點")}
                    </button>
                    <button onClick={handleDownloadReport} className="MenuEditor-button download">
                        {t("下載報表")}
                    </button>
                </div>

                {showAddForm && (
                    <div ref={addFormRef} className="MenuEditor-add-form">
                        <h4>{t("新增餐點資訊")}</h4>
                        <input
                            type="text"
                            placeholder={t("餐點名稱 (必填)")}
                            value={newMeal.name}
                            onChange={(e) => setNewMeal({ ...newMeal, name: e.target.value })}
                        />
                        <input
                            type="text"
                            placeholder={t("餐點英文名稱 (非必填)")}
                            value={newMeal.englishName}
                            onChange={(e) => setNewMeal({ ...newMeal, englishName: e.target.value })}
                        />
                        <input
                            type="number"
                            placeholder={t("價格 (必填)")}
                            value={newMeal.price}
                            onChange={(e) => setNewMeal({ ...newMeal, price: e.target.value })}
                        />
                        <input
                            type="text"
                            placeholder={t("圖片連結 (必填)")}
                            value={newMeal.image}
                            onChange={(e) => setNewMeal({ ...newMeal, image: e.target.value })}
                        />
                        <button onClick={handleAddMeal}>{t("送出新增")}</button>
                    </div>
                )}

                {editMeal && (
                    <div className="MenuEditor-overlay">
                        <div className="MenuEditor-edit-modal">
                            <h4>{t("編輯餐點資訊")}</h4>
                            <input
                                type="text"
                                value={editMeal.name}
                                onChange={(e) =>
                                    setEditMeal({ ...editMeal, name: e.target.value })
                                }
                            />
                            <input
                                type="text"
                                value={editMeal.englishName}
                                onChange={(e) =>
                                    setEditMeal({ ...editMeal, englishName: e.target.value })
                                }
                            />
                            <input
                                type="number"
                                value={editMeal.price}
                                onChange={(e) =>
                                    setEditMeal({ ...editMeal, price: parseInt(e.target.value) })
                                }
                            />
                            <input
                                type="text"
                                value={editMeal.image}
                                onChange={(e) =>
                                    setEditMeal({ ...editMeal, image: e.target.value })
                                }
                            />
                            <div className="MenuEditor-edit-modal-buttons">
                                <button onClick={handleSaveEdit}>{t("儲存")}</button>
                                <button onClick={() => setEditMeal(null)}>{t("取消")}</button>
                                <button onClick={handleDeleteMeal} className="MenuEditor-delete-button">
                                    {t("刪除")}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default MenuEditorPage;
