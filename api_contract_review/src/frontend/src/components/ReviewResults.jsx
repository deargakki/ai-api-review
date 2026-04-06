import React, { useState } from 'react';

const ReviewResults = ({ result }) => {
  const [activeTab, setActiveTab] = useState('summary');

  if (!result) {
    return null;
  }

  const { detailed_report } = result;

  if (!detailed_report) {
    return (
      <div className="w-full max-w-4xl mt-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Review Results</h2>
          <p className="text-gray-600 dark:text-gray-400">Detailed report not available</p>
        </div>
      </div>
    );
  }

  const { comparison, spectral, recommendations } = detailed_report;

  return (
    <div className="w-full max-w-4xl mt-8">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6">Review Results</h2>

        <div className="mb-6">
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('summary')}
              className={`px-4 py-2 font-medium ${activeTab === 'summary' ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            >
              Summary
            </button>
            <button
              onClick={() => setActiveTab('breaking')}
              className={`px-4 py-2 font-medium ${activeTab === 'breaking' ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            >
              Breaking Changes
            </button>
            <button
              onClick={() => setActiveTab('spectral')}
              className={`px-4 py-2 font-medium ${activeTab === 'spectral' ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            >
              Spectral Issues
            </button>
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-4 py-2 font-medium ${activeTab === 'recommendations' ? 'border-b-2 border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
            >
              Recommendations
            </button>
          </div>
        </div>

        {activeTab === 'summary' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">API Status</h3>
              <p className={`px-3 py-2 rounded ${comparison.api_status === 'new' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : comparison.api_status === 'modified' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
                {comparison.api_status.charAt(0).toUpperCase() + comparison.api_status.slice(1)}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Changes Summary</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Changes</p>
                  <p className="text-xl font-bold">{comparison.summary.total_changes || 0}</p>
                </div>
                <div className="bg-red-100 dark:bg-red-900 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Breaking Changes</p>
                  <p className="text-xl font-bold">{comparison.summary.breaking_changes || 0}</p>
                </div>
                <div className="bg-green-100 dark:bg-green-900 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Non-Breaking Changes</p>
                  <p className="text-xl font-bold">{comparison.summary.non_breaking_changes || 0}</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Spectral Issues</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total Issues</p>
                  <p className="text-xl font-bold">{spectral.summary.total || 0}</p>
                </div>
                <div className="bg-red-100 dark:bg-red-900 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Errors</p>
                  <p className="text-xl font-bold">{spectral.summary.errors || 0}</p>
                </div>
                <div className="bg-yellow-100 dark:bg-yellow-900 p-3 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Warnings</p>
                  <p className="text-xl font-bold">{spectral.summary.warnings || 0}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'breaking' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-2">Breaking Changes</h3>
            {comparison.breaking_changes && comparison.breaking_changes.length > 0 ? (
              <div className="space-y-3">
                {comparison.breaking_changes.map((change, index) => (
                  <div key={index} className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md border border-red-200 dark:border-red-800">
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">{change.type || 'Unknown'}</h4>
                      <span className={`px-2 py-1 text-xs rounded ${change.severity === 'Critical' ? 'bg-red-600 text-white' : change.severity === 'High' ? 'bg-orange-600 text-white' : change.severity === 'Medium' ? 'bg-yellow-600 text-white' : 'bg-blue-600 text-white'}`}>
                        {change.severity || 'Low'}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{change.description || 'No description'}</p>
                    {change.path && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Path: {change.path}</p>
                    )}
                    {change.method && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Method: {change.method}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No breaking changes found.</p>
            )}

            <h3 className="text-lg font-semibold mt-6 mb-2">Non-Breaking Changes</h3>
            {comparison.non_breaking_changes && comparison.non_breaking_changes.length > 0 ? (
              <div className="space-y-3">
                {comparison.non_breaking_changes.map((change, index) => (
                  <div key={index} className="bg-green-50 dark:bg-green-900/20 p-4 rounded-md border border-green-200 dark:border-green-800">
                    <h4 className="font-medium">{change.type || 'Unknown'}</h4>
                    <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{change.description || 'No description'}</p>
                    {change.path && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Path: {change.path}</p>
                    )}
                    {change.method && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Method: {change.method}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No non-breaking changes found.</p>
            )}
          </div>
        )}

        {activeTab === 'spectral' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-2">Spectral Issues</h3>
            {spectral.issues && spectral.issues.length > 0 ? (
              <div className="space-y-3">
                {spectral.issues.map((issue, index) => (
                  <div key={index} className={`p-4 rounded-md border ${issue.severity === 'error' ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800' : issue.severity === 'warning' ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800' : 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'}`}>
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">{issue.code || 'Unknown'}</h4>
                      <span className={`px-2 py-1 text-xs rounded ${issue.severity === 'error' ? 'bg-red-600 text-white' : issue.severity === 'warning' ? 'bg-yellow-600 text-white' : 'bg-blue-600 text-white'}`}>
                        {issue.severity || 'info'}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{issue.message || 'No message'}</p>
                    {issue.path && issue.path.length > 0 && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Path: {issue.path.join('.')}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No spectral issues found.</p>
            )}
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold mb-2">Recommendations</h3>
            {recommendations && recommendations.length > 0 ? (
              <div className="space-y-3">
                {recommendations.map((rec, index) => (
                  <div key={index} className={`p-4 rounded-md border ${rec.severity === 'high' ? 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800' : rec.severity === 'medium' ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800' : 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800'}`}>
                    <div className="flex justify-between items-start">
                      <h4 className="font-medium">{rec.type || 'General'}</h4>
                      <span className={`px-2 py-1 text-xs rounded ${rec.severity === 'high' ? 'bg-red-600 text-white' : rec.severity === 'medium' ? 'bg-yellow-600 text-white' : 'bg-blue-600 text-white'}`}>
                        {rec.severity || 'low'}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{rec.message || 'No message'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No recommendations available.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewResults;