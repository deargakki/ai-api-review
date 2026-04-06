import React from 'react';

const ProgressBar = ({ progress, message }) => {
  if (progress === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-2xl mt-8">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold mb-4">Review Progress</h3>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-2">
          <div 
            className="bg-blue-600 h-4 rounded-full transition-all duration-300 ease-in-out" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {message || `Progress: ${progress}%`}
        </p>
      </div>
    </div>
  );
};

export default ProgressBar;