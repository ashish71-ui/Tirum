'use client';

import useDarkMode from '../hooks/userDarkMode';

export default function HomePage() {
  const { isDark, toggleDarkMode, isLoaded } = useDarkMode();

  // Render nothing until dark mode state is loaded to avoid hydration mismatch
  if (!isLoaded) return null;

  return (
    <div className={`min-h-screen ${isDark ? 'bg-gray-900 text-gray-200' : 'bg-gray-50 text-gray-900'} transition-colors duration-300`}>
      {/* Your page content */}

      <button
        onClick={toggleDarkMode}
        className="fixed top-4 right-4 p-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-200 shadow"
      >
        {isDark ? 'Light Mode' : 'Dark Mode'}
      </button>

      <h1 className="text-3xl font-bold p-8">Hello, Next.js with Dark Mode!</h1>

      {/* Rest of your page */}
    </div>
  );
}
