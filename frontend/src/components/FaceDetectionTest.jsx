import React, { useRef, useState, useEffect } from 'react';
import SimpleFaceDetection from './SimpleFaceDetection.jsx';

/**
 * Test component for face detection debugging
 */
const FaceDetectionTest = () => {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [faceStatus, setFaceStatus] = useState({ facesCount: 0, confidence: 0 });
  const [violations, setViolations] = useState([]);

  useEffect(() => {
    // Auto-start camera when component mounts
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });
      
      setStream(mediaStream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          setIsActive(true);
        };
      }
    } catch (error) {
      console.error('Camera access error:', error);
    }
  };

  const handleFaceStatus = (status) => {
    setFaceStatus(status);
  };

  const handleViolation = (message) => {
    const violation = {
      id: Date.now(),
      message,
      timestamp: new Date().toLocaleTimeString()
    };
    setViolations(prev => [...prev.slice(-4), violation]); // Keep last 5
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>🎯 Face Detection Test</h2>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
        <div style={{ position: 'relative' }}>
          <video
            ref={videoRef}
            style={{
              width: '320px',
              height: '240px',
              border: '2px solid #333',
              borderRadius: '8px'
            }}
            muted
            playsInline
            autoPlay
          />
          
          {isActive && (
            <SimpleFaceDetection
              videoRef={videoRef}
              isActive={isActive}
              onFaceStatus={handleFaceStatus}
              onViolation={handleViolation}
            />
          )}
        </div>
        
        <div style={{ flex: 1 }}>
          <div style={{ 
            background: '#f5f5f5', 
            padding: '15px', 
            borderRadius: '8px',
            marginBottom: '15px'
          }}>
            <h3>📊 Current Status</h3>
            <div style={{ fontSize: '18px' }}>
              👥 <strong>Faces Detected: {faceStatus.facesCount}</strong>
            </div>
            <div style={{ fontSize: '16px', color: '#666' }}>
              🎯 Confidence: {Math.round(faceStatus.confidence * 100)}%
            </div>
            <div style={{ fontSize: '14px', color: '#888', marginTop: '5px' }}>
              Last Detection: {faceStatus.lastDetection ? new Date(faceStatus.lastDetection).toLocaleTimeString() : 'Never'}
            </div>
          </div>
          
          <div style={{ 
            background: violations.length > 0 ? '#ffe6e6' : '#e6f7e6', 
            padding: '15px', 
            borderRadius: '8px' 
          }}>
            <h3>⚠️ Violations ({violations.length})</h3>
            {violations.length === 0 ? (
              <div style={{ color: '#4CAF50' }}>✅ No violations detected</div>
            ) : (
              violations.map(violation => (
                <div key={violation.id} style={{ 
                  background: '#fff', 
                  padding: '8px', 
                  margin: '5px 0', 
                  borderRadius: '4px',
                  borderLeft: '4px solid #F44336'
                }}>
                  <div style={{ fontWeight: 'bold', color: '#F44336' }}>
                    {violation.timestamp}
                  </div>
                  <div>{violation.message}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      <div style={{ 
        background: '#e3f2fd', 
        padding: '15px', 
        borderRadius: '8px',
        fontSize: '14px'
      }}>
        <h4>🧪 Test Instructions:</h4>
        <ul>
          <li><strong>Single Person:</strong> Should detect 1 face consistently</li>
          <li><strong>Two People:</strong> Should detect 2 faces and trigger violation</li>
          <li><strong>No Person:</strong> Should detect 0 faces (no violation)</li>
          <li><strong>Hand/Object:</strong> Should not be counted as a face</li>
        </ul>
      </div>
    </div>
  );
};

export default FaceDetectionTest;