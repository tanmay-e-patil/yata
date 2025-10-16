import React from 'react';
import { useAuth } from '../../utils/auth';

const UserInfo: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        {user.avatar_url && (
          <img
            src={user.avatar_url}
            alt={user.name}
            className="w-8 h-8 rounded-full"
          />
        )}
        <span className="text-sm font-medium text-gray-700">{user.name}</span>
      </div>
      <button
        onClick={logout}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Logout
      </button>
    </div>
  );
};

export default UserInfo;