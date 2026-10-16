import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import NavBar from '../components/NavBar.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import SimpleFaceDetection from '../components/SimpleFaceDetection.jsx'
import '../styles.css'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

// Map UI categories to backend role hints discovered from datasets
const ROLE_MAP = {
	technical: 'software engineer',
	behavioral: 'general',
	hr: 'hr specialist',
	communication: 'general',
	case: 'product manager',
	fullstack: 'fullstack developer',
	datascience: 'data science',
}

function useQuery() { const { search } = useLocation(); return useMemo(() => new URLSearchParams(search), [search]) }

export default function InterviewRun(){
	const q = useQuery();
	const navigate = useNavigate();
	const category = q.get('category') || 'technical'
	const roleHint = ROLE_MAP[category] || category

	const [skills, setSkills] = useState('')
	const [questions, setQuestions] = useState([])
	const [idx, setIdx] = useState(0)
	const [answers, setAnswers] = useState([])
	const [timer, setTimer] = useState(90)
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState('')
	const [cameraStatus, setCameraStatus] = useState('requesting') // 'requesting', 'active', 'error', 'denied'
	const [sttSupported, setSttSupported] = useState(false)
	const [listening, setListening] = useState(false)
	const [autoSpeak, setAutoSpeak] = useState(true)
	const [showRules, setShowRules] = useState(true)
	const [tabWarning, setTabWarning] = useState('')
	const [violationCount, setViolationCount] = useState(0)
	const [showLeaveConfirm, setShowLeaveConfirm] = useState(false)
	const [faceStatus, setFaceStatus] = useState({ facesCount: 0, isLookingAway: false, confidence: 0 })
	const [faceWarning, setFaceWarning] = useState('')

	const recognitionRef = useRef(null)
	const videoRef = useRef(null)
	const mediaRef = useRef(null)
	const timerRef = useRef(null)
	const containerRef = useRef(null)
	const floatRef = useRef(null)
	const interimTextRef = useRef('') // Track interim speech text separately

	// Draggable floating preview position (top-left coords)
	const [floatPos, setFloatPos] = useState({ x: null, y: null })
	const [dragging, setDragging] = useState(false)
	const dragOffsetRef = useRef({ dx: 0, dy: 0 })

	useEffect(() => {
		startCamera()
		initSpeech()
		const onVisibility = () => {
			if (document.hidden && questions.length) {
				recordViolation('You switched tabs or minimized the window during the interview.')
			}
		}
		document.addEventListener('visibilitychange', onVisibility)
		return () => {
			document.removeEventListener('visibilitychange', onVisibility)
			stopCamera()
		}
	}, [])

	// Warn on tab close/refresh and intercept back navigation when interview is active
	useEffect(() => {
		if (!questions.length) return
		const onBeforeUnload = (e) => {
			// Only warn if interview in progress
			e.preventDefault()
			e.returnValue = ''
		}
		const onPopState = (e) => {
			// Block back navigation with a custom modal
			setShowLeaveConfirm(true)
			recordViolation('Attempted to leave the interview.')
			try { history.pushState(null, '', location.href) } catch {}
		}
		const onBlur = () => { recordViolation('Window lost focus during the interview.') }
		try { history.pushState(null, '', location.href) } catch {}
		window.addEventListener('beforeunload', onBeforeUnload)
		window.addEventListener('popstate', onPopState)
		window.addEventListener('blur', onBlur)
		return () => {
			window.removeEventListener('beforeunload', onBeforeUnload)
			window.removeEventListener('popstate', onPopState)
			window.removeEventListener('blur', onBlur)
		}
	}, [questions])

	function recordViolation(msg){
		setViolationCount((c) => {
			const next = c + 1
			const remaining = Math.max(0, 3 - next)
			setTabWarning(`Warning ${next}/3: ${msg} Interview will end after ${remaining} more ${remaining===1?'violation':'violations'}.`)
			if (next >= 3) {
				// Auto-terminate interview
				finish()
			}
			return next
		})
	}

	// Handle face detection violations
	function handleFaceViolation(message, isCritical = false) {
		setFaceWarning(message)
		recordViolation(message)
		
		// If it's a critical violation (multiple people detected), end interview immediately
		if (isCritical || message.includes('INTERVIEW TERMINATED')) {
			console.log('🚨 CRITICAL VIOLATION: Ending interview immediately')
			
			// Show critical warning for 3 seconds then redirect
			setTimeout(() => {
				// Force end the interview and go to results
				handleFinish()
			}, 3000)
			
			return // Don't set auto-clear timer for critical violations
		}
		
		// Auto-clear face warning after 5 seconds for non-critical violations
		setTimeout(() => {
			setFaceWarning('')
		}, 5000)
	}

	// Handle face status updates
	function handleFaceStatus(status) {
		setFaceStatus(status)
	}

	// Ensure video element attaches to existing stream whenever it mounts
	useEffect(() => {
		if (cameraStatus === 'active' && videoRef.current && mediaRef.current) {
			try {
				videoRef.current.srcObject = mediaRef.current
				videoRef.current.play?.()
			} catch {}
		}
	}, [cameraStatus, videoRef.current])

	// Initialize default floating position to bottom-right
	useEffect(() => {
		if (floatPos.x !== null) return
		const setInitial = () => {
			const w = floatRef.current?.offsetWidth || 260
			const h = floatRef.current?.offsetHeight || 160
			const x = Math.max(8, (window.innerWidth - w - 16))
			const y = Math.max(8, (window.innerHeight - h - 16))
			setFloatPos({ x, y })
		}
		// delay until element is measured
		requestAnimationFrame(setInitial)
		window.addEventListener('resize', setInitial)
		return () => window.removeEventListener('resize', setInitial)
	}, [floatPos.x])

	// Drag handlers
	const onDragStart = (clientX, clientY) => {
		if (floatPos.x === null) return
		setDragging(true)
		dragOffsetRef.current = { dx: clientX - floatPos.x, dy: clientY - floatPos.y }
	}
	const onDragMove = (clientX, clientY) => {
		if (!dragging) return
		const w = floatRef.current?.offsetWidth || 260
		const h = floatRef.current?.offsetHeight || 160
		const nx = clientX - dragOffsetRef.current.dx
		const ny = clientY - dragOffsetRef.current.dy
		const maxX = Math.max(8, window.innerWidth - w - 8)
		const maxY = Math.max(8, window.innerHeight - h - 8)
		setFloatPos({
			x: Math.min(Math.max(8, nx), maxX),
			y: Math.min(Math.max(8, ny), maxY),
		})
	}
	const onDragEnd = () => setDragging(false)

	useEffect(() => {
		const onMouseMove = (e) => onDragMove(e.clientX, e.clientY)
		const onMouseUp = () => onDragEnd()
		const onTouchMove = (e) => { if (e.touches && e.touches[0]) onDragMove(e.touches[0].clientX, e.touches[0].clientY) }
		const onTouchEnd = () => onDragEnd()
		if (dragging) {
			window.addEventListener('mousemove', onMouseMove)
			window.addEventListener('mouseup', onMouseUp)
			window.addEventListener('touchmove', onTouchMove, { passive: false })
			window.addEventListener('touchend', onTouchEnd)
		}
		return () => {
			window.removeEventListener('mousemove', onMouseMove)
			window.removeEventListener('mouseup', onMouseUp)
			window.removeEventListener('touchmove', onTouchMove)
			window.removeEventListener('touchend', onTouchEnd)
		}
	}, [dragging])

	// Prevent Picture-in-Picture so the webcam doesn't float as a separate window
	useEffect(() => {
		const v = videoRef.current
		if (!v) return
		const onEnterPip = async () => {
			try { if (document.pictureInPictureElement) await document.exitPictureInPicture() } catch {}
		}
		v.addEventListener('enterpictureinpicture', onEnterPip)
		return () => { v.removeEventListener('enterpictureinpicture', onEnterPip) }
	}, [videoRef.current])

	function initSpeech(){
		try{
			const Rec = window.SpeechRecognition || window.webkitSpeechRecognition
			if(!Rec){ setSttSupported(false); return }
			setSttSupported(true)
			const rec = new Rec()
			rec.lang = 'en-US'
			rec.continuous = true
			rec.interimResults = true
			rec.onresult = (event) => {
				let interim = ''
				let allFinalText = ''
				
				// Process ALL results to get complete transcript
				for (let i = 0; i < event.results.length; i++){
					const res = event.results[i]
					if(res.isFinal){ 
						allFinalText += res[0].transcript + ' '
					} else { 
						interim += res[0].transcript 
					}
				}
				
				// Update answers state with complete text (final + interim)
				if (typeof idx === 'number' && idx >= 0){
					const arr = [...answers]
					
					// Combine all final text with current interim text
					const finalPart = allFinalText.trim()
					const interimPart = interim.trim()
					
					// APPEND final part to existing answer (don't replace)
					const existingText = arr[idx] || ''
					arr[idx] = existingText + (existingText && finalPart ? ' ' : '') + finalPart
					setAnswers(arr)
					
					// Store interim text separately (will be appended in display)
					interimTextRef.current = interimPart
					
					// Show complete text in console
					const completeText = arr[idx] + (interimPart ? ' ' + interimPart : '')
					console.log('🎤 Speaking:', completeText)
				}
			}
			rec.onend = () => { 
				setListening(false)
				console.log('Speech recognition ended')
			}
			rec.onerror = (event) => { 
				setListening(false)
				console.error('Speech recognition error:', event.error)
				if (event.error === 'not-allowed') {
					setError('Microphone access denied. Please allow microphone access to use voice recording.')
				} else if (event.error === 'no-speech') {
					console.log('No speech detected, continuing...')
				} else {
					setError(`Voice recording error: ${event.error}`)
				}
			}
			recognitionRef.current = rec
		}catch(e){ setSttSupported(false) }
	}

	function startListening(){
		if(!recognitionRef.current) return
		try{ 
			// Stop any existing recognition first
			if (listening) {
				recognitionRef.current.stop()
			}
			// Small delay to ensure previous session is closed
			setTimeout(() => {
				try {
					recognitionRef.current.start()
					setListening(true)
					console.log('Started speech recognition')
				} catch(e) {
					console.error('Error starting speech recognition:', e)
					setError('Failed to start voice recording. Please try again.')
				}
			}, 100)
		}catch(e){ 
			console.error('Error in startListening:', e)
			setError('Voice recording not available. Please check microphone permissions.')
		}
	}

	function stopListening(){
		if(!recognitionRef.current) return
		try{ 
			recognitionRef.current.stop()
			setListening(false)
			interimTextRef.current = '' // Clear interim text when stopping
			console.log('Stopped speech recognition')
		}catch(e){ 
			console.error('Error stopping speech recognition:', e)
		}
	}

	function speakQuestion(text){
		try{
			if(!autoSpeak) return
			if (!('speechSynthesis' in window)) return
			const u = new SpeechSynthesisUtterance(text)
			u.lang = 'en-US'
			u.rate = 1.0
			window.speechSynthesis.cancel()
			window.speechSynthesis.speak(u)
		}catch{}
	}

	async function startCamera(){
		try{
			setCameraStatus('requesting')
			const stream = await navigator.mediaDevices.getUserMedia({ 
				video: { 
					width: { ideal: 640 },
					height: { ideal: 480 },
					facingMode: 'user'
				}, 
				audio: false 
			})
			mediaRef.current = stream
			// Mark active as soon as we have a stream
			setCameraStatus('active')
			if (videoRef.current) {
				try {
					// Ensure autoplay works on mobile: set attributes before assigning stream
					videoRef.current.muted = true
					videoRef.current.setAttribute('muted', '')
					videoRef.current.setAttribute('playsinline', '')
					videoRef.current.setAttribute('autoplay', '')
					videoRef.current.srcObject = stream
					
					// Better video ready state handling
					videoRef.current.onloadedmetadata = () => { 
						console.log('📹 Video metadata loaded:', {
							width: videoRef.current.videoWidth,
							height: videoRef.current.videoHeight,
							readyState: videoRef.current.readyState
						});
						try { 
							videoRef.current.play().then(() => {
								console.log('📹 Video playing successfully');
								setCameraStatus('active');
							}).catch(e => console.warn('Video play error:', e));
						} catch(e) {
							console.warn('Video play error (sync):', e);
						}
					}
					
					videoRef.current.oncanplay = () => { 
						console.log('📹 Video can play, ready state:', videoRef.current.readyState);
						setCameraStatus('active');
					}
					
					// Add error handling
					videoRef.current.onerror = (e) => {
						console.error('📹 Video error:', e);
						setCameraStatus('error');
					}
					
					await videoRef.current.play()
				} catch(playError) {
					console.warn('Video play error:', playError);
				}
				
				// Fallback: ensure active if tracks are live
				setTimeout(() => {
					const hasTrack = !!(mediaRef.current && mediaRef.current.getVideoTracks && mediaRef.current.getVideoTracks().length)
					const videoReady = videoRef.current && videoRef.current.videoWidth > 0 && videoRef.current.readyState >= 2
					console.log('📹 Fallback check:', { hasTrack, videoReady });
					if (hasTrack && videoReady) setCameraStatus('active')
				}, 1200)
			}
		}catch(e){
			console.warn('Camera error:', e)
			if (e.name === 'NotAllowedError') {
				setCameraStatus('denied')
			} else {
				setCameraStatus('error')
			}
		}
	}
	
	function stopCamera(){
		try{ 
			if (mediaRef.current) {
				mediaRef.current.getTracks().forEach(track => track.stop())
			}
		} catch {}
	}

	async function start(){
		setLoading(true)
		setError('')
		try{
			// Enter fullscreen for focused interview experience
			try{
				if (containerRef.current && !document.fullscreenElement) {
					await containerRef.current.requestFullscreen()
				}
			}catch{}
			// Ensure camera is active before starting
			if (cameraStatus !== 'active') {
				throw new Error('Please allow camera access before starting the interview.')
			}
			const payload = { skills: skills.split(',').map(s=>s.trim()).filter(Boolean), role_hint: roleHint }
			const { data } = await axios.post(`${API_BASE}/interview/questions`, payload)
			if(!data.success) throw new Error(data.error || 'Failed')
			setQuestions(data.questions || [])
			setAnswers(new Array((data.questions || []).length).fill(''))
			setIdx(0)
			setTimer((data.questions?.[0]?.time_limit_sec) || 90)
			if ((data.questions || []).length > 0) speakQuestion(data.questions[0].text || '')
			setShowRules(false)
			// Mark interview as active so Dashboard can hide Start option
			try { localStorage.setItem('interview_active', '1') } catch {}
			
			// Auto-start voice recording if supported
			setTimeout(() => {
				if(sttSupported && recognitionRef.current){
					startListening()
				}
			}, 1000)
		} catch(e){ setError(e.message) } finally { setLoading(false) }
	}

	useEffect(() => {
		if (!questions.length) return
		clearInterval(timerRef.current)
		timerRef.current = setInterval(() => {
			setTimer(t => {
				if (t <= 1) { clearInterval(timerRef.current); next() ; return 0 }
				return t - 1
			})
		}, 1000)
		return () => clearInterval(timerRef.current)
	}, [questions, idx])

	function next(){
		if(!questions.length) return
		
		// Stop current recording before moving to next question
		if(listening){
			stopListening()
		}
		
		if(idx + 1 < questions.length){
			setIdx(idx + 1)
			setTimer(questions[idx + 1]?.time_limit_sec || 90)
			speakQuestion(questions[idx + 1]?.text || '')
			
			// Restart recording for the next question after a short delay
			setTimeout(() => {
				if(sttSupported && recognitionRef.current){
					startListening()
				}
			}, 500)
		}else{
			finish()
		}
	}

	async function finish(){
		clearInterval(timerRef.current)
		setLoading(true)
		try{
			const payload = { role_hint: roleHint, questions, answers, skills: skills.split(',').map(s=>s.trim()).filter(Boolean) }
			const { data } = await axios.post(`${API_BASE}/interview/submit`, payload)
			if(!data.success) throw new Error(data.error||'Failed')
			const entry = {
				date: new Date().toLocaleString(),
				questions: answers.filter(a => (a||'').trim().length > 0).length,
				total: questions.length,
				status: 'completed',
				score: Math.round(data.result?.total_score || 0)
			}
			const hist = JSON.parse(localStorage.getItem('interview_history') || '[]')
			localStorage.setItem('interview_history', JSON.stringify([entry, ...hist].slice(0, 50)))
			try{ if (document.fullscreenElement) await document.exitFullscreen() }catch{}
			// Stop camera before navigating
			try { stopCamera() } catch {}
			// Clear interview active flag
			try { localStorage.removeItem('interview_active') } catch {}
			navigate('/interview/results', { state: { result: data.result, questions } })
		} catch(e){ setError(e.message) } finally { setLoading(false) }
	}

	const renderCameraPreview = (size = 'normal') => {
		const small = size === 'small'
		const boxHeight = small ? 160 : 240
		switch(cameraStatus) {
			case 'active':
				return (
					<div style={{ width: '100%', height: boxHeight, borderRadius: 10, border: '1px solid #e5e7eb', background: '#000', overflow: 'hidden' }}>
						<video 
						ref={videoRef} 
						autoPlay 
						muted
						playsInline 
						disabled={false}
						disablePictureInPicture
						controls={false}
						controlsList="nodownload noplaybackrate noremoteplayback nofullscreen"
						style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} 
						/>
					</div>
				)
			case 'requesting':
				return (
					<div style={{ 
						width: '100%', 
						height: boxHeight, 
						borderRadius: 10, 
						border: '1px solid #e5e7eb', 
						background: '#f8fafc',
						display: 'grid',
						placeItems: 'center',
						color: '#64748b'
					}}>
						<div style={{ textAlign: 'center' }}>
							<div style={{ fontSize: 24, marginBottom: 8 }}>📹</div>
							<div>Requesting camera access...</div>
						</div>
					</div>
				)
			case 'denied':
				return (
					<div style={{ 
						width: '100%', 
						height: boxHeight, 
						borderRadius: 10, 
						border: '1px solid #e5e7eb', 
						background: '#fef2f2',
						display: 'grid',
						placeItems: 'center',
						color: '#991b1b',
						padding: 20,
						textAlign: 'center'
					}}>
						<div>
							<div style={{ fontSize: 24, marginBottom: 8 }}>🚫</div>
							<div style={{ fontWeight: 600, marginBottom: 8 }}>Camera Access Denied</div>
							<div style={{ fontSize: 14, marginBottom: 12 }}>Please allow camera access in your browser settings to use this feature.</div>
							<button className="btn btn-secondary" onClick={startCamera}>Retry Camera</button>
						</div>
					</div>
				)
			case 'error':
				return (
					<div style={{ 
						width: '100%', 
						height: 240, 
						borderRadius: 10, 
						border: '1px solid #e5e7eb', 
						background: '#fef2f2',
						display: 'grid',
						placeItems: 'center',
						color: '#991b1b',
						padding: 20,
						textAlign: 'center'
					}}>
						<div>
							<div style={{ fontSize: 24, marginBottom: 8 }}>⚠️</div>
							<div style={{ fontWeight: 600, marginBottom: 8 }}>Camera Error</div>
							<div style={{ fontSize: 14, marginBottom: 12 }}>Unable to access camera. Please check your device.</div>
							<button className="btn btn-secondary" onClick={startCamera}>Retry Camera</button>
						</div>
					</div>
				)
			default:
				return null
		}
	}

	return (
			<>
				{questions.length === 0 && (<NavBar title="Interview" />)}
				<div className={`${questions.length > 0 ? 'interview-run-container' : 'container'}`} ref={containerRef}>
					{questions.length === 0 && (
						<>
							<div className="panel" style={{ marginBottom: 20 }}>
								<h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
									<span>🎯</span>
									Ready to Start Your Mock Interview?
								</h2>
								<p className="muted">Category: <strong style={{ color: '#111827', textTransform: 'capitalize' }}>{category}</strong></p>
								<div className="actions" style={{ marginTop: 16 }}>
									<input 
										className="textarea" 
										style={{ minHeight: 44 }} 
										placeholder="Optional: comma-separated skills to tailor questions (e.g., python, react, aws)" 
										value={skills} 
										onChange={e=>setSkills(e.target.value)} 
									/>
									<button 
										className="btn btn-primary" 
										disabled={loading || cameraStatus!=='active'} 
										onClick={()=>setShowRules(true)}
										style={{ display: 'flex', alignItems: 'center', gap: 8 }}
									>
										<span>🚀</span>
										Start Interview
									</button>
								</div>
							</div>

							<div className="interview-camera-preview">
								<div className="interview-camera-title">📹 Webcam Preview</div>
								{renderCameraPreview()}
							</div>
						</>
					)}

				{showLeaveConfirm && (
					<div className="loading-overlay" style={{ display: 'grid', placeItems: 'center', background: 'rgba(15,23,42,0.45)' }}>
						<div className="card" style={{ maxWidth: 520 }}>
							<h3 style={{ marginTop: 0 }}>Leave interview?</h3>
							<p className="muted">Your progress may be lost if you leave now.</p>
							<div className="actions" style={{ marginTop: 12 }}>
								<button className="btn" onClick={() => setShowLeaveConfirm(false)}>Stay</button>
								<button className="btn btn-primary" onClick={() => { try{ if (document.fullscreenElement) document.exitFullscreen() }catch{}; stopCamera(); navigate(-1) }}>Leave Interview</button>
							</div>
						</div>
					</div>
				)}

					{showRules && questions.length === 0 && (
						<div className="interview-rules-modal">
							<div className="interview-rules-card">
								<h3 className="interview-rules-title">Interview Rules & Guidelines</h3>
								<ul className="interview-rules-list">
									<li>Enable your webcam and keep it on throughout the interview. Camera monitoring is required for security.</li>
									<li><strong>Face Detection:</strong> Always active during interview. Only one person should be visible. Multiple people or electronic devices will immediately terminate the interview.</li>
									<li>Do not paste text into the answer box. Only manual typing is allowed to ensure authenticity.</li>
									<li>Stay on this tab at all times. Switching tabs, minimizing, or losing focus will be flagged as violations.</li>
									<li>Each question has a countdown timer. When time expires, the system will automatically advance to the next question.</li>
									<li>You have 3 violation warnings. After 3 violations, the interview will be automatically terminated.</li>
									<li>The interview will be conducted in fullscreen mode for a focused experience.</li>
								</ul>
								<div className="interview-rules-actions">
									<button 
										className="interview-btn interview-btn-secondary" 
										onClick={startCamera}
									>
										🔄 Retry Camera
									</button>
									<button 
										className="interview-btn interview-btn-primary" 
										disabled={cameraStatus!=='active' || loading} 
										onClick={start}
									>
										✅ I Agree & Start Interview
									</button>
									<button 
										className="interview-btn interview-btn-secondary" 
										onClick={()=>setShowRules(false)}
									>
										❌ Cancel
									</button>
								</div>
								{cameraStatus!=='active' && (
									<div style={{ 
										marginTop: 16, 
										padding: 12, 
										background: 'rgba(239, 68, 68, 0.1)', 
										borderRadius: 8, 
										textAlign: 'center',
										color: '#dc2626',
										fontWeight: 500
									}}>
										⚠️ Waiting for camera permission to continue...
									</div>
								)}
							</div>
						</div>
					)}

					{questions.length > 0 && (
					<div style={{ padding: '20px', width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
							<div className="interview-question-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', maxHeight: '100%' }}>
								<div className="interview-question-header">
									<div className="interview-question-counter">
										Question {idx + 1} of {questions.length}
									</div>
									<div className="interview-timer">
										Time left: {timer}s
									</div>
								</div>
								
								<div className="interview-question-text">{questions[idx]?.text}</div>
								
								<div className="interview-progress-container">
									<div 
										className="interview-progress-bar" 
										style={{ width: `${((idx) / Math.max(1, questions.length)) * 100}%` }}
									></div>
								</div>
								
								<textarea 
									className="interview-answer-textarea" 
									style={{ flex: 1, minHeight: '300px', resize: 'none' }}
									placeholder="Type your answer here... (Paste is disabled for security)" 
									value={(answers[idx] || '') + (interimTextRef.current && listening ? ' ' + interimTextRef.current : '')} 
									onChange={(e)=>{ 
										// Only update permanent answer, not interim text
										const a=[...answers]; 
										const newValue = e.target.value;
										// Remove any interim text from the value before saving
										const cleanValue = interimTextRef.current && newValue.endsWith(interimTextRef.current) 
											? newValue.slice(0, -interimTextRef.current.length).trim()
											: newValue;
										a[idx] = cleanValue;
										setAnswers(a);
									}}
									onPaste={(e)=>e.preventDefault()}
									onDrop={(e)=>e.preventDefault()}
									onContextMenu={(e)=>e.preventDefault()}
									onKeyDown={(e)=>{ if ((e.ctrlKey || e.metaKey) && (e.key==='v' || e.key==='V')) { e.preventDefault() } if (e.shiftKey && e.key==='Insert') { e.preventDefault() } }}
								/>
								
								{/* Recording status indicator */}
								{listening && (
									<div style={{
										padding: '8px 12px',
										background: 'linear-gradient(90deg, #4CAF50, #45a049)',
										color: 'white',
										borderRadius: '4px',
										marginTop: '8px',
										display: 'flex',
										alignItems: 'center',
										gap: '8px',
										fontSize: '14px',
										fontWeight: '500'
									}}>
										<span style={{
											width: '8px',
											height: '8px',
											background: 'white',
											borderRadius: '50%',
											animation: 'pulse 1.5s ease-in-out infinite'
										}}></span>
										🎤 Recording in progress - All words are being captured
										<span style={{ 
											marginLeft: 'auto', 
											fontSize: '13px', 
											opacity: 0.95,
											fontWeight: '600' 
										}}>
											Words: {((answers[idx] || '') + (interimTextRef.current ? ' ' + interimTextRef.current : '')).trim().split(/\s+/).filter(w => w.length > 0).length}
										</span>
									</div>
								)}
								
								<div className="interview-controls">
									<button className="interview-btn interview-btn-secondary" onClick={next}>
										⏭️ Next Question
									</button>
									<button className="interview-btn interview-btn-success" onClick={finish}>
										✅ Finish Interview
									</button>
									{sttSupported && !listening && (
										<button className="interview-btn interview-btn-primary" onClick={startListening}>
											🎙️ Start Voice Recording
										</button>
									)}
									{sttSupported && listening && (
										<button className="interview-btn interview-btn-danger" onClick={stopListening}>
											⏹️ Stop Recording
										</button>
									)}
									{sttSupported && (
										<label style={{ 
											display: 'inline-flex', 
											alignItems: 'center', 
											gap: 8, 
											color: 'rgba(255, 255, 255, 0.8)',
											fontSize: '0.9rem'
										}}>
											<input 
												type="checkbox" 
												checked={autoSpeak} 
												onChange={(e)=>setAutoSpeak(e.target.checked)}
												style={{ transform: 'scale(1.2)' }}
											/>
											<span>🔊 Read questions aloud</span>
										</label>
									)}
									
									{/* Face Detection Status - Always Active (No Toggle) */}
									<div style={{ 
										display: 'inline-flex', 
										alignItems: 'center', 
										gap: 8, 
										color: 'rgba(255, 255, 255, 0.8)',
										fontSize: '0.8rem',
										padding: '4px 8px',
										background: 'rgba(0, 0, 0, 0.3)',
										borderRadius: 4
									}}>
										<div
											style={{
												background: '#28a745',
												color: 'white',
												border: 'none',
												padding: '2px 6px',
												borderRadius: 3,
												fontSize: '0.7rem'
											}}
										>
											👁️ ACTIVE
										</div>
										<span>
											{faceStatus.facesCount === 1 ? '✅ Single Person' : 
											 faceStatus.facesCount > 1 ? '⚠️ Multiple People' : 
											 faceStatus.facesCount === 0 ? (cameraStatus === 'active' ? '👤 No Face Detected' : '📷 Camera Starting...') : '🔍 Detecting...'}
											{faceStatus.confidence > 0 && (
												<span style={{ fontSize: '0.7rem', opacity: 0.7 }}>
													 ({Math.round(faceStatus.confidence * 100)}%)
												</span>
											)}
										</span>
									</div>
								</div>
							</div>
							{/* Floating webcam preview (draggable) */}
							<div
								ref={floatRef}
								className="interview-floating-camera"
								style={{
									left: floatPos.x !== null ? floatPos.x : 'auto',
									top: floatPos.y !== null ? floatPos.y : 'auto',
									right: floatPos.x === null ? 16 : 'auto',
									bottom: floatPos.y === null ? 16 : 'auto',
									width: 260,
									cursor: dragging ? 'grabbing' : 'grab',
									userSelect: 'none',
								}}
								onMouseDown={(e) => onDragStart(e.clientX, e.clientY)}
								onTouchStart={(e) => { if (e.touches && e.touches[0]) { e.preventDefault(); onDragStart(e.touches[0].clientX, e.touches[0].clientY) } }}
							>
								{renderCameraPreview('small')}
								
								{/* Simple Face Detection Component - Always Active */}
								{cameraStatus === 'active' && (
									<SimpleFaceDetection
										videoRef={videoRef}
										isActive={true} // Always active - no toggle allowed
										onViolation={handleFaceViolation}
										onFaceStatus={handleFaceStatus}
									/>
								)}
							</div>
						</div>
					)}

					{!!error && <div className="toast"><div>{error}</div><button onClick={()=>setError('')}>×</button></div>}
					{!!tabWarning && (
						<div className="interview-violation-warning">
							<div style={{ fontWeight: 600, marginBottom: 4 }}>⚠️ Security Violation</div>
							<div>{tabWarning}</div>
							<button 
								onClick={()=>setTabWarning('')}
								style={{ 
									position: 'absolute', 
									top: 8, 
									right: 12, 
									background: 'none', 
									border: 'none', 
									color: 'white', 
									fontSize: 18, 
									cursor: 'pointer' 
								}}
							>
								×
							</button>
						</div>
					)}
					
					{!!faceWarning && (
						<div className="interview-violation-warning" style={{ 
							background: faceWarning.includes('INTERVIEW TERMINATED') 
								? 'linear-gradient(135deg, #7f1d1d, #991b1b)' // Darker red for critical
								: 'linear-gradient(135deg, #dc2626, #b91c1c)',
							border: faceWarning.includes('INTERVIEW TERMINATED') 
								? '3px solid #fca5a5' // Thicker border for critical
								: '2px solid #fca5a5',
							fontSize: faceWarning.includes('INTERVIEW TERMINATED') ? '18px' : '16px',
							animation: faceWarning.includes('INTERVIEW TERMINATED') ? 'pulse 1s infinite' : 'none'
						}}>
							<div style={{ fontWeight: 600, marginBottom: 4 }}>
								{faceWarning.includes('INTERVIEW TERMINATED') ? '🚨 CRITICAL VIOLATION' : '👁️ Face Detection Alert'}
							</div>
							<div>{faceWarning}</div>
							<button 
								onClick={()=>setFaceWarning('')}
								style={{ 
									position: 'absolute', 
									top: 8, 
									right: 12, 
									background: 'none', 
									border: 'none', 
									color: 'white', 
									fontSize: 18, 
									cursor: 'pointer' 
								}}
							>
								×
							</button>
						</div>
					)}
					{loading && <div className="loading-overlay"><div className="spinner"/></div>}
				</div>
			</>
		)
	}