import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  const navigate = useNavigate();

  const handleLogin = () => {
    if (username === 'admin' && password === '1234') {
      setMessage('✅ 登入成功！歡迎 admin');
      setTimeout(() => {
        navigate('/TodayMeals');  // 導向紀錄頁
      }, 1000);
    } else {
      setMessage('❌ 帳號或密碼錯誤');
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial", maxWidth: "300px", margin: "auto" }}>
      <h2>🔐 登入</h2>

      <input
        type="text"
        placeholder="帳號"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ display: 'block', marginBottom: '10px', width: '100%' }}
      />

      <input
        type="password"
        placeholder="密碼"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ display: 'block', marginBottom: '10px', width: '100%' }}
      />

      <button onClick={handleLogin} style={{ width: '100%' }}>
        登入
      </button>

      {message && <p style={{ marginTop: '15px' }}>{message}</p>}
    </div>
  );
}

export default LoginForm;