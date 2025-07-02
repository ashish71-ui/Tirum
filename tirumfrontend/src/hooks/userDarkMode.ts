import { useEffect, useState } from 'react';

export default function useDarkMode() {
    const [isDark, setIsDark] = useState(false);
    const [isLoaded, setIsLoaded] = useState(false); // To prevent hydration issues

    useEffect(() => {
        // Check saved preference
        const saved = localStorage.getItem('darkMode');
        if (saved === 'true') {
            setIsDark(true);
            document.documentElement.classList.add('dark');
        } else if (saved === 'false') {
            setIsDark(false);
            document.documentElement.classList.remove('dark');
        } else {
            // No saved preference, use OS
            const osPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            setIsDark(osPrefersDark);
            if (osPrefersDark) document.documentElement.classList.add('dark');
            else document.documentElement.classList.remove('dark');
        }
        setIsLoaded(true);
    }, []);

    const toggleDarkMode = () => {
        if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('darkMode', 'false');
            setIsDark(false);
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('darkMode', 'true');
            setIsDark(true);
        }
    };

    return { isDark, toggleDarkMode, isLoaded };
}
