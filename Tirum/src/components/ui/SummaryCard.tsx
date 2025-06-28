import React from 'react';

interface SummaryCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  change?: string;
  onClick?: () => void;
}

const SummaryCard: React.FC<SummaryCardProps> = ({ 
  title, 
  value, 
  icon, 
  color, 
  change, 
  onClick 
}) => {
  return (
    <div 
      className={`bg-white overflow-hidden shadow rounded-lg cursor-pointer transition-transform hover:scale-105 ${onClick ? 'hover:shadow-lg' : ''}`}
      onClick={onClick}
    >
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 rounded-md flex items-center justify-center ${color}`}>
              <span className="text-white font-bold text-lg">{icon}</span>
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="text-lg font-medium text-gray-900">
                {typeof value === 'number' ? `$${value.toFixed(2)}` : value}
              </dd>
              {change && (
                <dd className="text-sm text-gray-500">
                  {change}
                </dd>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryCard; 