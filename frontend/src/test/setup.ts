// src/test/setup.ts
import '@testing-library/jest-dom'
import { vi } from 'vitest'

// 模擬 twemoji
vi.mock('twemoji', () => ({
  default: {
    parse: vi.fn()
  }
}))

// 模擬 localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

if (typeof window === "undefined") {
  // @ts-ignore
  global.window = global;
}

if (typeof window.localStorage === "undefined") {
  // @ts-ignore
  window.localStorage = localStorageMock;
}

// beforeEach: 強制設置 i18n 語言與 localStorage 狀態
import i18n from '../i18n';
import { beforeEach } from 'vitest';
beforeEach(() => {
  localStorageMock.clear();
  localStorageMock.setItem('language', 'zh'); // 預設語言
  localStorageMock.setItem('i18nextLng', 'zh'); // 預設語言
  if (i18n.isInitialized) {
    i18n.changeLanguage('zh');
  }
});
