import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ReviewForm from './components/ReviewForm';
import ReviewResults from './components/ReviewResults';
import ProgressBar from './components/ProgressBar';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [user, setUser] = useState(null);
  const [isLogin, setIsLogin] = useState(true);
  const wsRef = useRef(null);

  // 检查用户是否已登录
  useEffect(() => {
    // 从 localStorage 中获取用户信息
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // 建立 WebSocket 连接
  useEffect(() => {
    // 只有在用户登录后才建立 WebSocket 连接
    if (user) {
      // 连接到 WebSocket 服务器
      const ws = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(data.progress);
          setProgressMessage(data.message);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      // 保持连接活跃
      const interval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, 30000);

      // 清理函数
      return () => {
        clearInterval(interval);
        if (wsRef.current) {
          wsRef.current.close();
        }
      };
    }
  }, [user]);

  const handleLogin = (userData) => {
    // 保存用户信息到状态和 localStorage
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleRegister = (userData) => {
    // 保存用户信息到状态和 localStorage
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    setReviewResult(null);
    setProgress(0);
    setProgressMessage('');
  };

  const handleReviewSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setReviewResult(null);
    setProgress(0);
    setProgressMessage('');

    try {
      const response = await axios.post('/api/review', formData, {
        headers: {
          Authorization: `Bearer ${user.token}`
        }
      });
      setReviewResult(response.data);
    } catch (err) {
      console.error('Error running review:', err);
      setError(err.response?.data?.detail || 'An error occurred while running the review');
      setProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  // 如果用户未登录，显示登录或注册表单
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-6xl">
          <header className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              API Contract Review
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Please login or register to access the review system
            </p>
          </header>

          {isLogin ? (
            <LoginForm 
              onLogin={handleLogin} 
              onSwitchToRegister={() => setIsLogin(false)} 
            />
          ) : (
            <RegisterForm 
              onRegister={handleRegister} 
              onSwitchToLogin={() => setIsLogin(true)} 
            />
          )}
        </div>
      </div>
    );
  }

  // 如果用户已登录，显示审查系统界面
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex flex-col items-center p-4">
      <div className="w-full max-w-6xl">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              API Contract Review
            </h1>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Automatically review API contract changes and identify breaking changes
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600 dark:text-gray-400">
              Welcome, {user.username}
            </span>
            <button
              onClick={handleLogout}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-gray-200 font-medium py-2 px-4 rounded-md transition-colors duration-200"
            >
              Logout
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 bg-red-100 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 p-4 rounded-md">
            {error}
          </div>
        )}

        <ReviewForm onSubmit={handleReviewSubmit} isLoading={isLoading} />
        <ProgressBar progress={progress} message={progressMessage} />
        <ReviewResults result={reviewResult} />
      </div>
    </div>
  );
}

export default App;