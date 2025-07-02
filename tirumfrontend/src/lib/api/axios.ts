import axios from 'axios';
import { getToken } from '../authStore.'; // helper to get token from Zustand

const axiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to headers before request
axiosInstance.interceptors.request.use((config) => {
    const token = getToken();
    if (token && config.headers) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

export default axiosInstance;
