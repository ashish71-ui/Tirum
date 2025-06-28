import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { userSummaryService } from '../services/userSummaryService';
import type { UserSummary } from '../types/userSummary';
import SummaryCard from '../components/ui/SummaryCard';
import TransactionList from '../components/dashboard/TransactionList';
import KhataSummary from '../components/dashboard/KhataSummary';

const UserSummaryDashboard: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const [userSummary, setUserSummary] = useState<UserSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Only fetch data if user is authenticated
    if (isAuthenticated) {
      fetchUserSummary();
    } else {
      setLoading(false);
      setError('User not authenticated');
    }
  }, [isAuthenticated]);

  const fetchUserSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await userSummaryService.getUserSummary();
      setUserSummary(data);
    } catch (err) {
      console.error('Error fetching user summary:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch user summary');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const data = await userSummaryService.refreshUserSummary();
      setUserSummary(data);
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  // Show loading state while checking authentication or loading data
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your financial summary...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchUserSummary}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Show no data state
  if (!userSummary) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 text-4xl mb-4">📊</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Data Available</h2>
          <p className="text-gray-600">Start adding transactions to see your summary</p>
        </div>
      </div>
    );
  }

  const { total_to_take, total_to_return, transactions } = userSummary;
  const netBalance = total_to_take - total_to_return;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Financial Dashboard</h1>
              <span className="text-sm text-gray-500">
                Welcome back, {user?.name || 'User'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <SummaryCard
              title="Money to Take"
              value={total_to_take}
              icon="💰"
              color="bg-green-500"
              change="From others"
            />
            <SummaryCard
              title="Money to Return"
              value={total_to_return}
              icon="💸"
              color="bg-red-500"
              change="To others"
            />
            <SummaryCard
              title="Net Balance"
              value={netBalance}
              icon={netBalance >= 0 ? "📈" : "📉"}
              color={netBalance >= 0 ? "bg-green-500" : "bg-red-500"}
              change={netBalance >= 0 ? "You're ahead" : "You owe money"}
            />
            <SummaryCard
              title="Total Transactions"
              value={transactions.length}
              icon="📊"
              color="bg-blue-500"
              change="This month"
            />
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Khata Summary */}
            <div>
              <KhataSummary userSummary={userSummary} />
            </div>

            {/* Recent Transactions */}
            <div>
              <TransactionList 
                transactions={transactions} 
                loading={false} 
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-8 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                <div className="text-2xl mb-2">➕</div>
                <div className="text-sm font-medium text-gray-900">Add Expense</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                <div className="text-2xl mb-2">👥</div>
                <div className="text-sm font-medium text-gray-900">Split Bill</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                <div className="text-2xl mb-2">📝</div>
                <div className="text-sm font-medium text-gray-900">Add Khata</div>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                <div className="text-2xl mb-2">📊</div>
                <div className="text-sm font-medium text-gray-900">View Reports</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSummaryDashboard; 