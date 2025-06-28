import React from 'react';
import type { UserSummary } from '../../types/userSummary';

interface KhataSummaryProps {
  userSummary: UserSummary;
}

const KhataSummary: React.FC<KhataSummaryProps> = ({ userSummary }) => {
  const { to_take_with, to_return_with, total_to_take, total_to_return } = userSummary;

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Khata Summary
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Money you owe and money owed to you
        </p>
      </div>
      <div className="border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
          {/* Money to Take */}
          <div>
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <h4 className="text-sm font-medium text-gray-900">Money to Take</h4>
              <span className="ml-auto text-lg font-bold text-green-600">
                ${total_to_take.toFixed(2)}
              </span>
            </div>
            {to_take_with.length > 0 ? (
              <ul className="space-y-2">
                {to_take_with.map((item, index) => (
                  <li key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                    <span className="text-sm text-gray-700">{item.borrower__username}</span>
                    <span className="text-sm font-medium text-green-600">
                      ${item.total.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">
                No money to take
              </p>
            )}
          </div>

          {/* Money to Return */}
          <div>
            <div className="flex items-center mb-4">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <h4 className="text-sm font-medium text-gray-900">Money to Return</h4>
              <span className="ml-auto text-lg font-bold text-red-600">
                ${total_to_return.toFixed(2)}
              </span>
            </div>
            {to_return_with.length > 0 ? (
              <ul className="space-y-2">
                {to_return_with.map((item, index) => (
                  <li key={index} className="flex justify-between items-center p-2 bg-red-50 rounded">
                    <span className="text-sm text-gray-700">{item.lender__username}</span>
                    <span className="text-sm font-medium text-red-600">
                      ${item.total.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500 text-center py-4">
                No money to return
              </p>
            )}
          </div>
        </div>

        {/* Net Balance */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-900">Net Balance</span>
            <span className={`text-lg font-bold ${total_to_take - total_to_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              ${(total_to_take - total_to_return).toFixed(2)}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {total_to_take - total_to_return >= 0 ? 'You are in profit' : 'You owe money'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default KhataSummary; 