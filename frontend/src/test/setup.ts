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

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})
