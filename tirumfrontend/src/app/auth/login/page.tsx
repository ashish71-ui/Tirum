'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { loginUser } from '@/lib/api/auth';
import { useAuthStore } from '../../../lib/authStore.';
import { Eye, EyeOff, User, Lock, AlertCircle } from 'lucide-react';

const ACCENT_GREEN = '#34d399'; // Tailwind emerald-400

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();
    const setToken = useAuthStore((state) => state.setToken);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const data = await loginUser(username, password);
            setToken(data.token);
            router.push('/');
        } catch (error: any) {
            setError(error.response?.data?.message || 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
            {/* Login Container */}
            <div className="bg-white rounded-3xl p-10 max-w-md w-full shadow-md">
                {/* Logo Section */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-green-200 rounded-2xl mb-6 shadow">
                        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                            <div className="w-6 h-6 bg-green-400 rounded-sm transform rotate-45"></div>
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        Welcome Back
                    </h1>
                    <p className="text-gray-600 text-lg">Sign in to continue your journey</p>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-600">
                        <AlertCircle size={20} stroke={ACCENT_GREEN} strokeWidth={2.2} />
                        <span className="text-sm font-medium">{error}</span>
                    </div>
                )}

                {/* Login Form */}
                <form onSubmit={handleLogin} className="space-y-6">
                    {/* Username */}
                    <div>
                        <label htmlFor="username" className="block text-sm font-semibold text-gray-700 mb-2">
                            Username
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <div className="w-8 h-8 flex items-center justify-center bg-green-100 border border-green-300 rounded-full text-green-500 shadow-sm">
                                    <User size={18} stroke={ACCENT_GREEN} strokeWidth={2.2} />
                                </div>
                            </div>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                disabled={isLoading}
                                placeholder="Enter your username"
                                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-300 text-gray-700 bg-white transition"
                            />
                        </div>
                    </div>

                    {/* Password */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                            Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <div className="w-8 h-8 flex items-center justify-center bg-green-100 border border-green-300 rounded-full text-green-500 shadow-sm">
                                    <Lock size={18} stroke={ACCENT_GREEN} strokeWidth={2.2} />
                                </div>
                            </div>
                            <input
                                id="password"
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                disabled={isLoading}
                                placeholder="Enter your password"
                                className="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-300 text-gray-700 bg-white transition"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-green-500 hover:text-green-600 transition"
                                disabled={isLoading}
                                aria-label={showPassword ? 'Hide password' : 'Show password'}
                            >
                                {showPassword ? (
                                    <EyeOff size={20} stroke={ACCENT_GREEN} strokeWidth={2.2} />
                                ) : (
                                    <Eye size={20} stroke={ACCENT_GREEN} strokeWidth={2.2} />
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-green-400 hover:bg-green-500 text-white py-3 rounded-lg font-semibold transition disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {isLoading ? 'Signing In...' : 'Sign In'}
                    </button>
                </form>

                {/* Extra Links */}
                <div className="mt-8 pt-6 border-t border-gray-200 text-center text-gray-600 text-sm">
                    <a href="#" className="text-green-500 hover:text-green-600 font-medium mr-4">
                        Forgot your password?
                    </a>
                    <a href="#" className="text-green-500 hover:text-green-600 font-semibold">
                        Create an account
                    </a>
                </div>
            </div>

            {/* Footer */}
            <footer className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-gray-400 text-sm">
                <p>&copy; 2024 Your Company Name. All rights reserved.</p>
            </footer>
        </div>
    );
}
