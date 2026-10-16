import React, { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar.jsx'
import '../styles.css'

function readHistory() {
	try {
		return JSON.parse(localStorage.getItem('interview_history') || '[]')
	} catch { return [] }
}

export default function Dashboard() {
	const history = useMemo(() => readHistory(), [])
	const total = history.length
	const completed = history.filter(h => h.status === 'completed').length
	const avg = history.length ? Math.round(history.reduce((a, b) => a + (b.score || 0), 0) / history.length) : 0
	const last = history[0]?.date || '—'
	const [interviewActive, setInterviewActive] = useState(false)

	useEffect(() => {
		try { setInterviewActive(localStorage.getItem('interview_active') === '1') } catch {}
		const onStorage = () => {
			try { setInterviewActive(localStorage.getItem('interview_active') === '1') } catch {}
		}
		window.addEventListener('storage', onStorage)
		return () => window.removeEventListener('storage', onStorage)
	}, [])

	return (
		<>
			<NavBar title="Career Guidance Platform" />
			<div className="page-container">
				<div className="dashboard-grid">
					<div className="panel welcome-panel">
						<h2 style={{ margin: 0 }}>Welcome to Career Guidance Platform</h2>
						<p className="muted" style={{ margin: '6px 0 0 0' }}>AI-powered job matching • Resume analysis • Virtual interview practice</p>
						<div className="h-scroll" style={{ marginTop: 12 }}>
							<div className="card feature" style={{ textAlign: 'center', padding: 24 }}>
								<div style={{ width: 64, height: 64, borderRadius: 16, background: '#e0e7ff', display: 'grid', placeItems: 'center', margin: '0 auto 16px', fontSize: 32 }}>💼</div>
								<h3 style={{ margin: '0 0 8px 0' }}>Job Recommendations</h3>
								<p className="muted" style={{ margin: '0 0 16px 0' }}>Upload your resume and get personalized job matches using AI analysis.</p>
								<Link className="btn btn-primary" to="/classic">Get Job Recommendations</Link>
							</div>
							<div className="card feature" style={{ textAlign: 'center', padding: 24 }}>
								<div style={{ width: 64, height: 64, borderRadius: 16, background: '#fef3c7', display: 'grid', placeItems: 'center', margin: '0 auto 16px', fontSize: 32 }}>🎯</div>
								<h3 style={{ margin: '0 0 8px 0' }}>Virtual Interview</h3>
								<p className="muted" style={{ margin: '0 0 16px 0' }}>Practice interviews with AI-generated questions and get instant feedback.</p>
								{interviewActive ? (
									<div style={{ display: 'flex', gap: 8, alignItems: 'center', justifyContent: 'center' }}>
										<span className="badge">In Progress</span>
										<Link className="btn btn-secondary" to="/interview/run">Resume</Link>
									</div>
								) : (
									<Link className="btn btn-primary" to="/interview/setup">Start Interview Practice</Link>
								)}
							</div>
							<div className="card feature" style={{ textAlign: 'center', padding: 24 }}>
								<div style={{ width: 64, height: 64, borderRadius: 16, background: '#dbeafe', display: 'grid', placeItems: 'center', margin: '0 auto 16px', fontSize: 32 }}>📋</div>
								<h3 style={{ margin: '0 0 8px 0' }}>Job Postings</h3>
								<p className="muted" style={{ margin: '0 0 16px 0' }}>Browse and post job opportunities in the community.</p>
								<Link className="btn btn-primary" to="/jobs">Browse Jobs</Link>
							</div>
							<div className="card feature" style={{ textAlign: 'center', padding: 24 }}>
								<div style={{ width: 64, height: 64, borderRadius: 16, background: '#f3e8ff', display: 'grid', placeItems: 'center', margin: '0 auto 16px', fontSize: 32 }}>💬</div>
								<h3 style={{ margin: '0 0 8px 0' }}>Interview Experiences</h3>
								<p className="muted" style={{ margin: '0 0 16px 0' }}>Read and share real interview experiences from the community.</p>
								<Link className="btn btn-primary" to="/experiences">Read Experiences</Link>
							</div>
							<div className="card feature" style={{ textAlign: 'center', padding: 24 }}>
								<div style={{ width: 64, height: 64, borderRadius: 16, background: '#dcfce7', display: 'grid', placeItems: 'center', margin: '0 auto 16px', fontSize: 32 }}>🧩</div>
								<h3 style={{ margin: '0 0 8px 0' }}>Coding Problems</h3>
								<p className="muted" style={{ margin: '0 0 16px 0' }}>Browse LeetCode-style problems and run code in Python/JS/C++/Java.</p>
								<Link className="btn btn-primary" to="/problems">Solve Problems</Link>
							</div>
						</div>
					</div>
				</div>
			</div>
		</>
	)
}
