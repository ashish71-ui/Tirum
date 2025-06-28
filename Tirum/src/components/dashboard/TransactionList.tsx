import React from 'react';
import type { Transaction } from '../../types/userSummary';

interface TransactionListProps {
  transactions: Transaction[];
  loading: boolean;
}

const TransactionList: React.FC<TransactionListProps> = ({ transactions, loading }) => {
  const getCategoryColor = (category: string) => {
    const colors = {
      'food': 'bg-red-100 text-red-800',
      'transport': 'bg-blue-100 text-blue-800',
      'entertainment': 'bg-purple-100 text-purple-800',
      'shopping': 'bg-green-100 text-green-800',
      'bills': 'bg-yellow-100 text-yellow-800',
      'other': 'bg-gray-100 text-gray-800',
    };
    return colors[category.toLowerCase() as keyof typeof colors] || colors.other;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Recent Transactions
          </h3>
        </div>
        <div className="border-t border-gray-200">
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-2">Loading transactions...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Recent Transactions
        </h3>
        <span className="text-sm text-gray-500">
          {transactions.length} transactions
        </span>
      </div>
      <div className="border-t border-gray-200">
        {transactions.length > 0 ? (
          <ul className="divide-y divide-gray-200">
            {transactions.slice(0, 10).map((transaction) => (
              <li key={transaction.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                        <span className="text-indigo-600 font-medium">
                          {transaction.category.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">
                        {transaction.description}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(transaction.category)}`}>
                          {transaction.category}
                        </span>
                        <span className="text-sm text-gray-500">
                          {formatDate(transaction.date)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      ${transaction.amount.toFixed(2)}
                    </div>
                    {transaction.split_details && transaction.split_details.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Split with {transaction.split_details.length} people
                      </div>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="p-4 text-center text-gray-500">
            <div className="text-4xl mb-2">📊</div>
            <p>No transactions found.</p>
            <p className="text-sm">Start adding expenses to see them here!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionList; 