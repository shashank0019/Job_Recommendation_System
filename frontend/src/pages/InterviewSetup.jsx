import React from 'react'
import { useNavigate } from 'react-router-dom'
import NavBar from '../components/NavBar.jsx'
import '../styles.css'

const categories = [
	{ key: 'technical', title: 'Technical Skills', desc: 'Programming concepts, algorithms, and frameworks', color: '#2563eb' },
	{ key: 'behavioral', title: 'Behavioral', desc: 'Past experiences, problem-solving, and decision-making', color: '#16a34a' },
	{ key: 'hr', title: 'HR / Personality', desc: 'Background, motivation, and cultural fit', color: '#7c3aed' },
	{ key: 'communication', title: 'Communication & Soft Skills', desc: 'Teamwork, leadership, and interpersonal skills', color: '#f97316' },
	{ key: 'case', title: 'Case Studies & Situational Judgement', desc: 'Problem-solving scenarios and critical thinking', color: '#ef4444' },
	// Added role-specific categories
	{ key: 'fullstack', title: 'Fullstack Developer', desc: 'Frontend + Backend application development', color: '#0ea5e9' },
	{ key: 'datascience', title: 'Data Science', desc: 'ML, analytics, statistics, and data tooling', color: '#10b981' },
]

export default function InterviewSetup() {
	const navigate = useNavigate()
	return (
		<>
			<NavBar title="Interview Setup" />
			<div className="interview-setup-container">
				<div className="interview-setup-content">
					<h1 className="interview-setup-title">Choose Your Interview Category</h1>
					<p className="interview-setup-subtitle">Select the type of interview you want to practice and boost your confidence.</p>
					
					<div className="interview-categories-grid">
						{categories.map(c => (
							<div key={c.key} className={`interview-category-card category-${c.key}`}>
								<div className="interview-category-icon"></div>
								<h3 className="interview-category-title">{c.title}</h3>
								<p className="interview-category-description">{c.desc}</p>
								<button 
									className="interview-category-button" 
									onClick={() => navigate(`/interview/run?category=${c.key}`)}
								>
									Start {c.title} Interview
								</button>
							</div>
						))}
					</div>
				</div>
			</div>
		</>
	)
} 