import React from 'react';
import { AuthProvider, useAuth } from './utils/auth';
import LoginButton from './components/auth/LoginButton';
import UserInfo from './components/auth/UserInfo';
import TodoList from './components/todos/TodoList';

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">Yata</h1>
            <div className="flex items-center">
              {user ? <UserInfo /> : <LoginButton />}
            </div>
          </div>
        </div>
      </header>

      <main>
        {user ? (
          <TodoList />
        ) : (
          <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                <span className="block">Welcome to Yata</span>
                <span className="block text-blue-600">Your Simple Todo App</span>
              </h2>
              <p className="mt-4 max-w-md mx-auto text-xl text-gray-500">
                Sign in with Google to start managing your todos.
              </p>
              <div className="mt-8 flex justify-center">
                <LoginButton />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;