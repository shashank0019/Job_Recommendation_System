import React from 'react'

export default function SkillGapAnalysis({ userSkills = [], jobSkills = [], jobTitle = '' }) {
	// Ensure userSkills and jobSkills are arrays
	const safeUserSkills = Array.isArray(userSkills) ? userSkills : []
	const safeJobSkills = Array.isArray(jobSkills) ? jobSkills : []
	
	// Convert to sets for easier comparison
	const userSkillSet = new Set(safeUserSkills.map(s => s.toLowerCase()))
	const jobSkillSet = new Set(safeJobSkills.map(s => s.toLowerCase()))
	
	// Find skill gaps
	const missingSkills = [...jobSkillSet].filter(skill => !userSkillSet.has(skill))
	const matchingSkills = [...userSkillSet].filter(skill => jobSkillSet.has(skill))
	const extraSkills = [...userSkillSet].filter(skill => !jobSkillSet.has(skill))
	
	// Calculate match percentage
	const matchPercentage = safeJobSkills.length > 0 ? Math.round((matchingSkills.length / safeJobSkills.length) * 100) : 0
	
	// Skill categories for better organization
	const skillCategories = {
		'Programming Languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby'],
		'Frameworks & Libraries': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express', 'laravel', 'asp.net'],
		'Databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server', 'dynamodb'],
		'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'terraform', 'ansible', 'ci/cd'],
		'Data & AI': ['machine learning', 'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'nlp'],
		'Tools & Platforms': ['jira', 'confluence', 'slack', 'figma', 'postman', 'swagger', 'kafka', 'rabbitmq']
	}
	
	const categorizeSkills = (skills) => {
		const categorized = {}
		skills.forEach(skill => {
			for (const [category, categorySkills] of Object.entries(skillCategories)) {
				if (categorySkills.some(catSkill => skill.toLowerCase().includes(catSkill))) {
					if (!categorized[category]) categorized[category] = []
					categorized[category].push(skill)
					break
				}
			}
			if (!Object.values(categorized).flat().includes(skill)) {
				if (!categorized['Other']) categorized['Other'] = []
				categorized['Other'].push(skill)
			}
		})
		return categorized
	}
	
	const userCategorized = categorizeSkills(safeUserSkills)
	const missingCategorized = categorizeSkills(missingSkills)
	
	return (
		<div className="skill-gap-panel">
			<div className="skill-gap-header">
				<h3 className="skill-gap-title">Skill Gap Analysis for {jobTitle || 'Target Role'}</h3>
				<div className="skill-match-score">
					{matchPercentage}%
				</div>
			</div>
			
			{/* Overall Match Progress Bar */}
			<div style={{ marginBottom: 20 }}>
				<div style={{ background: '#f1f5f9', height: 8, borderRadius: 999, overflow: 'hidden' }}>
					<div 
						style={{ 
							width: `${matchPercentage}%`, 
							height: '100%', 
							background: matchPercentage >= 80 ? '#16a34a' : matchPercentage >= 60 ? '#f59e0b' : '#ef4444',
							transition: 'width 0.3s ease'
						}} 
					/>
				</div>
				<div className="muted" style={{ marginTop: 6, fontSize: 13 }}>
					{matchingSkills.length} of {safeJobSkills.length} required skills matched
				</div>
			</div>
			
			<div className="skill-categories">
				{/* Your Skills */}
				<div className="skill-category">
					<div className="category-title">Your Skills</div>
					{Object.entries(userCategorized).map(([category, skills]) => (
						<div key={category} style={{ marginBottom: 8 }}>
							<div style={{ fontSize: 12, fontWeight: 500, color: '#6b7280', marginBottom: 4 }}>{category}</div>
							<div className="skill-pills">
								{skills.map((skill, i) => (
									<span key={i} className={`skill-pill ${skill.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}>
										{skill}
									</span>
								))}
							</div>
						</div>
					))}
				</div>
				
				{/* Missing Skills */}
				{missingSkills.length > 0 && (
					<div className="skill-category">
						<div className="category-title">Skills to Develop</div>
						{Object.entries(missingCategorized).map(([category, skills]) => (
							<div key={category} style={{ marginBottom: 8 }}>
								<div style={{ fontSize: 12, fontWeight: 500, color: '#6b7280', marginBottom: 4 }}>{category}</div>
								<div className="skill-pills">
									{skills.map((skill, i) => (
										<span key={i} className="skill-pill" style={{ background: '#fef2f2', color: '#991b1b', borderColor: '#fecaca' }}>
											{skill}
										</span>
									))}
								</div>
							</div>
						))}
					</div>
				)}
			</div>
			
			{/* Success Message */}
			{missingSkills.length === 0 && (
				<div style={{ 
					background: '#f0fdf4', 
					border: '1px solid #bbf7d0', 
					borderRadius: 8, 
					padding: 12, 
					color: '#166534', 
					fontWeight: 600,
					textAlign: 'center'
				}}>
					🎉 All required skills covered!
				</div>
			)}
			
			{/* Recommendations */}
			{missingSkills.length > 0 && (
				<div style={{ 
					background: '#f0f9ff', 
					border: '1px solid #bae6fd', 
					borderRadius: 8, 
					padding: 12, 
					marginTop: 16 
				}}>
					<div style={{ fontWeight: 600, color: '#0c4a6e', marginBottom: 6, fontSize: 14 }}>💡 Priority Skills</div>
					<div className="skill-pills">
						{missingSkills.slice(0, 4).map((skill, i) => (
							<span key={i} className="skill-pill" style={{ background: '#ffffff', color: '#0c4a6e', borderColor: '#7dd3fc' }}>
								{skill}
							</span>
						))}
						{missingSkills.length > 4 && (
							<span className="skill-pill" style={{ background: '#ffffff', color: '#0c4a6e', borderColor: '#7dd3fc' }}>
								+{missingSkills.length - 4} more
							</span>
						)}
					</div>
				</div>
			)}
		</div>
	)
}
