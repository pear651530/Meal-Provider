import { useEffect, useState } from "react";
import Navbar from "./NavBar";
import "./NavBar.css";
import "./StaffOrderPage.css";

interface TodayMeal {
  id: number;
  name: string;
  price: number;
  image: string;
}

interface SelectedMeal {
  meal: TodayMeal;
  payment: "cash" | "debt";
}

function StaffOrderPage(): JSX.Element {
  const [employeeId, setEmployeeId] = useState("");
  const [meals, setMeals] = useState<TodayMeal[]>([]);
  const [selectedMeal, setSelectedMeal] = useState<SelectedMeal | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setMeals([
        {
          id: 1,
          name: "咖哩飯",
          price: 120,
          image: "https://th.bing.com/th/id/OIP.vI5uFSdV9ZVyKuRVwWwEcgHaD4?w=294&h=180",
        },
        {
          id: 2,
          name: "炒麵",
          price: 100,
          image: "https://th.bing.com/th/id/OIP.hlmjCiCqOGAmzUDobwU5YAHaFj?w=227&h=180",
        },
        {
          id: 3,
          name: "燒肉丼",
          price: 150,
          image: "https://th.bing.com/th/id/OIP.-MXZNrzYO4WCU3nIYWGYmQHaFa?w=245&h=180",
        },
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const handleSelectMeal = (meal: TodayMeal) => {
    if (selectedMeal?.meal.id === meal.id) {
      setSelectedMeal(null);
    } else {
      setSelectedMeal({ meal, payment: "cash" });
    }
  };

  const handlePaymentChange = (payment: "cash" | "debt") => {
    if (selectedMeal) {
      setSelectedMeal({ ...selectedMeal, payment });
    }
  };

  const handleSubmit = () => {
    if (!employeeId || !selectedMeal) {
      alert("請輸入員工 ID 並選擇一項餐點");
      return;
    }

    const orderSummary = {
      employeeId,
      meals: [
        {
          id: selectedMeal.meal.id,
          name: selectedMeal.meal.name,
          payment: selectedMeal.payment,
        },
      ],
    };

    console.log("送出訂單：", orderSummary);
    alert("訂單已送出！");
    setSelectedMeal(null);
    setEmployeeId("");
  };

  if (loading) return <p className="loading">載入中...</p>;

  return (
    <div>
      <Navbar/>
      <div className="page-content">
        <h2 className="page-title">🧾 店員點餐</h2>

        <div className="input-container">
          <label className="input-id">
            員工 ID：
            <input
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              placeholder="請輸入員工 ID"
              className="input-id-borad"
            />
          </label>
        </div>

        <div className="meal-list">
          {meals.map((meal) => {
            const selected = selectedMeal?.meal.id === meal.id;
            return (
              <div key={meal.id} className="meal-card">
                <img src={meal.image} alt={meal.name} className="meal-image"/>
                <div className="meal-info">
                  <h3>{meal.name} <span className="meal-price">{meal.price} 元</span></h3>
                  <button onClick={() => handleSelectMeal(meal)}>
                    {selected ? "取消選擇" : "選擇"}
                  </button>
                {selected && (
                  <div style={{ marginTop: "10px" }}>
                    <div className="form-check">
                      <input
                        type="radio"
                        id="paymentCash"
                        className="form-check-input"
                        checked={selectedMeal?.payment === "cash"}
                        onChange={() => handlePaymentChange("cash")}
                      />
                      <label className="form-check-label" htmlFor="paymentCash">
                        現場支付
                      </label>
                    </div>

                    <div className="form-check">
                      <input
                        type="radio"
                        id="paymentDebt"
                        className="form-check-input"
                        checked={selectedMeal?.payment === "debt"}
                        onChange={() => handlePaymentChange("debt")}
                      />
                      <label className="form-check-label" htmlFor="paymentDebt">
                        賒帳
                      </label>
                    </div>
                  </div>
                )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="buttom-container">
          <button onClick={handleSubmit} className="buttom-submit">
            ✅ 送出訂單
          </button>
        </div>
      </div>
    </div>
  );
}

export default StaffOrderPage;
