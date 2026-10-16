import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from '../components/Auth/AuthModal';
import LandingPreview from './LandingPreview';

const AuthGate = ({ children }) => {
  const { user, isAuthenticated, loading, initialized, setRedirectPath, getAndClearRedirectPath } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('signup');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Once auth is initialized, show modal if not authenticated
    if (initialized && !isAuthenticated()) {
      // Save current location for redirect after auth
      if (location.pathname !== '/') {
        setRedirectPath(location.pathname + location.search);
      }
      setShowAuthModal(true);
    }
  }, [initialized, isAuthenticated, location, setRedirectPath]);

  const handleAuthSuccess = (userData, token) => {
    console.log('🎉 User authenticated:', userData.name);
    setShowAuthModal(false);
    
    // Small delay to ensure auth state is updated
    setTimeout(() => {
      // Check if there's a redirect path and navigate to it
      const redirectPath = getAndClearRedirectPath();
      if (redirectPath && redirectPath !== '/') {
        console.log('🔄 Redirecting to saved path:', redirectPath);
        navigate(redirectPath, { replace: true });
      } else {
        // No specific redirect path, go to dashboard (home page)
        console.log('🔄 Redirecting to dashboard after sign-in');
        navigate('/', { replace: true });
      }
    }, 100);
  };

  // Show loading while authentication is being initialized
  if (loading || !initialized) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-content">
          <div className="loading-spinner"></div>
          <h2>Loading...</h2>
          <p>Initializing Career Guidance Platform</p>
        </div>
      </div>
    );
  }

  // Show authentication modal if not authenticated
  if (!isAuthenticated()) {
    return (
      <div className="auth-required-screen">
        {/* Fixed header with sign in button */}
        <div className="auth-header">
          <div className="auth-header-content">
            <div className="logo">
              <h2>🚀 Career Guidance Platform</h2>
            </div>
            <div className="auth-header-actions">
              <button 
                className="sign-in-btn"
                onClick={() => {
                  setAuthMode('login');
                  setShowAuthModal(true);
                }}
              >
                Sign In
              </button>
              <button 
                className="get-started-btn"
                onClick={() => {
                  setAuthMode('signup');
                  setShowAuthModal(true);
                }}
              >
                Get Started Free
              </button>
            </div>
          </div>
        </div>

        {/* Main content - landing preview */}
        <div className="auth-main-content">
          <LandingPreview />
        </div>

        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
          required={true}
          initialMode={authMode}
        />

        <style>{`
          .auth-required-screen {
            min-height: 100vh;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          }
          
          .auth-required-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
            text-align: center;
          }
          
          .auth-required-content h1 {
            color: #1f2937;
            margin-bottom: 16px;
            font-size: 2rem;
            font-weight: 700;
            color: #1a1a1a;
          }

          .auth-header-actions {
            display: flex;
            gap: 1rem;
            align-items: center;
          }

          .sign-in-btn {
            background: transparent;
            color: #007bff;
            border: 1px solid #007bff;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
          }

          .sign-in-btn:hover {
            background: #007bff;
            color: white;
          }

          .get-started-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
          }

          .get-started-btn:hover {
            background: #0056b3;
            transform: translateY(-1px);
          }

          .auth-main-content {
            padding-top: 80px; /* Account for fixed header */
          }

          @media (max-width: 768px) {
            .auth-header-content {
              padding: 0 1rem;
            }
            
            .logo h2 {
              font-size: 1.2rem;
            }
            
            .auth-header-actions {
              gap: 0.5rem;
            }
            
            .sign-in-btn, .get-started-btn {
              padding: 0.4rem 1rem;
              font-size: 0.9rem;
            }
          }
        `}</style>
      </div>
    );
  }

  // User is authenticated, show the main application
  return (
    <div className="authenticated-app">
      <div className="user-welcome-banner">
        <div className="welcome-content">
          <span>Welcome back, <strong>{user?.name}</strong>!</span>
          <small>Ready to advance your career today?</small>
        </div>
      </div>
      {children}
    </div>
  );
};

export default AuthGate;