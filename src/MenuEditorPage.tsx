import { useEffect, useState, useRef} from "react";
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
  image: string;
  todayMeal: boolean;
  comments: Comment[];
}

function MenuEditorPage(): JSX.Element {
  const [meals, setMeals] = useState<TodayMeal[]>([]);
  const [draggingMealId, setDraggingMealId] = useState<number | null>(null);
  const [showAddForm, setShowAddForm] = useState<boolean>(false);
  const [newMeal, setNewMeal] = useState<{ name: string; price: string; image: string }>({
    name: "",
    price: "",
    image: "",
  });
  const addFormRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
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
    ]);
  }, []);

  const handleDragStart = (id: number) => {
    setDraggingMealId(id);
  };

  const handleDrop = (toTodayMeal: boolean) => {
    if (draggingMealId !== null) {
      setMeals((prev) =>
        prev.map((meal) =>
          meal.id === draggingMealId ? { ...meal, todayMeal: toTodayMeal } : meal
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
      style={{
        border: "1px solid #ccc",
        padding: "10px",
        margin: "10px",
        backgroundColor: "white",
        width: "200px",
      }}
    >
      <img src={meal.image} alt={meal.name} style={{ width: "100%" }} />
      <h4>{meal.name}</h4>
      <p>價格：{meal.price} 元</p>
      <p>推薦比例：{calculateRecommendationRate(meal.comments)}</p>
    </div>
  );

  const todayMeals = meals.filter((m) => m.todayMeal);
  const notTodayMeals = meals.filter((m) => !m.todayMeal);

  const handleConfirm = () => {
    console.log("更新後餐點資料：", meals);
    alert("餐點已更新！");
  };

  const handleAddMeal = () => {
    const nextId = meals.length === 0 ? 1 : Math.max(...meals.map((m) => m.id)) + 1;
    const { name, price, image } = newMeal;

    if (!name || !price || !image) {
      alert("請填寫完整資訊");
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

    console.log("新增的餐點資料：", newItem);
    alert("餐點已新增！");
  };

  return (
    <div>
      <Navbar debtAmount={0} />
      <div className="page-content">
        <h2>📋 菜單調整頁面</h2>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => handleDrop(true)}
          style={{
            minHeight: "200px",
            border: "2px dashed #90caf9",
            padding: "10px",
            marginBottom: "20px",
            backgroundColor: "#e3f2fd",
          }}
        >
          <h3>📌 今日餐點</h3>
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {todayMeals.map(renderMealCard)}
          </div>
        </div>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => handleDrop(false)}
          style={{
            minHeight: "200px",
            border: "2px dashed #eeeeee",
            padding: "10px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h3>📂 非今日餐點</h3>
          <div style={{ display: "flex", flexWrap: "wrap" }}>
            {notTodayMeals.map(renderMealCard)}
          </div>
        </div>

        <div style={{ marginTop: "20px", display: "flex", gap: "10px" }}>
          <button
            onClick={handleConfirm}
            style={{
              padding: "10px 20px",
              fontSize: "16px",
              fontWeight: "bold",
            }}
          >
            ✅ 確認修改
          </button>

          <button
            onClick={() => {
              setShowAddForm((prev) => {
                const next = !prev;
                if (!next) return next;
                setTimeout(() => {
                  addFormRef.current?.scrollIntoView({ behavior: "smooth" });
                }, 100); // 等待 UI 展開完再捲動
                return next;
              });
            }}
            style={{
              padding: "10px 20px",
              fontSize: "16px",
              fontWeight: "bold",
            }}
          >
            ➕ 新增餐點
          </button>
        </div>

        {showAddForm && (
          <div
            ref={addFormRef}
            style={{
              marginTop: "20px",
              padding: "15px",
              border: "1px solid #ccc",
              backgroundColor: "#f1f1f1",
              width: "300px",
            }}
          >
            <h4>新增餐點資訊</h4>
            <input
              type="text"
              placeholder="餐點名稱"
              value={newMeal.name}
              onChange={(e) => setNewMeal({ ...newMeal, name: e.target.value })}
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <input
              type="number"
              placeholder="價格"
              value={newMeal.price}
              onChange={(e) => setNewMeal({ ...newMeal, price: e.target.value })}
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <input
              type="text"
              placeholder="圖片連結"
              value={newMeal.image}
              onChange={(e) => setNewMeal({ ...newMeal, image: e.target.value })}
              style={{ width: "100%", marginBottom: "10px" }}
            />
            <button
              onClick={handleAddMeal}
              style={{
                padding: "6px 12px",
                fontWeight: "bold",
              }}
            >
              📤 送出新增
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default MenuEditorPage;
