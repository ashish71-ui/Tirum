import { create } from 'zustand';

interface AuthState {
    token: string | null;
    setToken: (token: string | null) => void;
    logout: () => void;
    isLoggedIn: () => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    token: null,

    setToken: (token) => {
        set({ token });
        if (token) {
            localStorage.setItem('token', token);
        } else {
            localStorage.removeItem('token');
        }
    },

    logout: () => {
        set({ token: null });
        localStorage.removeItem('token');
    },

    isLoggedIn: () => !!get().token,
}));

// Helper to get token outside react components (for axios interceptor)
export function getToken() {
    // Try from localStorage (persist token)
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token');
    }
    return null;
}
