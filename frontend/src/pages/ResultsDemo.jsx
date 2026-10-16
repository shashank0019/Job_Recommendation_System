import React from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar.jsx'
import ProgressBar from '../components/ProgressBar.jsx'
import SkillGapAnalysis from '../components/SkillGapAnalysis.jsx'
import '../styles.css'

export default function ResultsDemo(){
	// Mock data for demonstration
	const result = {
		total_score: 85,
		evaluation_method: 'Enhanced AI Evaluation',
		per_answer: [
			{
				score: 92,
				strengths: ['Demonstrated deep understanding of React architecture', 'Provided specific, measurable examples'],
				improvements: ['Could elaborate more on performance optimization', 'Consider mentioning accessibility considerations']
			},
			{
				score: 78,
				strengths: ['Clear explanation of authentication flow', 'Good security awareness'],
				improvements: ['More details on JWT implementation', 'Discuss refresh token strategies']
			},
			{
				score: 88,
				strengths: ['Excellent system design thinking', 'Considered scalability from the start'],
				improvements: ['Could mention database sharding', 'Discuss caching strategies in more detail']
			}
		]
	}
	
	const questions = [
		{
			text: "Describe how you would architect a full-stack e-commerce application. What technologies would you choose for frontend, backend, and database layers?"
		},
		{
			text: "Walk me through how you would handle user authentication and authorization across a full-stack application. Include security best practices."
		},
		{
			text: "How would you implement real-time features (like live chat or notifications) in a full-stack application? Discuss both frontend and backend considerations."
		}
	]
	
	const overall = Math.round(result.total_score || 0)
	const userSkills = ['React', 'Node.js', 'JavaScript', 'MongoDB', 'Express']
	const targetSkills = ['React', 'Node.js', 'JavaScript', 'MongoDB', 'Express', 'TypeScript', 'AWS', 'Docker', 'Redis']

	// Helper functions for professional styling
	const getScoreColor = (score) => {
		if (score >= 80) return '#10b981' // Green
		if (score >= 60) return '#f59e0b' // Yellow
		return '#ef4444' // Red
	}

	const getPerformanceLevel = (score) => {
		if (score >= 90) return { level: 'Excellent', icon: '🏆' }
		if (score >= 80) return { level: 'Very Good', icon: '⭐' }
		if (score >= 70) return { level: 'Good', icon: '👍' }
		if (score >= 60) return { level: 'Fair', icon: '📈' }
		return { level: 'Needs Improvement', icon: '📚' }
	}

	const performance = getPerformanceLevel(overall)

	return (
		<>
			<NavBar title="Interview Results - Demo" />
			<div className="container">
				{/* Professional Header Section */}
				<div style={{ 
					background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
					borderRadius: 16,
					padding: 32,
					color: 'white',
					marginBottom: 24,
					textAlign: 'center',
					boxShadow: '0 10px 25px rgba(102, 126, 234, 0.3)'
				}}>
					<div style={{ fontSize: 48, marginBottom: 8 }}>{performance.icon}</div>
					<h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>Interview Complete!</h1>
					<p style={{ margin: '8px 0 0 0', fontSize: 18, opacity: 0.9 }}>
						{performance.level} Performance - Fullstack Developer Role
					</p>
				</div>

				{/* Enhanced Score Overview */}
				<div className="panel" style={{ marginBottom: 24 }}>
					<div className="section-title" style={{ marginBottom: 20, fontSize: 20 }}>Performance Overview</div>
					<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
						<div className="card" style={{ 
							background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
							border: '2px solid #e2e8f0',
							textAlign: 'center',
							padding: 24,
							borderRadius: 12
						}}>
							<div style={{ 
								fontSize: 48, 
								fontWeight: 800, 
								color: getScoreColor(overall),
								marginBottom: 8
							}}>
								{overall}%
							</div>
							<div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>Overall Score</div>
							<p className="muted" style={{ margin: 0, marginBottom: 12 }}>Based on all completed questions</p>
							<ProgressBar value={overall} />
						</div>
						
						<div className="card" style={{ padding: 24, borderRadius: 12 }}>
							<div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12 }}>Technical Accuracy</div>
							<div style={{ 
								fontSize: 24, 
								fontWeight: 700, 
								color: getScoreColor(88),
								marginBottom: 8
							}}>
								88%
							</div>
							<ProgressBar value={88} />
							<p className="muted" style={{ marginTop: 8, margin: 0 }}>Correctness of technical concepts</p>
						</div>
						
						<div className="card" style={{ padding: 24, borderRadius: 12 }}>
							<div style={{ fontWeight: 700, fontSize: 16, marginBottom: 12 }}>Communication</div>
							<div style={{ 
								fontSize: 24, 
								fontWeight: 700, 
								color: getScoreColor(82),
								marginBottom: 8
							}}>
								82%
							</div>
							<ProgressBar value={82} />
							<p className="muted" style={{ marginTop: 8, margin: 0 }}>Clarity and structure of explanations</p>
						</div>
					</div>
				</div>

				{/* Enhanced Question Analysis */}
				<div className="panel" style={{ marginBottom: 24 }}>
					<div className="section-title" style={{ marginBottom: 20, fontSize: 20 }}>Question-by-Question Analysis</div>
					<div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
						{questions.map((q, i) => {
							const questionScore = Math.round(result.per_answer?.[i]?.score || 0)
							const answerData = result.per_answer?.[i] || {}
							
							return (
								<div key={i} className="card" style={{ 
									padding: 20,
									border: `2px solid ${getScoreColor(questionScore)}20`,
									borderLeft: `4px solid ${getScoreColor(questionScore)}`,
									borderRadius: 12,
									transition: 'all 0.3s ease'
								}}>
									<div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 16, alignItems: 'start' }}>
										<div>
											<div style={{ 
												display: 'flex', 
												alignItems: 'center', 
												gap: 8, 
												marginBottom: 8 
											}}>
												<div style={{ 
													fontWeight: 700, 
													fontSize: 16,
													color: '#1e293b'
												}}>
													Question {i + 1}
												</div>
												<div style={{
													background: getScoreColor(questionScore),
													color: 'white',
													padding: '4px 12px',
													borderRadius: 16,
													fontSize: 12,
													fontWeight: 600
												}}>
													{questionScore}%
												</div>
											</div>
											<div className="muted" style={{ 
												marginBottom: 12,
												lineHeight: 1.5,
												fontSize: 14
											}}>
												{q.text}
											</div>
											
											{/* Enhanced feedback display */}
											{answerData.strengths && answerData.strengths.length > 0 && (
												<div style={{ marginBottom: 8 }}>
													<div style={{ 
														fontSize: 14, 
														fontWeight: 600, 
														color: '#10b981',
														marginBottom: 4,
														display: 'flex',
														alignItems: 'center',
														gap: 4
													}}>
														✅ Strengths:
													</div>
													<ul style={{ 
														margin: 0, 
														paddingLeft: 16,
														fontSize: 13,
														color: '#64748b'
													}}>
														{answerData.strengths.map((strength, idx) => (
															<li key={idx} style={{ marginBottom: 2 }}>{strength}</li>
														))}
													</ul>
												</div>
											)}
											
											{answerData.improvements && answerData.improvements.length > 0 && (
												<div>
													<div style={{ 
														fontSize: 14, 
														fontWeight: 600, 
														color: '#f59e0b',
														marginBottom: 4,
														display: 'flex',
														alignItems: 'center',
														gap: 4
													}}>
														💡 Areas for Improvement:
													</div>
													<ul style={{ 
														margin: 0, 
														paddingLeft: 16,
														fontSize: 13,
														color: '#64748b'
													}}>
														{answerData.improvements.map((improvement, idx) => (
															<li key={idx} style={{ marginBottom: 2 }}>{improvement}</li>
														))}
													</ul>
												</div>
											)}
										</div>
										
										<div style={{ 
											textAlign: 'center',
											minWidth: 80
										}}>
											<div style={{ 
												fontSize: 32, 
												fontWeight: 800, 
												color: getScoreColor(questionScore),
												lineHeight: 1
											}}>
												{questionScore}%
											</div>
											<div style={{ 
												fontSize: 12, 
												color: '#64748b',
												marginTop: 4
											}}>
												Score
											</div>
										</div>
									</div>
								</div>
							)
						})}
					</div>
				</div>

				{/* Evaluation Method Info */}
				<div className="panel" style={{ marginBottom: 24 }}>
					<div className="section-title" style={{ marginBottom: 16, fontSize: 20 }}>Evaluation Details</div>
					<div className="card" style={{ 
						background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
						border: '2px solid #0ea5e9',
						padding: 20,
						borderRadius: 12
					}}>
						<div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
							<div style={{ fontSize: 24 }}>🤖</div>
							<div>
								<div style={{ fontWeight: 700, marginBottom: 4, fontSize: 16 }}>
									Evaluated using: {result.evaluation_method}
								</div>
								<p className="muted" style={{ margin: 0, fontSize: 14 }}>
									Your responses were analyzed using advanced AI evaluation criteria including 
									technical accuracy, communication skills, and problem-solving approach.
								</p>
							</div>
						</div>
					</div>
				</div>

				{/* Skill Gap Analysis for Career Development */}
				<SkillGapAnalysis 
					userSkills={userSkills}
					jobSkills={targetSkills}
					jobTitle="Senior Fullstack Developer"
				/>

				{/* Enhanced Action Buttons */}
				<div style={{ 
					display: 'flex', 
					gap: 12, 
					justifyContent: 'center',
					marginTop: 32,
					paddingBottom: 32,
					flexWrap: 'wrap'
				}}>
					<Link 
						className="btn btn-secondary" 
						to="/"
						style={{ 
							padding: '12px 24px',
							fontSize: 16,
							borderRadius: 8,
							display: 'flex',
							alignItems: 'center',
							gap: 8
						}}
					>
						🏠 Back to Dashboard
					</Link>
					<Link 
						className="btn btn-primary" 
						to="/interview/setup"
						style={{ 
							padding: '12px 24px',
							fontSize: 16,
							borderRadius: 8,
							display: 'flex',
							alignItems: 'center',
							gap: 8
						}}
					>
						🔄 Try Another Interview
					</Link>
					<Link 
						className="btn" 
						to="/problems"
						style={{ 
							padding: '12px 24px',
							fontSize: 16,
							borderRadius: 8,
							background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
							color: 'white',
							border: 'none',
							display: 'flex',
							alignItems: 'center',
							gap: 8
						}}
					>
						💻 Practice Coding
					</Link>
				</div>
			</div>
		</>
	)
}
