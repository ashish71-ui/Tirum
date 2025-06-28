# Authentication System

This directory contains the authentication components and logic for the Tirum application.

## File Structure

```
src/
├── components/
│   └── auth/
│       ├── LoginForm.tsx      # Login form component with UI
│       ├── ProtectedRoute.tsx # Route protection component
│       └── README.md         # This file
├── pages/
│   ├── LoginPage.tsx         # Login page container
│   └── DashboardPage.tsx     # Dashboard page after login
├── stores/
│   └── authStore.ts          # Zustand store for auth state
└── types/
    └── auth.ts               # TypeScript types for auth
```

## Components

### LoginForm
A reusable login form component with:
- Email and password inputs
- Show/hide password toggle
- Loading states
- Error handling
- Remember me checkbox
- Forgot password link
- Sign up link

### ProtectedRoute
A wrapper component that:
- Checks authentication status
- Redirects unauthenticated users to login
- Preserves the intended destination URL

## Pages

### LoginPage
Container page that:
- Integrates LoginForm with auth store
- Handles navigation after successful login
- Clears errors on mount

### DashboardPage
Simple dashboard that:
- Displays user information
- Provides logout functionality
- Shows authentication success

## State Management

### AuthStore (Zustand)
Manages authentication state including:
- User data
- Authentication status
- Loading states
- Error messages
- Login/logout actions

## Types

### Auth Types
- `LoginFormData`: Form data structure
- `User`: User information
- `AuthState`: Store state structure
- `LoginResponse`: API response structure
- `AuthError`: Error handling

## Usage

### Testing the Login
Use these credentials to test the login functionality:
- Email: `test@example.com`
- Password: `password`

### Integration with Backend
Replace the `mockLoginAPI` function in `authStore.ts` with actual API calls to your Django backend.

## Features

- ✅ Modern, responsive UI with Tailwind CSS
- ✅ TypeScript support
- ✅ Form validation
- ✅ Loading states
- ✅ Error handling
- ✅ Route protection
- ✅ Persistent authentication
- ✅ Mock API for testing 