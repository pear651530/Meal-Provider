import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import i18n from '../../i18n'

// 儲存原始語言設定
const originalLanguage = i18n.language

describe('i18n 國際化功能', () => {
  beforeEach(() => {
    localStorage.clear()
    // 重置為中文
    i18n.changeLanguage('zh')
  })

  afterEach(() => {
    // 測試完畢後恢復原始設定
    i18n.changeLanguage(originalLanguage)
  })

  it('應該預設使用中文', () => {
    expect(i18n.language).toBe('zh')
  })

  it('應該能夠切換語言', () => {
    i18n.changeLanguage('en')
    expect(i18n.language).toBe('en')
  })

  it('切換語言應該更新 localStorage', () => {
    i18n.changeLanguage('en')
    expect(localStorage.getItem('language')).toBe('en')
  })

  it('中文翻譯應該正確', () => {
    i18n.changeLanguage('zh')
    expect(i18n.t('登入')).toBe('登入')
    expect(i18n.t('忘記密碼')).toBe('忘記密碼')
    expect(i18n.t('今日餐點')).toBe('今日餐點')
    expect(i18n.t('用餐紀錄')).toBe('用餐紀錄')
  })

  it('英文翻譯應該正確', () => {
    i18n.changeLanguage('en')
    expect(i18n.t('登入')).toBe('Login')
    expect(i18n.t('忘記密碼')).toBe('Forgot Password')
    expect(i18n.t('今日餐點')).toBe('Today\'s Meals')
    expect(i18n.t('用餐紀錄')).toBe('Dining Records')
  })

  it('不存在的文字應該返回原始文字', () => {
    const nonExistentKey = 'ThisKeyDoesNotExist' + Date.now()
    expect(i18n.t(nonExistentKey)).toBe(nonExistentKey)
  })

  it('i18n 應該正確初始化', () => {
    expect(i18n).toBeDefined()
    expect(typeof i18n.t).toBe('function')
  })

  it('應該支援帶參數的翻譯', () => {
    i18n.changeLanguage('en')
    const email = 'test@example.com'
    expect(i18n.t('重設密碼連結已發送至: {{email}}', { email }))
      .toBe(`Password reset link sent to: ${email}`)
    
    i18n.changeLanguage('zh')
    expect(i18n.t('重設密碼連結已發送至: {{email}}', { email }))
      .toBe(`重設密碼連結已發送至: ${email}`)
  })
})
