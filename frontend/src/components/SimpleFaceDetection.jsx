import React, { useEffect, useRef, useState } from 'react';

/**
 * Simple Face Detection Component
 * Uses basic computer vision techniques for reliable face detection
 */
const SimpleFaceDetection = ({ 
  videoRef, 
  isActive = false, 
  onViolation = () => {},
  onFaceStatus = () => {}
}) => {
  console.log('🎯 SimpleFaceDetection component mounted', { isActive, hasVideoRef: !!videoRef });
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const [lastViolationTime, setLastViolationTime] = useState(0);
  const [detectionStartTime, setDetectionStartTime] = useState(0);
  const [consecutiveNoFaceCount, setConsecutiveNoFaceCount] = useState(0);
  const [consecutiveDeviceCount, setConsecutiveDeviceCount] = useState(0);
  const [consecutiveMultipleFaceCount, setConsecutiveMultipleFaceCount] = useState(0);
  const [faceStatus, setFaceStatus] = useState({
    facesCount: 0,
    confidence: 0,
    lastDetection: null
  });

  // Detection settings
  const DETECTION_INTERVAL = 2000; // 2 seconds (faster for better responsiveness)
  const VIOLATION_COOLDOWN = 8000; // 8 seconds between violations
  const GRACE_PERIOD = 10000; // 10 seconds grace period before first violation
  const DEVICE_DETECTION_THRESHOLD = 2; // Require 2 consecutive device detections before violation (4 seconds) - VERY SENSITIVE
  const MULTIPLE_FACE_THRESHOLD = 3; // Require 3 consecutive multiple face detections before violation (6 seconds)
  
  // ULTRA-AGGRESSIVE device detection thresholds (EXTREMELY LOW = MAXIMUM SENSITIVITY)
  const DEVICE_COLOR_THRESHOLD = 0.1; // 0.1% of pixels - ULTRA SENSITIVE
  const GLOW_THRESHOLD = 0.1; // 0.1% of pixels - ULTRA SENSITIVE
  const REFLECTIVE_THRESHOLD = 0.1; // 0.1% of pixels - ULTRA SENSITIVE
  const UNIFORM_THRESHOLD = 0.5; // 0.5% of pixels - ULTRA SENSITIVE
  const EDGE_THRESHOLD = 0.5; // 0.5% edge pixels - ULTRA SENSITIVE
  const RECTANGULAR_THRESHOLD = 0.5; // 0.5% rectangular patterns - ULTRA SENSITIVE
  const CORNER_THRESHOLD = 0.1; // 0.1% corner pixels - ULTRA SENSITIVE
  const HIGH_CONTRAST_THRESHOLD = 0.5; // 0.5% high contrast areas - ULTRA SENSITIVE

  // Start/stop detection
  useEffect(() => {
    if (!isActive || !videoRef.current) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    console.log('🎯 Starting simple face detection...');
    
    // Set detection start time for grace period
    setDetectionStartTime(Date.now());
    setConsecutiveNoFaceCount(0);
    setConsecutiveMultipleFaceCount(0);

    // Start detection
    intervalRef.current = setInterval(() => {
      detectFaces();
    }, DETECTION_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isActive, videoRef.current]);

  const detectFaces = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    console.log('🔍 detectFaces called', {
      video: !!video,
      canvas: !!canvas,
      videoWidth: video?.videoWidth,
      videoHeight: video?.videoHeight,
      videoReadyState: video?.readyState,
      isActive
    });
    
    // Check if video is properly loaded and ready
    if (!video || !canvas || video.videoWidth === 0 || video.videoHeight === 0 || video.readyState < 2) {
      console.log('❌ Video not ready for detection', {
        hasVideo: !!video,
        hasCanvas: !!canvas,
        videoWidth: video?.videoWidth,
        videoHeight: video?.videoHeight,
        readyState: video?.readyState,
        message: 'Video element not ready or has no dimensions'
      });
      return;
    }

    // Additional check: ensure video is actually playing
    if (video.paused || video.ended) {
      console.log('❌ Video is paused or ended, skipping detection');
      return;
    }

    try {
      // Set canvas size to match video - ensure proper dimensions
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;
      
      if (videoWidth <= 0 || videoHeight <= 0) {
        console.log('❌ Invalid video dimensions', { videoWidth, videoHeight });
        return;
      }
      
      canvas.width = videoWidth;
      canvas.height = videoHeight;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.error('❌ Could not get canvas context');
        return;
      }
      
      // Clear canvas first
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw current video frame
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Get image data
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      
      // Verify we got valid image data
      if (!imageData || !imageData.data || imageData.data.length === 0) {
        console.error('❌ No image data captured from video');
        return;
      }
      
      // Analyze the image for faces
      const detectionResult = analyzeForFaces(imageData, canvas.width, canvas.height);
      
      console.log('🔍 Detection result:', detectionResult);
      
      // Update status
      const newStatus = {
        facesCount: detectionResult.faceCount,
        confidence: detectionResult.confidence,
        lastDetection: Date.now(),
        imageDataSize: imageData.data.length,
        skinPercentage: detectionResult.skinPercentage,
        brightPercentage: detectionResult.brightPercentage,
        darkPercentage: detectionResult.darkPercentage,
        devicePercentage: detectionResult.devicePercentage,
        glowPercentage: detectionResult.glowPercentage,
        edgePercentage: detectionResult.edgePercentage,
        rectangularPercentage: detectionResult.rectangularPercentage,
        reflectivePercentage: detectionResult.reflectivePercentage,
        uniformPercentage: detectionResult.uniformPercentage,
        cornerPercentage: detectionResult.cornerPercentage,
        highContrastPercentage: detectionResult.highContrastPercentage,
        hasElectronicDevice: detectionResult.hasElectronicDevice
      };
      
      // DEBUG: Log device detection status
      console.log('🔍 newStatus.hasElectronicDevice:', newStatus.hasElectronicDevice);
      
      setFaceStatus(newStatus);
      onFaceStatus(newStatus);
      
      // Check for violations
      checkViolations(newStatus);
      
    } catch (error) {
      console.error('❌ Face detection error:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        videoWidth: video?.videoWidth,
        videoHeight: video?.videoHeight,
        canvasWidth: canvas?.width,
        canvasHeight: canvas?.height
      });
    }
  };

  // NEW: Detect rectangular/square electronic devices (phones, tablets, laptops)
  const detectRectangularDevices = (imageData, width, height) => {
    const data = imageData.data;
    const pixelsPerRow = width * 4;
    
    // Look for rectangular regions with consistent device-like colors
    let rectangularRegions = [];
    const gridSize = 20; // Check in 20x20 pixel blocks
    
    for (let y = 0; y < height - gridSize; y += gridSize) {
      for (let x = 0; x < width - gridSize; x += gridSize) {
        // Analyze this block
        let deviceColorCount = 0;
        let totalInBlock = 0;
        let avgR = 0, avgG = 0, avgB = 0;
        let minBrightness = 255, maxBrightness = 0;
        
        // Check pixels in this block
        for (let dy = 0; dy < gridSize; dy += 2) {
          for (let dx = 0; dx < gridSize; dx += 2) {
            const px = x + dx;
            const py = y + dy;
            if (px >= width || py >= height) continue;
            
            const idx = (py * pixelsPerRow) + (px * 4);
            const r = data[idx];
            const g = data[idx + 1];
            const b = data[idx + 2];
            
            if (r === undefined) continue;
            
            avgR += r;
            avgG += g;
            avgB += b;
            totalInBlock++;
            
            const brightness = (r + g + b) / 3;
            minBrightness = Math.min(minBrightness, brightness);
            maxBrightness = Math.max(maxBrightness, brightness);
            
            // Check if this pixel looks like a device
            if (isElectronicDevice(r, g, b) || isScreenGlow(r, g, b)) {
              deviceColorCount++;
            }
          }
        }
        
        if (totalInBlock === 0) continue;
        
        avgR /= totalInBlock;
        avgG /= totalInBlock;
        avgB /= totalInBlock;
        
        const devicePercentageInBlock = (deviceColorCount / totalInBlock) * 100;
        const colorVariance = maxBrightness - minBrightness;
        
        // Check if this block looks like a device:
        // 1. High percentage of device-colored pixels (>20% - more sensitive)
        // 2. Relatively uniform color (low variance < 90) OR has screen glow (high variance > 90)
        // 3. Not primarily skin-colored (allow some skin for person holding device)
        const avgBrightness = (avgR + avgG + avgB) / 3;
        const isSkin = isSkinColor(avgR, avgG, avgB);
        const isDark = avgBrightness < 100; // Dark devices (phones/tablets)
        const isLight = avgBrightness > 150; // Light devices or screens
        
        const isDeviceBlock = devicePercentageInBlock > 20 && 
                             (colorVariance < 90 || colorVariance > 90) &&
                             (isDark || isLight || !isSkin);
        
        if (isDeviceBlock) {
          rectangularRegions.push({
            x, y,
            width: gridSize,
            height: gridSize,
            devicePercentage: devicePercentageInBlock,
            avgColor: { r: avgR, g: avgG, b: avgB },
            variance: colorVariance
          });
        }
      }
    }
    
    // Merge nearby regions to find larger rectangular devices
    const mergedRegions = mergeRectangularRegions(rectangularRegions, gridSize);
    
    // Return detection result
    return {
      count: mergedRegions.length,
      regions: mergedRegions,
      largestArea: mergedRegions.length > 0 ? Math.max(...mergedRegions.map(r => r.width * r.height)) : 0,
      confidence: mergedRegions.length > 0 ? Math.min(1.0, mergedRegions.length * 0.3) : 0
    };
  };

  // Helper: Merge nearby rectangular regions
  const mergeRectangularRegions = (regions, threshold) => {
    if (regions.length === 0) return [];
    
    const merged = [];
    const used = new Set();
    
    for (let i = 0; i < regions.length; i++) {
      if (used.has(i)) continue;
      
      let region = { ...regions[i] };
      used.add(i);
      
      // Try to merge with nearby regions
      let changed = true;
      while (changed) {
        changed = false;
        for (let j = 0; j < regions.length; j++) {
          if (used.has(j)) continue;
          
          const other = regions[j];
          // Check if regions are adjacent or overlapping
          const isAdjacent = 
            Math.abs(region.x - other.x) <= threshold * 2 &&
            Math.abs(region.y - other.y) <= threshold * 2;
          
          if (isAdjacent) {
            // Merge regions
            const newX = Math.min(region.x, other.x);
            const newY = Math.min(region.y, other.y);
            const newWidth = Math.max(region.x + region.width, other.x + other.width) - newX;
            const newHeight = Math.max(region.y + region.height, other.y + other.height) - newY;
            
            region = {
              x: newX,
              y: newY,
              width: newWidth,
              height: newHeight,
              devicePercentage: (region.devicePercentage + other.devicePercentage) / 2
            };
            
            used.add(j);
            changed = true;
          }
        }
      }
      
      // Only keep regions that are reasonably large (likely to be actual devices)
      // Phones are typically 100x200+ pixels, tablets 200x300+, laptops 300x200+
      // Lowered threshold to catch devices at various distances from camera
      const area = region.width * region.height;
      const aspectRatio = Math.max(region.width, region.height) / Math.min(region.width, region.height);
      
      // Device characteristics:
      // 1. Large enough area (> 2000 sq pixels = ~45x45 minimum)
      // 2. Rectangular shape (aspect ratio > 1.2, meaning not square)
      if (area > 2000 && aspectRatio > 1.2) {
        merged.push(region);
      }
    }
    
    return merged;
  };

  // NEW: Detect screen light reflections
  const detectScreenReflections = (imageData, width, height) => {
    const data = imageData.data;
    let reflectionCount = 0;
    const threshold = width * height * 0.01; // 1% threshold
    
    // Look for bright reflective areas (typical of screens)
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      
      if (r === undefined) continue;
      
      // Bright reflective surfaces (white/blue glow from screens)
      const brightness = (r + g + b) / 3;
      const isReflective = brightness > 200 && Math.abs(r - g) < 30 && Math.abs(g - b) < 30;
      
      if (isReflective) {
        reflectionCount++;
      }
    }
    
    return {
      count: reflectionCount,
      percentage: (reflectionCount / (width * height)) * 100,
      detected: reflectionCount > threshold
    };
  };

  // NEW: Detect uniform device bodies (solid color regions typical of phones/tablets)
  const detectUniformDeviceRegions = (imageData, width, height) => {
    const data = imageData.data;
    const pixelsPerRow = width * 4;
    let uniformRegions = 0;
    const blockSize = 15; // Check 15x15 blocks
    
    for (let y = 0; y < height - blockSize; y += blockSize) {
      for (let x = 0; x < width - blockSize; x += blockSize) {
        let sumR = 0, sumG = 0, sumB = 0;
        let count = 0;
        
        // Calculate average color in block
        for (let dy = 0; dy < blockSize; dy++) {
          for (let dx = 0; dx < blockSize; dx++) {
            const idx = ((y + dy) * pixelsPerRow) + ((x + dx) * 4);
            if (data[idx] !== undefined) {
              sumR += data[idx];
              sumG += data[idx + 1];
              sumB += data[idx + 2];
              count++;
            }
          }
        }
        
        if (count === 0) continue;
        
        const avgR = sumR / count;
        const avgG = sumG / count;
        const avgB = sumB / count;
        
        // Check variance - uniform regions have low variance
        let variance = 0;
        for (let dy = 0; dy < blockSize; dy++) {
          for (let dx = 0; dx < blockSize; dx++) {
            const idx = ((y + dy) * pixelsPerRow) + ((x + dx) * 4);
            if (data[idx] !== undefined) {
              const diffR = data[idx] - avgR;
              const diffG = data[idx + 1] - avgG;
              const diffB = data[idx + 2] - avgB;
              variance += (diffR * diffR + diffG * diffG + diffB * diffB);
            }
          }
        }
        variance = Math.sqrt(variance / count);
        
        // Low variance (<20) + device-like color = uniform device region
        const isDeviceColor = isElectronicDevice(avgR, avgG, avgB);
        if (variance < 20 && isDeviceColor) {
          uniformRegions++;
        }
      }
    }
    
    return {
      count: uniformRegions,
      percentage: (uniformRegions / ((width / blockSize) * (height / blockSize))) * 100
    };
  };

  const analyzeForFaces = (imageData, width, height) => {
    const data = imageData.data;
    let skinPixels = 0;
    let totalPixels = 0;
    let brightPixels = 0;
    let darkPixels = 0;
    let avgBrightness = 0;
    let devicePixels = 0; // New: count pixels that look like electronic devices
    let glowPixels = 0;   // New: count pixels with screen glow
    let edgePixels = 0;   // New: count edge pixels that might indicate device boundaries
    let rectangularPixels = 0; // New: count pixels that form rectangular patterns
    let reflectivePixels = 0; // NEW: count reflective surfaces (glass, screens)
    let uniformRegionPixels = 0; // NEW: count uniform color regions (device bodies)
    let cornerPixels = 0; // NEW: count corner pixels (device corners are very sharp)
    let highContrastPixels = 0; // NEW: count high contrast pixels (screens have very high contrast)
    
    // NEW: Detect rectangular device shapes (phones, tablets, laptops)
    const rectangularDevices = detectRectangularDevices(imageData, width, height);
    
    // NEW: Detect screen light reflections
    const screenReflections = detectScreenReflections(imageData, width, height);
    
    // NEW: Detect uniform device bodies
    const uniformDeviceRegions = detectUniformDeviceRegions(imageData, width, height);
    
    // ANALYZE EVERY PIXEL for MAXIMUM accuracy (was every 4th pixel)
    for (let i = 0; i < data.length; i += 4) { // Every single pixel (RGBA = 4 bytes)
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      
      // Skip if undefined (shouldn't happen but safety check)
      if (r === undefined || g === undefined || b === undefined) continue;
      
      totalPixels++;
      
      // Check for skin color
      if (isSkinColor(r, g, b)) {
        skinPixels++;
      }
      
      // Check for electronic device characteristics
      if (isElectronicDevice(r, g, b)) {
        devicePixels++;
      }
      
      // Check for screen glow (bright white/blue light typical of screens)
      if (isScreenGlow(r, g, b)) {
        glowPixels++;
      }
      
      // Check for sharp edges (device boundaries)
      if (isSharpEdge(r, g, b, data, i, width)) {
        edgePixels++;
      }
      
      // Check for rectangular patterns (device shapes)
      if (isRectangularPattern(r, g, b, data, i, width, height)) {
        rectangularPixels++;
      }
      
      // NEW: Check for reflective surfaces (glass, screens, phone backs)
      if (isReflectiveSurface(r, g, b)) {
        reflectivePixels++;
      }
      
      // NEW: Check for uniform color regions (device bodies)
      if (isUniformRegion(r, g, b, data, i, width)) {
        uniformRegionPixels++;
      }
      
      // NEW: Check for sharp corners (device corners are 90-degree angles)
      if (isCornerPixel(r, g, b, data, i, width, height)) {
        cornerPixels++;
      }
      
      // NEW: Check for high contrast (screens have very high contrast text/images)
      if (isHighContrast(r, g, b, data, i, width)) {
        highContrastPixels++;
      }
      
      // Check brightness
      const brightness = (r + g + b) / 3;
      avgBrightness += brightness;
      if (brightness > 180) brightPixels++;
      if (brightness < 60) darkPixels++;
    }
    
    // Calculate metrics
    avgBrightness = avgBrightness / totalPixels;
    const skinPercentage = totalPixels > 0 ? (skinPixels / totalPixels) * 100 : 0;
    const brightPercentage = totalPixels > 0 ? (brightPixels / totalPixels) * 100 : 0;
    const darkPercentage = totalPixels > 0 ? (darkPixels / totalPixels) * 100 : 0;
    const devicePercentage = totalPixels > 0 ? (devicePixels / totalPixels) * 100 : 0;
    const glowPercentage = totalPixels > 0 ? (glowPixels / totalPixels) * 100 : 0;
    const edgePercentage = totalPixels > 0 ? (edgePixels / totalPixels) * 100 : 0;
    const rectangularPercentage = totalPixels > 0 ? (rectangularPixels / totalPixels) * 100 : 0;
    const reflectivePercentage = totalPixels > 0 ? (reflectivePixels / totalPixels) * 100 : 0;
    const uniformPercentage = totalPixels > 0 ? (uniformRegionPixels / totalPixels) * 100 : 0;
    const cornerPercentage = totalPixels > 0 ? (cornerPixels / totalPixels) * 100 : 0;
    const highContrastPercentage = totalPixels > 0 ? (highContrastPixels / totalPixels) * 100 : 0;
    
    console.log(`📊 Analysis: Pixels: ${totalPixels}, Skin: ${skinPercentage.toFixed(1)}%, Device: ${devicePercentage.toFixed(1)}%, Glow: ${glowPercentage.toFixed(1)}%, Edge: ${edgePercentage.toFixed(1)}%, Rect: ${rectangularPercentage.toFixed(1)}%, Reflective: ${reflectivePercentage.toFixed(1)}%, Uniform: ${uniformPercentage.toFixed(1)}%, Corner: ${cornerPercentage.toFixed(1)}%, HighContrast: ${highContrastPercentage.toFixed(1)}%, Bright: ${brightPercentage.toFixed(1)}%, Dark: ${darkPercentage.toFixed(1)}%, AvgBright: ${avgBrightness.toFixed(1)}, RectDevices: ${rectangularDevices.count}`);
    
    console.log(`🔍 RAW PIXEL COUNTS:`);
    console.log(`  - Total pixels analyzed: ${totalPixels}`);
    console.log(`  - Device color pixels: ${devicePixels} (${devicePercentage.toFixed(2)}%)`);
    console.log(`  - Glow pixels: ${glowPixels} (${glowPercentage.toFixed(2)}%)`);
    console.log(`  - Edge pixels: ${edgePixels} (${edgePercentage.toFixed(2)}%)`);
    console.log(`  - Rectangular pixels: ${rectangularPixels} (${rectangularPercentage.toFixed(2)}%)`);
    console.log(`  - Reflective pixels: ${reflectivePixels} (${reflectivePercentage.toFixed(2)}%)`);
    console.log(`  - Uniform pixels: ${uniformRegionPixels} (${uniformPercentage.toFixed(2)}%)`);
    console.log(`  - Corner pixels: ${cornerPixels} (${cornerPercentage.toFixed(2)}%)`);
    console.log(`  - High contrast pixels: ${highContrastPixels} (${highContrastPercentage.toFixed(2)}%)`);
    
    // Additional checks for better accuracy
    const isVeryBright = brightPercentage > 70;
    const isVeryDark = darkPercentage > 60;
    const hasReasonableSkin = skinPercentage > 0.5 && skinPercentage < 60;
    
    // AGGRESSIVE: Device detected if ANY threshold is met (using constants defined above)
    const hasElectronicDevice = 
      rectangularDevices.count > 0 || 
      devicePercentage > DEVICE_COLOR_THRESHOLD || 
      glowPercentage > GLOW_THRESHOLD || 
      (edgePercentage > EDGE_THRESHOLD && rectangularPercentage > RECTANGULAR_THRESHOLD) || 
      reflectivePercentage > REFLECTIVE_THRESHOLD || 
      uniformPercentage > UNIFORM_THRESHOLD ||
      cornerPercentage > CORNER_THRESHOLD ||
      highContrastPercentage > HIGH_CONTRAST_THRESHOLD ||
      // FALLBACK: Simple checks - ANY significant device indicator
      (devicePercentage > 0.05 && edgePercentage > 0.3) || // Device color + edges
      (glowPercentage > 0.05 && brightPercentage > 15) || // Screen glow + brightness
      (cornerPercentage > 0.05 && rectangularPercentage > 0.3) || // Corners + rectangles
      (uniformPercentage > 0.3 && edgePercentage > 0.3); // Uniform regions + edges
    
    // DEBUG: Log detailed device detection breakdown with new methods
    console.log(`🔍 Device Detection Breakdown (AGGRESSIVE THRESHOLDS):`);
    console.log(`  - rectangularDevices.count: ${rectangularDevices.count} ${rectangularDevices.count > 0 ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - devicePercentage: ${devicePercentage.toFixed(1)}% (threshold: ${DEVICE_COLOR_THRESHOLD}%) ${devicePercentage > DEVICE_COLOR_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - glowPercentage: ${glowPercentage.toFixed(1)}% (threshold: ${GLOW_THRESHOLD}%) ${glowPercentage > GLOW_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - edgePercentage: ${edgePercentage.toFixed(1)}% + rectangularPercentage: ${rectangularPercentage.toFixed(1)}% (thresholds: ${EDGE_THRESHOLD}% + ${RECTANGULAR_THRESHOLD}%) ${(edgePercentage > EDGE_THRESHOLD && rectangularPercentage > RECTANGULAR_THRESHOLD) ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - reflectivePercentage: ${reflectivePercentage.toFixed(1)}% (threshold: ${REFLECTIVE_THRESHOLD}%) ${reflectivePercentage > REFLECTIVE_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - uniformPercentage: ${uniformPercentage.toFixed(1)}% (threshold: ${UNIFORM_THRESHOLD}%) ${uniformPercentage > UNIFORM_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - cornerPercentage: ${cornerPercentage.toFixed(1)}% (threshold: ${CORNER_THRESHOLD}%) ${cornerPercentage > CORNER_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - highContrastPercentage: ${highContrastPercentage.toFixed(1)}% (threshold: ${HIGH_CONTRAST_THRESHOLD}%) ${highContrastPercentage > HIGH_CONTRAST_THRESHOLD ? '✅ DEVICE!' : '❌'}`);
    console.log(`  - FINAL hasElectronicDevice: ${hasElectronicDevice ? '🚨 YES - DEVICE DETECTED!' : '❌ NO'}`);
    
    // Log device detection details
    if (hasElectronicDevice) {
      console.log(`🔍 DEVICE DETECTED: RectDevices: ${rectangularDevices.count}, Device: ${devicePercentage.toFixed(1)}%, Glow: ${glowPercentage.toFixed(1)}%, Edge: ${edgePercentage.toFixed(1)}%, Rect: ${rectangularPercentage.toFixed(1)}%`);
      if (rectangularDevices.count > 0) {
        console.log(`📱 RECTANGULAR DEVICE FOUND: Size: ${rectangularDevices.largestArea}px, Confidence: ${rectangularDevices.confidence.toFixed(2)}`);
      }
    }
    
    // Determine face count based on analysis
    let faceCount = 0;
    let confidence = 0;
    
    // CRITICAL FIX: If rectangular device detected, prioritize device detection over face detection
    // This prevents devices from being misidentified as multiple people
    if (rectangularDevices.count > 0) {
      console.log(`🚨 RECTANGULAR DEVICE TAKES PRIORITY: Ignoring face count, device detected`);
      // Still detect if there's a person present, but don't count device as extra person
      if (skinPercentage >= 1 && skinPercentage < 50) {
        faceCount = 1; // One person holding the device
        confidence = Math.min(0.85, Math.max(0.5, (skinPercentage - 1) / 49));
      } else {
        faceCount = 0; // Just device, no person visible
        confidence = 0;
      }
    }
    // Fixed face detection logic - more conservative to prevent false positives
    else if (isVeryDark && skinPercentage < 1) {
      // Very dark image, likely no person or camera covered
      faceCount = 0;
      confidence = 0;
    } else if (isVeryBright && skinPercentage < 2) {
      // Overexposed image, likely no person visible
      faceCount = 0;
      confidence = 0;
    } else if (skinPercentage >= 1 && skinPercentage < 45) {
      // Single person detected - increased threshold to prevent false positives
      // A single person can easily have 30-40% skin pixels when close to camera
      faceCount = 1;
      confidence = Math.min(0.85, Math.max(0.5, (skinPercentage - 1) / 44));
    } else if (skinPercentage >= 45 && skinPercentage < 75) {
      // Two people detected - only when there's significant skin coverage
      faceCount = 2;
      confidence = Math.min(0.9, Math.max(0.6, (skinPercentage - 45) / 30));
    } else if (skinPercentage >= 75) {
      // Multiple people (3+) or very close faces - very high threshold
      faceCount = Math.min(4, 3 + Math.floor((skinPercentage - 75) / 10));
      confidence = 0.7;
    } else {
      // No significant skin detected
      faceCount = 0;
      confidence = 0;
    }
    
    console.log(`🎯 Face Detection Result: ${faceCount} face(s), confidence: ${(confidence * 100).toFixed(1)}%, skin: ${skinPercentage.toFixed(1)}%`);
    
    return {
      faceCount: Math.min(faceCount, 3), // Cap at 3 faces max
      confidence,
      skinPercentage,
      brightPercentage,
      darkPercentage,
      avgBrightness,
      totalPixels,
      devicePercentage,
      glowPercentage,
      edgePercentage,
      rectangularPercentage,
      reflectivePercentage,
      uniformPercentage,
      cornerPercentage,
      highContrastPercentage,
      hasElectronicDevice
    };
  };

  const isSkinColor = (r, g, b) => {
    // Balanced skin tone detection - not too conservative to properly detect multiple people
    
    // Primary condition: Standard RGB-based skin detection
    const condition1 = (r > 95 && r < 230) && (g > 40 && g < 200) && (b > 20 && b < 180) &&
                      (Math.max(r, g, b) - Math.min(r, g, b) > 15) &&
                      (Math.abs(r - g) > 15) && (r > g && r > b);
    
    // Secondary condition: YCbCr color space (most accurate for skin detection)
    const y = 0.299 * r + 0.587 * g + 0.114 * b;
    const cb = -0.169 * r - 0.331 * g + 0.5 * b + 128;
    const cr = 0.5 * r - 0.419 * g - 0.081 * b + 128;
    const condition2 = (cb >= 77 && cb <= 127) && (cr >= 133 && cr <= 173);
    
    // Tertiary condition: HSV-based detection with relaxed bounds for better detection
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const diff = max - min;
    let h = 0;
    if (diff !== 0) {
      if (max === r) h = ((g - b) / diff) % 6;
      else if (max === g) h = (b - r) / diff + 2;
      else h = (r - g) / diff + 4;
    }
    h = h * 60;
    if (h < 0) h += 360;
    
    const s = max === 0 ? 0 : diff / max;
    const v = max / 255;
    
    const condition3 = (h >= 0 && h <= 50) && (s >= 0.25) && (v >= 0.35);
    
    // More balanced approach - at least 1 strong condition OR 2 weaker conditions
    const conditionCount = (condition1 ? 1 : 0) + (condition2 ? 1 : 0) + (condition3 ? 1 : 0);
    
    // If YCbCr (most reliable) is true, that's enough
    if (condition2) return true;
    
    // Otherwise, need at least 1 other condition
    return conditionCount >= 1;
  };

  // Aggressive electronic device detection - detects all common devices
  const isElectronicDevice = (r, g, b) => {
    // More aggressive device detection - catch devices early
    
    // Black devices - phones/tablets with black bezels (expanded)
    const isBlackDevice = (r < 60 && g < 60 && b < 60) && (Math.abs(r - g) < 20 && Math.abs(g - b) < 20);
    
    // Dark gray devices - space gray devices, dark laptops (expanded)
    const isDarkGray = (r >= 30 && r <= 130) && (g >= 30 && g <= 130) && (b >= 30 && b <= 130) && 
                       (Math.abs(r - g) < 30 && Math.abs(g - b) < 30);
    
    // White devices - white phones/tablets (expanded)
    const isWhiteDevice = (r > 180 && g > 180 && b > 180) && (Math.abs(r - g) < 35 && Math.abs(g - b) < 35);
    
    // Silver/metallic devices - MacBooks, silver phones (expanded)
    const isSilver = (r >= 100 && r <= 240) && (g >= 100 && g <= 240) && (b >= 100 && b <= 240) &&
                     (Math.abs(r - g) < 35 && Math.abs(g - b) < 35);
    
    // Gold/rose gold devices - newer iPhones, iPads (expanded)
    const isGold = (r >= 160 && r <= 255) && (g >= 130 && g <= 240) && (b >= 100 && b <= 210) &&
                   (r >= g && g >= b) && (r - b > 20);
    
    // Blue devices - some Android phones (expanded)
    const isBlueDevice = (b > r + 20 && b > g + 20) && (b >= 70 && b <= 210) && 
                        (r < 140 && g < 140);
    
    // Red devices - red phones, cases (expanded)
    const isRedDevice = (r > g + 25 && r > b + 25) && (r >= 120 && r <= 240) && 
                       (g < 130 && b < 130);
    
    // Very dark devices - almost black
    const isVeryDark = (r < 35 && g < 35 && b < 35);
    
    // Matte surfaces - device backs/lids
    const isMatte = (r >= 70 && r <= 190) && (g >= 70 && g <= 190) && (b >= 70 && b <= 190) &&
                   (Math.abs(r - g) < 35 && Math.abs(g - b) < 35);
    
    return isBlackDevice || isDarkGray || isWhiteDevice || isSilver || isGold || 
           isBlueDevice || isRedDevice || isVeryDark || isMatte;
  };

  // Aggressive screen glow detection - detects all screen activity
  const isScreenGlow = (r, g, b) => {
    // More aggressive screen detection - catch active screens early
    
    // Bright screen glow - active phone/laptop screens (lowered threshold)
    const isBrightScreen = (r > 180 || g > 180 || b > 180) && (r + g + b > 540);
    
    // Blue glow from screens - LCD/OLED displays (more sensitive)
    const isBlueGlow = (b > r + 25 && b > g + 25) && (b > 150) && (b - Math.max(r, g) > 35);
    
    // White/bright glow - bright screens (lowered threshold)
    const isWhiteGlow = (r > 180 && g > 180 && b > 180) && (Math.abs(r - g) < 40 && Math.abs(g - b) < 40);
    
    // Green screen glow - Android screens, some apps (more sensitive)
    const isGreenGlow = (g > r + 25 && g > b + 25) && (g > 150) && (g - Math.max(r, b) > 35);
    
    // Red screen glow - some apps, notifications
    const isRedGlow = (r > g + 25 && r > b + 25) && (r > 150) && (r - Math.max(g, b) > 35);
    
    // Notification LEDs (expanded)
    const isNotificationLight = ((r > 170 && g < 130 && b < 130) || // Red LED
                                (g > 170 && r < 130 && b < 130) || // Green LED
                                (b > 170 && r < 130 && g < 130) || // Blue LED
                                (r > 150 && g > 150 && b < 120)); // Yellow LED
    
    // Screen reflection patterns
    const isScreenReflection = (r > 140 && g > 140 && b > 140) && 
                              (Math.abs(r - g) < 45 && Math.abs(g - b) < 45) &&
                              (Math.max(r, g, b) > 180);
    
    // Dim screen glow - low brightness screens
    const isDimGlow = (r > 110 || g > 110 || b > 110) && (r + g + b > 380);
    
    return isBrightScreen || isBlueGlow || isWhiteGlow || isGreenGlow || isRedGlow ||
           isNotificationLight || isScreenReflection || isDimGlow;
  };

  // Detect sharp edges that might indicate device boundaries
  const isSharpEdge = (r, g, b, data, currentIndex, width) => {
    try {
      // Simple edge detection - check contrast with neighboring pixels
      const pixelsPerRow = width * 4; // 4 bytes per pixel (RGBA)
      
      // Get neighboring pixel indices (if they exist)
      const rightIndex = currentIndex + 4;
      const bottomIndex = currentIndex + pixelsPerRow;
      
      // Check if indices are valid
      if (rightIndex >= data.length || bottomIndex >= data.length) return false;
      
      // Get neighboring pixel values
      const rightR = data[rightIndex];
      const rightG = data[rightIndex + 1];
      const rightB = data[rightIndex + 2];
      
      const bottomR = data[bottomIndex];
      const bottomG = data[bottomIndex + 1];
      const bottomB = data[bottomIndex + 2];
      
      // Calculate brightness differences
      const currentBrightness = (r + g + b) / 3;
      const rightBrightness = (rightR + rightG + rightB) / 3;
      const bottomBrightness = (bottomR + bottomG + bottomB) / 3;
      
      // Check for sharp contrast (device edges) - more sensitive
      const rightContrast = Math.abs(currentBrightness - rightBrightness);
      const bottomContrast = Math.abs(currentBrightness - bottomBrightness);
      
      // Lower contrast threshold to detect device edges better
      return rightContrast > 65 || bottomContrast > 65;
    } catch (e) {
      return false;
    }
  };

  // Detect rectangular patterns that might indicate devices
  const isRectangularPattern = (r, g, b, data, currentIndex, width, height) => {
    try {
      // Look for consistent color patterns in a small rectangular area
      const pixelsPerRow = width * 4;
      const checkRadius = 2; // Check 2 pixels in each direction
      
      let similarPixels = 0;
      let totalChecked = 0;
      
      // Check a small rectangular area around the current pixel
      for (let dy = -checkRadius; dy <= checkRadius; dy++) {
        for (let dx = -checkRadius; dx <= checkRadius; dx++) {
          const checkIndex = currentIndex + (dy * pixelsPerRow) + (dx * 4);
          
          // Make sure we're within bounds
          if (checkIndex >= 0 && checkIndex < data.length - 2) {
            const checkR = data[checkIndex];
            const checkG = data[checkIndex + 1];
            const checkB = data[checkIndex + 2];
            
            // Check if this pixel is similar to the center pixel (device-like consistency)
            const colorDiff = Math.abs(r - checkR) + Math.abs(g - checkG) + Math.abs(b - checkB);
            
            if (colorDiff < 55) { // More lenient similarity
              similarPixels++;
            }
            totalChecked++;
          }
        }
      }
      
      // If most pixels in the area are similar, it might be a device surface
      const similarity = totalChecked > 0 ? (similarPixels / totalChecked) : 0;
      return similarity > 0.75; // 75% similarity threshold (more sensitive)
      
    } catch (e) {
      return false;
    }
  };

  // NEW: Detect reflective surfaces (glass screens, phone backs)
  const isReflectiveSurface = (r, g, b) => {
    // Reflective surfaces have:
    // 1. High brightness with specular highlights (very bright spots)
    // 2. High saturation in highlights (colorful reflections)
    // 3. Sharp brightness gradients
    
    const brightness = (r + g + b) / 3;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const saturation = max === 0 ? 0 : ((max - min) / max) * 100;
    
    // Detect bright specular highlights (typical of glass reflections)
    const isSpecularHighlight = brightness > 220 && saturation < 20; // Very bright + low saturation = white reflection
    
    // Detect colorful reflections (ambient light reflecting off glass)
    const isColorfulReflection = brightness > 180 && saturation > 30; // Bright + high saturation = colored reflection
    
    // Detect semi-gloss surfaces (matte phone backs)
    const isSemiGloss = brightness > 150 && brightness < 200 && saturation < 25;
    
    return isSpecularHighlight || isColorfulReflection || isSemiGloss;
  };

  // NEW: Detect uniform color regions (large consistent color blocks typical of device bodies)
  const isUniformRegion = (r, g, b, data, currentIndex, width) => {
    try {
      // Devices have large uniform color areas (phone backs, tablet screens when off)
      const pixelsPerRow = width * 4;
      const checkSize = 4; // Check larger area (4 pixels = roughly 1cm on typical device)
      
      let uniformPixels = 0;
      let totalChecked = 0;
      
      // Check a horizontal and vertical line from current pixel
      for (let offset = 1; offset <= checkSize; offset++) {
        // Check right
        const rightIndex = currentIndex + (offset * 4);
        if (rightIndex < data.length - 2) {
          const rDiff = Math.abs(r - data[rightIndex]);
          const gDiff = Math.abs(g - data[rightIndex + 1]);
          const bDiff = Math.abs(b - data[rightIndex + 2]);
          totalChecked++;
          if (rDiff < 20 && gDiff < 20 && bDiff < 20) uniformPixels++; // Very tight tolerance
        }
        
        // Check down
        const downIndex = currentIndex + (offset * pixelsPerRow);
        if (downIndex < data.length - 2) {
          const rDiff = Math.abs(r - data[downIndex]);
          const gDiff = Math.abs(g - data[downIndex + 1]);
          const bDiff = Math.abs(b - data[downIndex + 2]);
          totalChecked++;
          if (rDiff < 20 && gDiff < 20 && bDiff < 20) uniformPixels++; // Very tight tolerance
        }
      }
      
      // If > 75% of checked pixels are uniform, this is likely a device surface
      return totalChecked > 0 && (uniformPixels / totalChecked) > 0.75;
    } catch (e) {
      return false;
    }
  };

  // NEW: Detect sharp corners (90-degree angles typical of device corners)
  const isCornerPixel = (r, g, b, data, currentIndex, width, height) => {
    try {
      const pixelsPerRow = width * 4;
      
      // Get pixels in a + pattern (up, down, left, right)
      const upIndex = currentIndex - pixelsPerRow;
      const downIndex = currentIndex + pixelsPerRow;
      const leftIndex = currentIndex - 4;
      const rightIndex = currentIndex + 4;
      
      // Check bounds
      if (upIndex < 0 || downIndex >= data.length || leftIndex < 0 || rightIndex >= data.length - 2) {
        return false;
      }
      
      const currentBrightness = (r + g + b) / 3;
      const upBrightness = (data[upIndex] + data[upIndex + 1] + data[upIndex + 2]) / 3;
      const downBrightness = (data[downIndex] + data[downIndex + 1] + data[downIndex + 2]) / 3;
      const leftBrightness = (data[leftIndex] + data[leftIndex + 1] + data[leftIndex + 2]) / 3;
      const rightBrightness = (data[rightIndex] + data[rightIndex + 1] + data[rightIndex + 2]) / 3;
      
      // Corner detection: high contrast in two perpendicular directions
      const verticalContrast = Math.abs(upBrightness - downBrightness);
      const horizontalContrast = Math.abs(leftBrightness - rightBrightness);
      
      // Device corners have VERY high contrast in both directions (> 80)
      return verticalContrast > 80 && horizontalContrast > 80;
    } catch (e) {
      return false;
    }
  };

  // NEW: Detect high contrast areas (screens display high contrast text/images)
  const isHighContrast = (r, g, b, data, currentIndex, width) => {
    try {
      const pixelsPerRow = width * 4;
      const currentBrightness = (r + g + b) / 3;
      
      // Check 8 surrounding pixels for very high contrast
      const offsets = [
        -pixelsPerRow - 4, -pixelsPerRow, -pixelsPerRow + 4,  // top row
        -4, 4,                                                  // left, right
        pixelsPerRow - 4, pixelsPerRow, pixelsPerRow + 4       // bottom row
      ];
      
      let maxContrast = 0;
      for (const offset of offsets) {
        const checkIndex = currentIndex + offset;
        if (checkIndex >= 0 && checkIndex < data.length - 2) {
          const checkBrightness = (data[checkIndex] + data[checkIndex + 1] + data[checkIndex + 2]) / 3;
          const contrast = Math.abs(currentBrightness - checkBrightness);
          if (contrast > maxContrast) maxContrast = contrast;
        }
      }
      
      // Screens often have contrast > 120 (black text on white background, etc.)
      return maxContrast > 120;
    } catch (e) {
      return false;
    }
  };

  const checkViolations = (status) => {
    const now = Date.now();
    
    // Grace period check - no violations for first 10 seconds
    if (now - detectionStartTime < GRACE_PERIOD) {
      console.log('🕒 Grace period active, no violations yet');
      return;
    }
    
    // Cooldown check
    if (now - lastViolationTime < VIOLATION_COOLDOWN) {
      return;
    }
    
    let violationMessage = null;
    
    // STRICT MULTIPLE PERSON DETECTION - REQUIRES CONSECUTIVE DETECTIONS
    // Multiple people detected = terminate after consecutive detections to prevent false positives
    if (status.facesCount > 1 && status.confidence > 0.65) {
      const newMultipleFaceCount = consecutiveMultipleFaceCount + 1;
      setConsecutiveMultipleFaceCount(newMultipleFaceCount);
      
      console.log(`👥 Multiple faces detected ${newMultipleFaceCount}/${MULTIPLE_FACE_THRESHOLD} times (${status.facesCount} faces, ${(status.confidence * 100).toFixed(1)}% confidence)`);
      
      if (newMultipleFaceCount >= MULTIPLE_FACE_THRESHOLD) {
        violationMessage = `INTERVIEW TERMINATED: Multiple people detected consistently (${status.facesCount} people). Only the candidate should be visible during the interview.`;
        console.log('🚨 CRITICAL VIOLATION: Multiple people detected consistently - terminating interview');
        
        // Reset counter and trigger violation
        setConsecutiveMultipleFaceCount(0);
        setLastViolationTime(now);
        setConsecutiveNoFaceCount(0);
        onViolation(violationMessage, true); // Pass true to indicate this should end the interview
        return; // Exit immediately
      }
    } else {
      // Reset multiple face counter if single person or no person detected
      setConsecutiveMultipleFaceCount(0);
    }
    
    // ELECTRONIC DEVICE DETECTION - REQUIRES CONSECUTIVE DETECTIONS
    // Electronic devices detected = terminate after multiple consecutive detections
    if (status.hasElectronicDevice) {
      const newDeviceCount = consecutiveDeviceCount + 1;
      setConsecutiveDeviceCount(newDeviceCount);
      
      console.log(`📱 Device detected ${newDeviceCount}/${DEVICE_DETECTION_THRESHOLD} times (Device: ${status.devicePercentage?.toFixed(1)}%, Screen: ${status.glowPercentage?.toFixed(1)}%, Edge: ${status.edgePercentage?.toFixed(1)}%, Rect: ${status.rectangularPercentage?.toFixed(1)}%, Refl: ${status.reflectivePercentage?.toFixed(1)}%, Unif: ${status.uniformPercentage?.toFixed(1)}%)`);
      
      if (newDeviceCount >= DEVICE_DETECTION_THRESHOLD) {
        violationMessage = `INTERVIEW TERMINATED: Electronic device detected (Device: ${status.devicePercentage?.toFixed(1)}%, Screen: ${status.glowPercentage?.toFixed(1)}%, Edge: ${status.edgePercentage?.toFixed(1)}%, Rect: ${status.rectangularPercentage?.toFixed(1)}%, Refl: ${status.reflectivePercentage?.toFixed(1)}%, Unif: ${status.uniformPercentage?.toFixed(1)}%). Use of phones, tablets, or other electronic devices is prohibited.`;
        console.log('🚨 CRITICAL VIOLATION: Electronic device detected multiple times - terminating interview');
        
        // Reset counter and trigger violation
        setConsecutiveDeviceCount(0);
        setLastViolationTime(now);
        setConsecutiveNoFaceCount(0);
        onViolation(violationMessage, true); // Pass true to indicate this should end the interview
        return; // Exit immediately
      }
    } else {
      // Reset device counter if no device detected
      setConsecutiveDeviceCount(0);
    }
    
    if (status.facesCount <= 1 && !status.hasElectronicDevice) {
      console.log(`✅ No violation: ${status.facesCount} face(s) detected, no devices detected`);
    }
    
    // Reset no-face counter (we don't penalize for no face anymore)
    setConsecutiveNoFaceCount(0);
  };

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}>
      {/* Canvas for processing - ALWAYS VISIBLE FOR DEBUGGING */}
      <canvas
        ref={canvasRef}
        style={{ 
          display: 'block', // ALWAYS SHOW for debugging
          position: 'absolute',
          top: 0,
          left: 0,
          width: '160px',
          height: '120px',
          border: '2px solid red',
          zIndex: 1000,
          background: 'black'
        }}
      />
      
      {/* Enhanced status display for development and testing */}
      <div style={{
        position: 'absolute',
        top: 130,
        left: 0,
        background: 'rgba(0,0,0,0.9)',
        color: 'white',
        padding: '8px',
        fontSize: '11px',
        borderRadius: '4px',
        zIndex: 1001,
        maxWidth: '250px',
        lineHeight: '1.3'
      }}>
        <div style={{color: faceStatus.facesCount === 1 ? '#4CAF50' : faceStatus.facesCount === 0 ? '#FFC107' : '#F44336'}}>
          <strong>👥 Faces: {faceStatus.facesCount} | Conf: {Math.round(faceStatus.confidence * 100)}%</strong>
        </div>
        <div style={{color: '#00BCD4'}}>
          <strong>🎯 Skin: {faceStatus.skinPercentage ? faceStatus.skinPercentage.toFixed(1) : '0.0'}%</strong>
        </div>
        <div style={{color: faceStatus.hasElectronicDevice ? '#F44336' : '#4CAF50'}}>
          <strong>📱 Dev: {faceStatus.devicePercentage ? faceStatus.devicePercentage.toFixed(1) : '0.0'}% | Scr: {faceStatus.glowPercentage ? faceStatus.glowPercentage.toFixed(1) : '0.0'}%</strong>
        </div>
        <div style={{color: faceStatus.hasElectronicDevice ? '#F44336' : '#4CAF50'}}>
          <strong>🔲 Edge: {faceStatus.edgePercentage ? faceStatus.edgePercentage.toFixed(1) : '0.0'}% | Rect: {faceStatus.rectangularPercentage ? faceStatus.rectangularPercentage.toFixed(1) : '0.0'}%</strong>
        </div>
        <div style={{color: faceStatus.hasElectronicDevice ? '#F44336' : '#4CAF50'}}>
          <strong>✨ Refl: {faceStatus.reflectivePercentage ? faceStatus.reflectivePercentage.toFixed(1) : '0.0'}% | Unif: {faceStatus.uniformPercentage ? faceStatus.uniformPercentage.toFixed(1) : '0.0'}%</strong>
        </div>
        <div style={{color: faceStatus.hasElectronicDevice ? '#F44336' : '#4CAF50'}}>
          <strong>🔺 Corner: {faceStatus.cornerPercentage ? faceStatus.cornerPercentage.toFixed(1) : '0.0'}% | Contrast: {faceStatus.highContrastPercentage ? faceStatus.highContrastPercentage.toFixed(1) : '0.0'}%</strong>
        </div>
        <div style={{color: faceStatus.hasElectronicDevice ? '#FF0000' : '#4CAF50', fontWeight: 'bold', fontSize: '12px', marginTop: '4px', padding: '4px', background: faceStatus.hasElectronicDevice ? 'rgba(255,0,0,0.2)' : 'rgba(76,175,80,0.2)', borderRadius: '3px'}}>
          {faceStatus.hasElectronicDevice ? '🚨 DEVICE DETECTED!' : '✅ No Device'}
        </div>
        <div>🎯 Active: {isActive ? 'YES' : 'NO'}</div>
        <div>⏰ Last: {faceStatus.lastDetection ? new Date(faceStatus.lastDetection).toLocaleTimeString() : 'Never'}</div>
        {faceStatus.imageDataSize && <div>📊 Data: {(faceStatus.imageDataSize / 1000).toFixed(0)}KB</div>}
        <div style={{fontSize: '10px', marginTop: '4px', opacity: 0.8}}>
          🔧 Detection every {DETECTION_INTERVAL/1000}s
        </div>
      </div>
    </div>
  );
};

export default SimpleFaceDetection;
