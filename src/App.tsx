const menuItems = [
  { name: "用餐紀錄", action: () => alert("用餐紀錄") },
  { name: "賒帳紀錄", action: () => alert("賒帳紀錄") },
  { name: "店員點餐", action: () => alert("店員點餐") },
  { name: "員工賒帳紀錄", action: () => alert("員工賒帳紀錄") },
  { name: "菜單調整", action: () => alert("菜單調整") },
];

function App() {
  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center bg-light">
      <div className="card shadow p-4" style={{ maxWidth: "400px", width: "100%" }}>
        <h1 className="text-center mb-4">Menu</h1>
        <div className="d-grid gap-3">
          {menuItems.map((item, index) => (
            <button
              key={index}
              onClick={item.action}
              className="btn btn-primary"
            >
              {item.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
