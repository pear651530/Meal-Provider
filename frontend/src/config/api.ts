/// <reference types="vite/client" />

// export const API_CONFIG = {
//     USER_SERVICE: import.meta.env.VITE_USER_SERVICE_URL || 'http://localhost:8000',
//     ORDER_SERVICE: import.meta.env.VITE_ORDER_SERVICE_URL || 'http://localhost:8001',
//     ADMIN_SERVICE: import.meta.env.VITE_ADMIN_SERVICE_URL || 'http://localhost:8002',
//   };

  export const API_CONFIG = {
    USER_SERVICE: 'http://localhost:8000',
    ORDER_SERVICE: 'http://localhost:8001',
    ADMIN_SERVICE: 'http://localhost:8002',
  };
  
  export const getApiUrl = (service: keyof typeof API_CONFIG, path: string) => {
    return `${API_CONFIG[service]}${path}`;
  };