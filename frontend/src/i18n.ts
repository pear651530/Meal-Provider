// 修復後的 i18n.ts 文件
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

// 從 localStorage 讀取語言設置，如果沒有則使用默認語言 'zh'
const savedLanguage = localStorage.getItem("language") || "zh";

// 定義通用翻譯
const commonTranslations = {
  en: {
    "載入中...": "Loading...",
    "元": "NT$",
    "註冊帳號": "Register",
    "密碼": "Password",
  },
  zh: {
    "載入中...": "載入中...",
    "元": "元",
    "註冊帳號": "註冊帳號",
    "密碼": "密碼",
  }
};

// 定義各頁面翻譯
const translations = {
  en: {
    // NavBar
    "今日餐點": "Today's Meals",
    "用餐紀錄": "Dining Records",
    "店員點餐": "Staff Orders",
    "員工賒帳紀錄": "Staff Debt Records",
    "菜單調整": "Menu Editor",
    "登出": "Logout",

    // ForgotPassword
    "請輸入電子郵件地址": "Please enter your email address",
    "重設密碼的連結已發送至 {{email}}": "Password reset link has been sent to {{email}}",
    "重設密碼連結已發送至: {{email}}": "Password reset link sent to: {{email}}",
    "返回登入頁": "Back to Login",
    "找回密碼": "Forgot Password",
    "請輸入您的電子郵件地址，我們將發送一封包含重設密碼連結的郵件給您。": "Please enter your email address. We will send you an email with a link to reset your password.",
    "電子郵件": "Email",
    "發送重設密碼連結": "Send Reset Link",
    "已發送": "sent",

    // LoginForm
    "此處保留未來添加資訊": "Reserved for future information",
    "員工登入": "Staff Login",
    "帳號": "Username",
    "登入": "Login",
    "登入成功！": "Login successful!",
    "尚有餘款未繳清!": "You still have unpaid balance!",
    "帳號或密碼錯誤": "Incorrect username or password",
    "忘記密碼": "Forgot Password",
    "成功": "success",

    // Register
    "註冊帳號_頁面": "Register Account",
    "員工號": "Employee ID",
    "確認密碼": "Confirm Password",
    "驗證員工號": "Verify Employee ID",
    "註冊": "Register",
    "請輸入員工號": "Please enter employee ID",
    "員工號驗證成功！": "Employee ID verified successfully!",
    "無效的員工號，請確認後重試": "Invalid employee ID, please try again",
    "驗證員工號時出錯:": "Error verifying employee ID:",
    "驗證員工號時發生錯誤，請稍後再試": "Error verifying employee ID, please try again later",
    "請填寫所有欄位": "Please fill in all fields",
    "密碼與確認密碼不一致": "Password and confirmation do not match",
    "請先驗證員工號": "Please verify employee ID first",
    "註冊成功！即將跳轉至登入頁面": "Registration successful! Redirecting to login page",

    // MenuEditor
    "菜單調整頁面": "Menu Editor Page",
    "今日餐點_選項": "Today's Meals",
    "非今日餐點": "Not Today's Meals",
    "確認修改": "Confirm Changes",
    "新增餐點": "Add Meal",
    "刪除": "Delete",
    "確定要刪除這個餐點嗎？": "Are you sure you want to delete this meal?",
    "餐點已刪除！": "Meals have been deleted!",
    "新增餐點資訊": "Add Meal Info",
    "餐點名稱": "Meal Name",
    "圖片連結": "Image URL",
    "送出新增": "Submit",
    "請填寫完整資訊": "Please fill in all information",
    "餐點已新增！": "Meal added!",
    "更新後餐點資料": "Updated meal data",
    "餐點已更新！": "Meals updated!",
    "推薦比例": "Recommendation Rate",

    // TodayMeals
    "今日餐點_頁面": "Today's Meals",
    "👍 推薦": "👍 Recommended",
    "👎 不推薦": "👎 Not Recommended",

    // Records
    "歷史用餐紀錄": "Dining History",
    "點餐日期": "Order Date",
    "餐點": "Meal",
    "價格": "Price",
    "付款狀況": "Payment Status",
    "我的評價": "My Rating",
    "已付款": "Paid",
    "未付款": "Unpaid",
    "喜歡": "Like",
    "不喜歡": "Dislike",
    "填寫評論": "Write Comment",
    "取消": "Cancel",
    "儲存": "Save",
    "已填寫": "Submitted",
    "賒帳總額": "Total Debt",
    "下一次結帳期限": "Next Payment Due",
    "馬上結帳": "Pay Now",
    "馬上結帳功能尚未實作！": "Immediate payment feature not yet implemented!",

    // StaffDebt
    "員工賒帳狀況": "Staff Debt Status",
    "全選": "Select All",
    "員工ID": "Employee ID",
    "員工名稱": "Employee Name",
    "賒帳金額": "Debt Amount",
    "預警選取員工": "Warn Selected Staff",
    "選取的員工 ID: {{ids}}": "Selected employee IDs: {{ids}}",

    // StaffOrder
    "員工 ID：": "Employee ID:",
    "請輸入員工 ID": "Enter Employee ID",
    "取消選擇": "Deselect",
    "選擇": "Select",
    "現場支付": "Pay Now",
    "賒帳": "Credit",
    "送出訂單": "Submit Order",
    "請輸入員工 ID 並選擇一項餐點": "Please enter an employee ID and select a meal",
    "訂單已送出！": "Order submitted!",
    "送出訂單：": "Submitting order:",

    // LanguageSwitcher
    "切換語言": "Language",
    "中文": "中文",
    "英文": "English"
  },
  
  zh: {
    // NavBar
    "今日餐點": "今日餐點",
    "用餐紀錄": "用餐紀錄",
    "店員點餐": "店員點餐",
    "員工賒帳紀錄": "員工賒帳紀錄",
    "菜單調整": "菜單調整",
    "登出": "登出",

    // ForgotPassword
    "請輸入電子郵件地址": "請輸入電子郵件地址",
    "重設密碼的連結已發送至 {{email}}": "重設密碼的連結已發送至 {{email}}",
    "重設密碼連結已發送至: {{email}}": "重設密碼連結已發送至: {{email}}",
    "返回登入頁": "返回登入頁",
    "找回密碼": "找回密碼",
    "請輸入您的電子郵件地址，我們將發送一封包含重設密碼連結的郵件給您。": "請輸入您的電子郵件地址，我們將發送一封包含重設密碼連結的郵件給您。",
    "電子郵件": "電子郵件",
    "發送重設密碼連結": "發送重設密碼連結",
    "已發送": "已發送",

    // LoginForm
    "此處保留未來添加資訊": "此處保留未來添加資訊",
    "員工登入": "員工登入",
    "帳號": "帳號",
    "登入": "登入",
    "登入成功！": "登入成功！",
    "尚有餘款未繳清!": "尚有餘款未繳清!",
    "帳號或密碼錯誤": "帳號或密碼錯誤",
    "忘記密碼": "忘記密碼",
    "成功": "成功",

    // Register
    "註冊帳號_頁面": "註冊帳號",
    "員工號": "員工號",
    "確認密碼": "確認密碼",
    "驗證員工號": "驗證員工號",
    "註冊": "註冊",
    "請輸入員工號": "請輸入員工號",
    "員工號驗證成功！": "員工號驗證成功！",
    "無效的員工號，請確認後重試": "無效的員工號，請確認後重試",
    "驗證員工號時出錯:": "驗證員工號時出錯:",
    "驗證員工號時發生錯誤，請稍後再試": "驗證員工號時發生錯誤，請稍後再試",
    "請填寫所有欄位": "請填寫所有欄位",
    "密碼與確認密碼不一致": "密碼與確認密碼不一致",
    "請先驗證員工號": "請先驗證員工號",
    "註冊成功！即將跳轉至登入頁面": "註冊成功！即將跳轉至登入頁面",

    // MenuEditor
    "菜單調整頁面": "菜單調整頁面",
    "今日餐點_選項": "今日餐點",
    "非今日餐點": "非今日餐點",
    "確認修改": "確認修改",
    "新增餐點": "新增餐點",
    "刪除": "刪除",
    "確定要刪除這個餐點嗎？": "確定要刪除這個餐點嗎？",
    "餐點已刪除！": "餐點已刪除！",
    "新增餐點資訊": "新增餐點資訊",
    "餐點名稱": "餐點名稱",
    "圖片連結": "圖片連結",
    "送出新增": "送出新增",
    "請填寫完整資訊": "請填寫完整資訊",
    "餐點已新增！": "餐點已新增！",
    "更新後餐點資料": "更新後餐點資料",
    "餐點已更新！": "餐點已更新！",
    "推薦比例": "推薦比例",

    // TodayMeals
    "今日餐點_頁面": "今日餐點",
    "👍 推薦": "👍 推薦",
    "👎 不推薦": "👎 不推薦",

    // Records
    "歷史用餐紀錄": "歷史用餐紀錄",
    "點餐日期": "點餐日期",
    "餐點": "餐點",
    "價格": "價格",
    "付款狀況": "付款狀況",
    "我的評價": "我的評價",
    "已付款": "已付款",
    "未付款": "未付款",
    "喜歡": "喜歡",
    "不喜歡": "不喜歡",
    "填寫評論": "填寫評論",
    "取消": "取消",
    "儲存": "儲存",
    "已填寫": "已填寫",
    "賒帳總額": "賒帳總額",
    "下一次結帳期限": "下一次結帳期限",
    "馬上結帳": "馬上結帳",
    "馬上結帳功能尚未實作！": "馬上結帳功能尚未實作！",

    // StaffDebt
    "員工賒帳狀況": "員工賒帳狀況",
    "全選": "全選",
    "員工ID": "員工ID",
    "員工名稱": "員工名稱",
    "賒帳金額": "賒帳金額",
    "預警選取員工": "預警選取員工",
    "選取的員工 ID: {{ids}}": "選取的員工 ID: {{ids}}",

    // StaffOrder
    "員工 ID：": "員工 ID：",
    "請輸入員工 ID": "請輸入員工 ID",
    "取消選擇": "取消選擇",
    "選擇": "選擇",
    "現場支付": "現場支付",
    "賒帳": "賒帳",
    "送出訂單": "送出訂單",
    "請輸入員工 ID 並選擇一項餐點": "請輸入員工 ID 並選擇一項餐點",
    "訂單已送出！": "訂單已送出！",
    "送出訂單：": "送出訂單：",

    // LanguageSwitcher
    "切換語言": "切換語言",
    "中文": "中文",
    "英文": "英文"
  }
};

// 合併通用翻譯和頁面翻譯
const resources = {
  en: {
    translation: {...commonTranslations.en, ...translations.en}
  },
  zh: {
    translation: {...commonTranslations.zh, ...translations.zh}
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage, // 使用保存的語言
    fallbackLng: "en",
    interpolation: {
      escapeValue: false
    }
  });

// 當語言變更時，保存到 localStorage
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
});

export default i18n;
