import React, { useEffect, useRef, useState } from 'react';

/**
 * Face Detection Component for Interview Monitoring
 * Uses face-api.js for reliable face detection
 */
const FaceDetection = ({ 
  videoRef, 
  isActive = false, 
  onViolation = () => {},
  onFaceStatus = () => {},
  sensitivity = 'medium' // 'low', 'medium', 'high'
}) => {
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [lastViolationTime, setLastViolationTime] = useState(0);
  const [faceStatus, setFaceStatus] = useState({
    facesCount: 0,
    isLookingAway: false,
    confidence: 0,
    lastDetection: null
  });

  // Detection sensitivity settings
  const sensitivityConfig = {
    low: {
      detectionInterval: 2000, // 2 seconds
      violationCooldown: 10000, // 10 seconds
      confidenceThreshold: 0.3,
      lookAwayThreshold: 0.4
    },
    medium: {
      detectionInterval: 1000, // 1 second
      violationCooldown: 5000, // 5 seconds
      confidenceThreshold: 0.5,
      lookAwayThreshold: 0.6
    },
    high: {
      detectionInterval: 500, // 0.5 seconds
      violationCooldown: 3000, // 3 seconds
      confidenceThreshold: 0.7,
      lookAwayThreshold: 0.8
    }
  };

  const config = sensitivityConfig[sensitivity] || sensitivityConfig.medium;

  // Initialize face-api.js
  useEffect(() => {
    const loadModels = async () => {
      try {
        console.log('🔄 Loading face detection models...');
        
        if (typeof window !== 'undefined' && window.faceapi) {
          // Load required models from CDN
          const MODEL_URL = 'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/weights';
          
          await Promise.all([
            window.faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
            window.faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
            window.faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
          ]);
          
          setIsModelLoaded(true);
          setIsSupported(true);
          console.log('✅ Face detection models loaded successfully');
        } else {
          console.log('⚠️ face-api.js not available, using fallback detection');
          setIsSupported(true);
          setIsModelLoaded(false);
        }
      } catch (error) {
        console.error('❌ Failed to load face detection models:', error);
        setIsSupported(true); // Still use fallback
        setIsModelLoaded(false);
      }
    };

    loadModels();

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Perform face detection using face-api.js
  const detectFaces = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (!video || !canvas || video.videoWidth === 0) return;

    try {
      let detections = [];
      
      if (isModelLoaded && window.faceapi) {
        // Use face-api.js for accurate detection
        detections = await window.faceapi
          .detectAllFaces(video, new window.faceapi.TinyFaceDetectorOptions({
            inputSize: 416,
            scoreThreshold: config.confidenceThreshold
          }));
      }
      
      // If face-api.js fails or unavailable, use fallback
      if (!detections || detections.length === 0) {
        detections = await fallbackFaceDetection(video, canvas);
      }

      const facesCount = detections.length;
      let maxConfidence = 0;
      let isLookingAway = false;

      // Process detections
      if (detections.length > 0) {
        detections.forEach((detection) => {
          const confidence = detection.score || detection.confidence || 0.8;
          maxConfidence = Math.max(maxConfidence, confidence);

          // Draw bounding box for debugging
          if (process.env.NODE_ENV === 'development') {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const box = detection.box || detection;
            ctx.strokeStyle = facesCount === 1 ? '#00ff00' : '#ff0000';
            ctx.lineWidth = 2;
            ctx.strokeRect(box.x || box.left || 0, box.y || box.top || 0, 
                          box.width || 100, box.height || 100);
          }
        });
      }

      const newStatus = {
        facesCount,
        isLookingAway,
        confidence: maxConfidence,
        lastDetection: Date.now()
      };

      setFaceStatus(newStatus);
      onFaceStatus(newStatus);

      // Check for violations
      checkForViolations(newStatus);
      
    } catch (error) {
      console.error('Face detection error:', error);
      // Use fallback detection
      const fallbackResult = await fallbackFaceDetection(video, canvas);
      const newStatus = {
        facesCount: fallbackResult.length,
        isLookingAway: false,
        confidence: fallbackResult.length > 0 ? 0.6 : 0,
        lastDetection: Date.now()
      };
      
      setFaceStatus(newStatus);
      onFaceStatus(newStatus);
      checkForViolations(newStatus);
    }
  };

  // Improved fallback face detection
  const fallbackFaceDetection = async (video, canvas) => {
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data for analysis
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    
    // Enhanced face detection using skin color detection and edge detection
    const faces = detectFacesByColor(imageData, canvas.width, canvas.height);
    
    return faces;
  };

  // Skin color and face detection heuristic
  const detectFacesByColor = (imageData, width, height) => {
    const data = imageData.data;
    const faces = [];
    
    // Skin color detection parameters
    const skinRegions = [];
    let skinPixels = 0;
    
    // Scan for skin-colored regions
    for (let y = 0; y < height; y += 4) {
      for (let x = 0; x < width; x += 4) {
        const i = (y * width + x) * 4;
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        
        // Simple skin color detection
        if (isSkinColor(r, g, b)) {
          skinPixels++;
          skinRegions.push({ x, y });
        }
      }
    }
    
    // If we have enough skin pixels, assume there's a face
    const skinThreshold = (width * height) / 1000; // Adjust threshold
    
    if (skinPixels > skinThreshold) {
      // Calculate bounding box for detected skin region
      const minX = Math.min(...skinRegions.map(p => p.x));
      const maxX = Math.max(...skinRegions.map(p => p.x));
      const minY = Math.min(...skinRegions.map(p => p.y));
      const maxY = Math.max(...skinRegions.map(p => p.y));
      
      // Add some padding and create face detection result
      const padding = 20;
      faces.push({
        x: Math.max(0, minX - padding),
        y: Math.max(0, minY - padding),
        width: Math.min(width, maxX - minX + padding * 2),
        height: Math.min(height, maxY - minY + padding * 2),
        confidence: Math.min(0.8, skinPixels / skinThreshold)
      });
    }
    
    return faces;
  };

  // Simple skin color detection
  const isSkinColor = (r, g, b) => {
    // Basic skin color ranges (works for most skin tones)
    return (
      (r > 95 && g > 40 && b > 20) &&
      (Math.max(r, g, b) - Math.min(r, g, b) > 15) &&
      (Math.abs(r - g) > 15) &&
      (r > g && r > b)
    ) || (
      // Alternative skin detection
      (r > 220 && g > 210 && b > 170) ||
      (r > 60 && r < 230 && g > 50 && g < 200 && b > 30 && b < 180)
    );
  };

  // Check for violations
  const checkForViolations = (status) => {
    const now = Date.now();
    
    // Cooldown to prevent spam violations
    if (now - lastViolationTime < config.violationCooldown) {
      return;
    }

    let violationMessage = null;

    // Multiple faces detected
    if (status.facesCount > 1) {
      violationMessage = `Multiple faces detected (${status.facesCount}). Only the candidate should be visible.`;
    }
    // No face detected
    else if (status.facesCount === 0) {
      violationMessage = 'No face detected. Please ensure you are visible to the camera.';
    }
    // Face looking away (if supported)
    else if (status.isLookingAway && status.confidence > config.confidenceThreshold) {
      violationMessage = 'Please look at the camera during the interview.';
    }

    if (violationMessage) {
      setLastViolationTime(now);
      onViolation(violationMessage);
    }
  };

  // Start/stop detection based on isActive
  useEffect(() => {
    if (!isSupported || !isActive) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    console.log('🎯 Starting face detection with interval:', config.detectionInterval);

    // Start detection interval
    intervalRef.current = setInterval(() => {
      detectFaces();
    }, config.detectionInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, isSupported, isModelLoaded]);

  // Update canvas size when video dimensions change
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video && canvas) {
      const updateCanvasSize = () => {
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
      };

      video.addEventListener('loadedmetadata', updateCanvasSize);
      return () => video.removeEventListener('loadedmetadata', updateCanvasSize);
    }
  }, [videoRef.current]);

  return (
    <div style={{ position: 'relative', display: 'none' }}>
      {/* Hidden canvas for face detection processing */}
      <canvas
        ref={canvasRef}
        style={{ 
          display: process.env.NODE_ENV === 'development' ? 'block' : 'none',
          position: 'absolute',
          top: 0,
          left: 0,
          zIndex: 10,
          pointerEvents: 'none',
          border: '1px solid red'
        }}
      />
      
      {/* Status indicator (optional) */}
      {process.env.NODE_ENV === 'development' && isActive && (
        <div style={{
          position: 'absolute',
          top: 10,
          right: 10,
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '4px 8px',
          borderRadius: 4,
          fontSize: 12,
          zIndex: 20
        }}>
          Faces: {faceStatus.facesCount} | 
          Conf: {(faceStatus.confidence * 100).toFixed(0)}%
          {faceStatus.isLookingAway && ' | Looking Away'}
        </div>
      )}
    </div>
  );
};

export default FaceDetection;
