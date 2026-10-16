import React, { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar.jsx'
import ProfileEdit from '../components/ProfileEdit.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import '../styles.css'

function readHistory() {
  try {
    return JSON.parse(localStorage.getItem('interview_history') || '[]')
  } catch {
    return []
  }
}

export default function Profile() {
  const { user } = useAuth()
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  
  const history = useMemo(() => readHistory(), [])
  const total = history.length
  const completed = history.filter(h => h.status === 'completed').length
  const avg = history.length ? Math.round(history.reduce((a, b) => a + (b.score || 0), 0) / history.length) : 0
  const last = history[0]?.date || '—'

  const handleProfileSave = () => {
    // Close modal first
    setIsEditModalOpen(false)
    
    // Immediate reload without delay
    window.location.reload()
  }

  return (
    <>
      <NavBar title="My Profile" />
      <div className="page-container">
        <div className="panel" style={{ marginBottom: 16 }}>
          <h2 style={{ margin: 0 }}>Account</h2>
          <p className="muted" style={{ margin: '6px 0 0 0' }}>Your profile and analytics</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 20, marginBottom: 20 }} key={refreshKey}>
          <div className="panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <div className="section-title">Profile Information</div>
              <button 
                className="btn-primary" 
                onClick={() => setIsEditModalOpen(true)}
                style={{ padding: '8px 16px', fontSize: '14px' }}
              >
                Edit Profile
              </button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
              <div className="card">
                <div className="muted">Name</div>
                <div style={{ fontWeight: 600, marginTop: 4 }}>{user?.name || 'Not provided'}</div>
              </div>
              <div className="card">
                <div className="muted">Email</div>
                <div style={{ fontWeight: 600, marginTop: 4 }}>{user?.email || 'Not provided'}</div>
              </div>
              <div className="card">
                <div className="muted">Mobile</div>
                <div style={{ fontWeight: 600, marginTop: 4 }}>
                  {user?.profile?.mobile && user.profile.mobile.trim() ? user.profile.mobile : 'Not provided'}
                </div>
              </div>
              <div className="card">
                <div className="muted">Gender</div>
                <div style={{ fontWeight: 600, marginTop: 4, textTransform: 'capitalize' }}>
                  {user?.profile?.gender && user.profile.gender.trim() ? user.profile.gender.replace('_', ' ') : 'Not provided'}
                </div>
              </div>
              <div className="card">
                <div className="muted">State</div>
                <div style={{ fontWeight: 600, marginTop: 4 }}>
                  {user?.profile?.state && user.profile.state.trim() ? user.profile.state : 'Not provided'}
                </div>
              </div>
              <div className="card">
                <div className="muted">Status</div>
                <div style={{ fontWeight: 600, marginTop: 4, textTransform: 'capitalize' }}>
                  {user?.profile?.employment_status && user.profile.employment_status.trim() ? user.profile.employment_status.replace('_', ' ') : 'Not provided'}
                </div>
              </div>
            </div>
            {user?.profile?.skills && user.profile.skills.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div className="muted" style={{ marginBottom: 8 }}>Skills</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {user.profile.skills.map((skill, index) => (
                    <span key={index} className="badge" style={{ background: '#7c3aed', color: 'white' }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1.3fr', gap: 20, alignItems: 'start' }}>
          <div className="panel">
            <div className="section-title">Interview Practice Stats</div>
            <div className="grid">
              <div className="card"><div className="muted">Total Sessions</div><div style={{ fontSize: 28, fontWeight: 800 }}>{total}</div></div>
              <div className="card"><div className="muted">Completed</div><div style={{ fontSize: 28, fontWeight: 800 }}>{completed}</div></div>
              <div className="card"><div className="muted">Average Score</div><div style={{ fontSize: 28, fontWeight: 800, color: '#7c3aed' }}>{avg}%</div></div>
              <div className="card"><div className="muted">Last Session</div><div style={{ fontSize: 16, fontWeight: 700 }}>{last}</div></div>
            </div>
          </div>

          <div className="panel">
            <div className="section-title">Recent Interview Sessions</div>
            <div>
              {history.length === 0 && (
                <div className="card" style={{ textAlign: 'center', color: '#64748b' }}>No sessions yet</div>
              )}
              {history.slice(0, 8).map((s, i) => (
                <div key={i} className="card" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr 1fr', gap: 12 }}>
                  <div className="muted">{s.date}</div>
                  <div>{s.questions} / {s.total} answered</div>
                  <div><span className="badge">{s.status}</span></div>
                  <div style={{ fontWeight: 700 }}>{s.score != null ? s.score + '%' : 'Not analyzed'}</div>
                </div>
              ))}
            </div>
            {history.length > 8 && (
              <div style={{ textAlign: 'center', marginTop: 12 }}>
                <Link className="link" to="/interview/history">View All Sessions</Link>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <ProfileEdit 
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSave={handleProfileSave}
      />
    </>
  )
}
