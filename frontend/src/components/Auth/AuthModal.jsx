import React, { useEffect, useState } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './SignupForm';

const AuthModal = ({ isOpen, onClose, onAuthSuccess, required = false, initialMode = 'signup' }) => {
  const [mode, setMode] = useState(initialMode);
  const [message, setMessage] = useState({ text: '', type: '' }); // 'success' or 'error'

  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setMessage({ text: '', type: '' });
    }
  }, [isOpen, initialMode]);

  const handleSuccess = (userOrMessage, token = null) => {
    if (mode === 'signup') {
      // Registration success - show message and switch to login
      setMessage({ text: userOrMessage, type: 'success' });
      setMode('login');
    } else {
      // Login success - close modal and notify parent
      setMessage({ text: '', type: '' });
      onAuthSuccess(userOrMessage, token);
      onClose();
    }
  };

  const handleError = (errorMessage) => {
    setMessage({ text: errorMessage, type: 'error' });
  };

  const switchMode = () => {
    setMessage({ text: '', type: '' });
    setMode(mode === 'login' ? 'signup' : 'login');
  };

  const handleClose = () => {
    if (required) return; // Don't allow closing if auth is required
    setMessage({ text: '', type: '' });
    setMode(initialMode);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={handleClose}>
      <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
        {!required && (
          <button className="auth-modal-close" onClick={handleClose}>
            ✕
          </button>
        )}
        
        {message.text && (
          <div className={`auth-message ${message.type}`}>
            {message.text}
          </div>
        )}

        {mode === 'login' ? (
          <LoginForm
            onSuccess={handleSuccess}
            onError={handleError}
            onSwitchToSignup={switchMode}
          />
        ) : (
          <SignupForm
            onSuccess={handleSuccess}
            onError={handleError}
            onSwitchToLogin={switchMode}
          />
        )}
      </div>
    </div>
  );
};

export default AuthModal;