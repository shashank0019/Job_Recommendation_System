import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function NavBar({ title = 'AI Mock Interview' }) {
    const location = useLocation()
    const isHome = location.pathname === '/'
    const [open, setOpen] = React.useState(false)
    const menuRef = React.useRef(null)
    const { user, logout } = useAuth()

    React.useEffect(() => {
        function onClickOutside(e) {
            if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false)
        }
        window.addEventListener('click', onClickOutside)
        return () => window.removeEventListener('click', onClickOutside)
    }, [])

    return (
        <div style={{ background: '#ffffff', borderBottom: '1px solid #e5e7eb' }}>
            <div style={{ maxWidth: 1100, margin: '0 auto', padding: '12px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: '#e0e7ff', display: 'grid', placeItems: 'center', color: '#3730a3', fontWeight: 800 }}>AI</div>
                    <div style={{ fontWeight: 800, letterSpacing: '-0.02em' }}>{title}</div>
                </div>
                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                    {!isHome && <Link className="link" to="/">Dashboard</Link>}
                    <Link className="link" to="/classic">Job Recommendations</Link>
                    <Link className="link" to="/jobs">Job Postings</Link>
                    <Link className="link" to="/experiences">Interview Experiences</Link>
                    <Link className="link" to="/interview/setup">Virtual Interview</Link>
                    <Link className="link" to="/problems">Problems</Link>

                    <div ref={menuRef} className="user-menu" style={{ position: 'relative' }}>
                        <button
                            type="button"
                            className="avatar-btn"
                            onClick={(e) => { e.stopPropagation(); setOpen((v) => !v) }}
                            aria-haspopup="menu"
                            aria-expanded={open}
                            title={`Account - ${user?.name || 'User'}`}
                        >
                            <span className="avatar-circle">
                                {user?.name?.charAt(0)?.toUpperCase() || '👤'}
                            </span>
                        </button>
                        {open && (
                            <div className="menu-dropdown" role="menu">
                                <div className="menu-header">
                                    Signed in as <strong>{user?.name}</strong>
                                </div>
                                <div className="menu-subheader">{user?.email}</div>
                                <Link className="menu-item" to="/profile" role="menuitem" onClick={() => setOpen(false)}>Profile Settings</Link>
                                <div className="menu-header">Quick Actions</div>
                                <Link className="menu-item" to="/interview/setup" role="menuitem" onClick={() => setOpen(false)}>Practice Interview</Link>
                                <Link className="menu-item" to="/classic" role="menuitem" onClick={() => setOpen(false)}>Upload Resume</Link>
                                <Link className="menu-item" to="/problems" role="menuitem" onClick={() => setOpen(false)}>Open Problems</Link>
                                <button className="menu-item" role="menuitem" onClick={() => { try { localStorage.removeItem('interview_history') } catch {} setOpen(false); alert('Cleared interview data') }}>Clear Interview Data</button>
                                <button className="menu-item danger" role="menuitem" onClick={async () => { setOpen(false); await logout(); window.location.reload() }}>
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
