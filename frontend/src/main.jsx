import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import AuthGate from './components/AuthGate.jsx'
import App from './App.jsx'
import Dashboard from './pages/Dashboard.jsx'
import InterviewSetup from './pages/InterviewSetup.jsx'
import InterviewRun from './pages/InterviewRun.jsx'
import Results from './pages/Results.jsx'
import ResultsDemo from './pages/ResultsDemo.jsx'
import Problems from './pages/Problems.jsx'
import Profile from './pages/Profile.jsx'
import JobPostings from './pages/JobPostings.jsx'
import InterviewExperiences from './pages/InterviewExperiences.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}>
        <AuthGate>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/interview/setup" element={<InterviewSetup />} />
            <Route path="/interview/run" element={<InterviewRun />} />
            <Route path="/interview/results" element={<Results />} />
            <Route path="/interview/results-demo" element={<ResultsDemo />} />
            <Route path="/classic" element={<App />} />
            <Route path="/jobs" element={<JobPostings />} />
            <Route path="/experiences" element={<InterviewExperiences />} />
            <Route path="/problems" element={<Problems />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthGate>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
)