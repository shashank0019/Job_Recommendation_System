import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Local storage helper functions
const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9);
const generateToken = () => Math.random().toString(36).substr(2) + Date.now().toString(36);
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const [redirectPath, setRedirectPath] = useState(null);

  // Simple token validation (localStorage-based system)
  const validateStoredAuth = (storedToken, storedUser) => {
    try {
      const userData = JSON.parse(storedUser);
      if (storedToken && userData) {
        setUser(userData);
        setToken(storedToken);
        console.log('✅ Authentication restored from localStorage');
        return true;
      }
    } catch (error) {
      console.error('Stored auth data corrupted:', error);
      // Clear corrupted data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
    return false;
  };

  const clearAuthState = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    setUser(null);
    setToken(null);
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('user_data');

      if (!storedToken || !storedUser) {
        setLoading(false);
        setInitialized(true);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/auth/profile`, {
          headers: { Authorization: `Bearer ${storedToken}` }
        });
        const result = await response.json();

        if (!response.ok || !result.success || !result.user) {
          throw new Error(result.error || 'Stored session is invalid');
        }

        setUser(result.user);
        setToken(storedToken);
        localStorage.setItem('user_data', JSON.stringify(result.user));
        console.log('✅ Backend authentication restored');
      } catch (error) {
        console.warn('⚠️ Stored authentication is invalid; clearing session');
        clearAuthState();
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const result = await response.json();
      if (!response.ok || !result.success) return { success: false, error: result.error || 'Sign in failed' };
      const userToken = result.token;
      const userData = result.user;
      setUser(userData);
      setToken(userToken);
      localStorage.setItem('auth_token', userToken);
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      console.log('✅ User logged in successfully');
      return { success: true, user: userData, token: userToken };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed. Please try again.' };
    }
  };

  const signup = async (name, email, password) => {
    try {
      console.log('🔄 Attempting signup for:', email);
      const response = await fetch(`${API_BASE}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });
      const result = await response.json();
      if (!response.ok || !result.success) return { success: false, error: result.error || 'Registration failed' };
      console.log('✅ User registered successfully');
      return { success: true, message: result.message };
    } catch (error) {
      console.log('❌ Signup error:', error);
      return { success: false, error: 'Registration failed. Please try again.' };
    }
  };

  const logout = async () => {
    // Clear state and storage
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
    
    console.log('✅ User logged out');
  };

  const updateProfile = async (profileData) => {
    try {
      console.log('🔄 Updating profile with data:', profileData);
      console.log('👤 Current user state:', user);
      
      if (!user) {
        console.error('❌ No user logged in');
        return { success: false, error: 'No user logged in' };
      }
      
      if (!user.id) {
        console.error('❌ User has no ID:', user);
        return { success: false, error: 'User ID is missing' };
      }
      
      // Get existing users from localStorage
      const storedUsers = localStorage.getItem('local_users') || '[]';
      const users = JSON.parse(storedUsers);
      console.log('📦 Total users in local_users:', users.length);
      console.log('🔍 Looking for user ID:', user.id);
      
      // Find user by ID or email as fallback
      let userIndex = users.findIndex(u => u.id === user.id);
      if (userIndex === -1 && user.email) {
        console.log('⚠️ User ID not found, trying email:', user.email);
        userIndex = users.findIndex(u => u.email === user.email);
        if (userIndex !== -1) {
          console.log('✅ Found user by email');
        }
      }
      
      if (userIndex === -1) {
        console.error('❌ User not found in local_users');
        console.error('Available user IDs:', users.map(u => u.id));
        return { success: false, error: 'User not found in database' };
      }
      
      console.log('✅ Found user at index:', userIndex);
      
      // Separate name from profile-specific data
      const { name, mobile, gender, state, skills, employment_status } = profileData;
      
      // Update user data with profile nested structure
      const updatedUserData = {
        ...users[userIndex],
        name: name || users[userIndex].name, // Update name at top level
        profile: {
          ...users[userIndex].profile, // Preserve existing profile data
          mobile: mobile || users[userIndex].profile?.mobile || '',
          gender: gender || users[userIndex].profile?.gender || '',
          state: state || users[userIndex].profile?.state || '',
          skills: skills || users[userIndex].profile?.skills || [],
          employment_status: employment_status || users[userIndex].profile?.employment_status || ''
        },
        updated_at: new Date().toISOString()
      };
      
      users[userIndex] = updatedUserData;
      
      // Save back to localStorage
      localStorage.setItem('local_users', JSON.stringify(users));
      console.log('💾 Saved to local_users:', updatedUserData);
      
      // Update current user state (with profile data, without password)
      const updatedUser = {
        id: updatedUserData.id,
        name: updatedUserData.name,
        email: updatedUserData.email,
        profile: updatedUserData.profile, // ✅ INCLUDE PROFILE OBJECT
        created_at: updatedUserData.created_at,
        updated_at: updatedUserData.updated_at
      };
      
      setUser(updatedUser);
      localStorage.setItem('user_data', JSON.stringify(updatedUser));
      console.log('✅ Profile updated successfully, new user state:', updatedUser);
      
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('❌ Profile update error:', error);
      return { success: false, error: 'Failed to update profile' };
    }
  };

  const isAuthenticated = () => {
    return !!(user && token);
  };


  const getAndClearRedirectPath = () => {
    const path = redirectPath;
    setRedirectPath(null);
    return path;
  };

  const value = {
    user,
    token,
    loading,
    initialized,
    isAuthenticated,
    login,
    signup,
    logout,
    updateProfile,
    setRedirectPath,
    getAndClearRedirectPath
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;