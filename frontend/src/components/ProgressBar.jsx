import React from 'react'

export default function ProgressBar({ value = 0 }) {
	const pct = Math.max(0, Math.min(100, value))
	return (
		<div style={{ width: '100%', height: 8, background: '#e5e7eb', borderRadius: 999 }}>
			<div style={{ width: pct + '%', height: 8, background: '#2563eb', borderRadius: 999 }} />
		</div>
	)
} 