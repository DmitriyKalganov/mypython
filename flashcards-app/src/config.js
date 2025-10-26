// API Configuration
// Для локальной разработки используйте http://localhost:5000
// Для продакшена укажите URL вашего деплоя backend
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  generate: `${API_BASE_URL}/api/generate`,
  translate: `${API_BASE_URL}/api/translate`,
  health: `${API_BASE_URL}/health`
};
