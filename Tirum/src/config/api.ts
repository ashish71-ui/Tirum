// API Configuration for Django Backend
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  TIMEOUT: 10000, // 10 seconds
  ENDPOINTS: {
    AUTH: {
      LOGIN: '/login/',
      LOGOUT: '/logout/',
      USER: '/user/',
      REGISTER: '/register/',
    },
    // Your Django backend endpoints
    EXPENSES: {
      CATEGORIES: '/expense-categories/',
      TRANSACTIONS: '/transactions/',
      SPLIT_DETAILS: '/split-details/',
    },
    KHATA: {
      ENTRIES: '/khata-entries/',
    },
    NOTIFICATIONS: {
      LIST: '/notifications/',
      BILL_REMINDERS: '/bill-reminders/',
    },
    WALLETS: {
      LIST: '/wallets/',
    },
    USER_SUMMARY: '/user-summary/summary/',
  },
} as const;

// Environment check
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD; 