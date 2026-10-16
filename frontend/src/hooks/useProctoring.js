import { useEffect, useRef, useState } from 'react'
import { FaceDetector, FilesetResolver } from '@mediapipe/tasks-vision'

// On-device face proctoring with 3-strike rule.
// Violations: multiple faces, no face for N frames, sudden movement (IoU drop).
export function useProctoring({
  enabled,
  noFaceFramesThreshold = 45,
  movementIouThreshold = 0.35,
  maxStrikes = 3,
  sessionId = null,
  onStrike,        // (reason, strikes) => void
  onMaxStrikes,    // () => void
} = {}) {
  const [status, setStatus] = useState({ faceCount: 0, strikes: 0, reason: null })
  const videoRef = useRef(null)
  const detectorRef = useRef(null)
  const runningRef = useRef(false)
  const lastBoxRef = useRef(null)
  const noFaceFramesRef = useRef(0)
  const strikesRef = useRef(0)

  useEffect(() => {
    if (!enabled) return
    let stream

    async function init() {
      runningRef.current = true
      const vision = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      )
      const detector = await FaceDetector.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            'https://storage.googleapis.com/mediapipe-models/face_detector/short_range/float16/1/face_detector_short_range.tflite',
        },
        runningMode: 'VIDEO',
      })
      detectorRef.current = detector

      stream = await navigator.mediaDevices.getUserMedia({ video: true })
      const v = document.createElement('video')
      v.srcObject = stream
      v.autoplay = true
      v.muted = true
      v.playsInline = true
      videoRef.current = v

      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      function iou(a, b) {
        const x1 = Math.max(a.x, b.x)
        const y1 = Math.max(a.y, b.y)
        const x2 = Math.min(a.x + a.w, b.x + b.w)
        const y2 = Math.min(a.y + a.h, b.y + b.h)
        const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1)
        const union = a.w * a.h + b.w * b.h - inter || 1
        return inter / union
      }

      const tick = async () => {
        if (!runningRef.current) return
        if (v.readyState >= 2) {
          canvas.width = v.videoWidth
          canvas.height = v.videoHeight
          ctx.drawImage(v, 0, 0)
          const result = await detector.detectForVideo(v, performance.now())
          const faces = result.detections || []
          const fc = faces.length

          let reason = null
          if (fc === 0) {
            noFaceFramesRef.current++
            if (noFaceFramesRef.current >= noFaceFramesThreshold) {
              reason = 'no_face_detected'
            }
          } else {
            noFaceFramesRef.current = 0
            if (fc > 1) {
              reason = 'multiple_faces'
            } else {
              // sudden movement
              const bb = faces[0].boundingBox
              const cur = { x: bb.originX, y: bb.originY, w: bb.width, h: bb.height }
              if (lastBoxRef.current) {
                const overlap = iou(lastBoxRef.current, cur)
                if (overlap < movementIouThreshold) {
                  reason = 'sudden_movement'
                }
              }
              lastBoxRef.current = cur
            }
          }

          if (reason) {
            strikesRef.current++
            const strikes = strikesRef.current
            setStatus({ faceCount: fc, strikes, reason })
            onStrike?.(reason, strikes)
            try {
              await fetch('/api/proctor/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ event: 'proctor_violation', reason, strikes, session_id: sessionId || undefined })
              })
            } catch {}
            if (strikes >= maxStrikes) {
              onMaxStrikes?.()
              runningRef.current = false
              stream.getTracks().forEach(t => t.stop())
              return
            }
          } else {
            setStatus({ faceCount: fc, strikes: strikesRef.current, reason: null })
          }
        }
        requestAnimationFrame(tick)
      }
      requestAnimationFrame(tick)
    }

    init()
    return () => {
      runningRef.current = false
      try { detectorRef.current?.close?.() } catch {}
      try { videoRef.current?.srcObject?.getTracks?.().forEach(t => t.stop()) } catch {}
    }
  }, [enabled, noFaceFramesThreshold, movementIouThreshold, maxStrikes, sessionId, onStrike, onMaxStrikes])

  return { status }
}
