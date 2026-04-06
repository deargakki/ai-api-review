import React, { useState } from 'react';

const ReviewForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    confluencePageId: '',
    githubRepo: '',
    githubFile: '',
    githubBranch: 'master'
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.confluencePageId.trim()) {
      newErrors.confluencePageId = 'Confluence Page ID is required';
    }
    if (!formData.githubRepo.trim()) {
      newErrors.githubRepo = 'GitHub Repo is required (format: owner/repo)';
    } else if (!formData.githubRepo.includes('/')) {
      newErrors.githubRepo = 'GitHub Repo should be in format: owner/repo';
    }
    if (!formData.githubFile.trim()) {
      newErrors.githubFile = 'GitHub File is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit({
        confluence_page_id: formData.confluencePageId,
        github_repo: formData.githubRepo,
        github_file: formData.githubFile,
        github_branch: formData.githubBranch
      });
    }
  };

  return (
    <div className="w-full max-w-2xl">
      <h2 className="text-2xl font-bold mb-6 text-center">API Contract Review</h2>
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Confluence Page ID
          </label>
          <input
            type="text"
            name="confluencePageId"
            value={formData.confluencePageId}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter Confluence Page ID"
          />
          {errors.confluencePageId && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.confluencePageId}</p>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            GitHub Repo
          </label>
          <input
            type="text"
            name="githubRepo"
            value={formData.githubRepo}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter GitHub Repo (owner/repo)"
          />
          {errors.githubRepo && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.githubRepo}</p>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            GitHub File
          </label>
          <input
            type="text"
            name="githubFile"
            value={formData.githubFile}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter GitHub File Path or Filename"
          />
          {errors.githubFile && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.githubFile}</p>
          )}
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            GitHub Branch
          </label>
          <input
            type="text"
            name="githubBranch"
            value={formData.githubBranch}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder="Enter GitHub Branch (default: master)"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Running Review...' : 'Run Review'}
        </button>
      </form>
    </div>
  );
};

export default ReviewForm;