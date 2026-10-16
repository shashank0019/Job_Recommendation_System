import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import NavBar from './components/NavBar.jsx';
import SkillGapAnalysis from './components/SkillGapAnalysis.jsx';
import SplitView from './components/SplitView';
import './styles.css';

const RAW_API_BASE = import.meta.env.VITE_API_BASE || '/api';
const API_BASE = (() => {
  try {
    if (RAW_API_BASE.startsWith('http')) {
      return /\/api\/?$/.test(RAW_API_BASE) 
        ? RAW_API_BASE.replace(/\/$/, '') 
        : `${RAW_API_BASE.replace(/\/$/, '')}/api`;
    }
  } catch {}
  return RAW_API_BASE;
})();

export default function App() {
  // State declarations
  const [resumeText, setResumeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parsed, setParsed] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [liveJobs, setLiveJobs] = useState([]);
  const [problems, setProblems] = useState([]);
  const [problemLoading, setProblemLoading] = useState(false);
  const [problemFilters, setProblemFilters] = useState({ 
    difficulty: '', 
    topic: '', 
    search: '' 
  });
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [codeLang, setCodeLang] = useState('python');
  const [sourceCode, setSourceCode] = useState('');
  const [runResult, setRunResult] = useState(null);
  const [interviewOn, setInterviewOn] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [timer, setTimer] = useState(90);
  const timerRef = useRef(null);

  // Helper functions
  const notify = (msg) => { 
    setError(String(msg || 'Something went wrong')); 
    setTimeout(() => setError(''), 6000); 
  };

  const fetchProblems = async () => {
    setProblemLoading(true);
    try {
      const params = {};
      if (problemFilters.difficulty) params.difficulty = problemFilters.difficulty;
      if (problemFilters.topic) params.topic = problemFilters.topic;
      if (problemFilters.search) params.search = problemFilters.search;
      
      const { data } = await axios.get(`${API_BASE}/problems`, { params });
      if (!data.success) throw new Error(data.error || 'Failed to load problems');
      setProblems(data.items || []);
    } catch (e) { 
      notify(e.message); 
    } finally { 
      setProblemLoading(false); 
    }
  };

  // ... (other functions remain the same)

  // Main render
  return (
    <div className="app">
      <NavBar title="Job Recommendations" />
      
      <div className="container">
        {/* Main content area */}
        {selectedProblem ? (
          <div className="problem-view">
            {/* Problem details */}
            <div className="panel">
              <h2>{selectedProblem.title}</h2>
              <div dangerouslySetInnerHTML={{ __html: selectedProblem.description }} />
              
              {/* Code editor area */}
              <div className="code-editor">
                <select 
                  value={codeLang}
                  onChange={(e) => setCodeLang(e.target.value)}
                >
                  {(selectedProblem.languages || []).map(lang => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
                <textarea
                  value={sourceCode}
                  onChange={(e) => setSourceCode(e.target.value)}
                  className="code-input"
                  placeholder={`Enter your ${codeLang} code here...`}
                />
                <div className="actions">
                  <button 
                    className="btn btn-primary"
                    onClick={() => runOrSubmit('run')}
                  >
                    Run Code
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => runOrSubmit('submit')}
                  >
                    Submit
                  </button>
                </div>
              </div>

              {/* Results display */}
              {runResult && (
                <div className="results-panel">
                  <h3>Results</h3>
                  <pre>{JSON.stringify(runResult, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="dashboard">
            {/* Resume upload/input */}
            <div className="panel">
              <h2>Get Personalized Job Recommendations</h2>
              <p>Upload your resume or paste the text to find matching jobs using AI analysis.</p>
              
              <form onSubmit={onSubmit} className="resume-form">
                <textarea 
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste your resume here..."
                  className="resume-textarea"
                />
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Processing...' : 'Analyze Resume'}
                  </button>
                  <label className="file-upload-btn">
                    Upload File
                    <input 
                      type="file" 
                      accept=".pdf,.txt,.docx" 
                      onChange={onUpload} 
                      style={{ display: 'none' }} 
                    />
                  </label>
                </div>
              </form>
            </div>

            {/* Parsed resume preview */}
            {parsed && (
              <div className="panel">
                <h3>Parsed Resume</h3>
                <div className="skills-container">
                  {(parsed.skills || []).map((skill, i) => (
                    <span key={i} className="skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>
                {parsed.years_experience && (
                  <p>Experience: {parsed.years_experience} years</p>
                )}
              </div>
            )}

            {/* Job listings */}
            {jobs.length > 0 && (
              <div className="job-listings">
                <h2>Recommended Jobs</h2>
                <div className="job-grid">
                  {jobs.map((job, i) => (
                    <div key={i} className="job-card">
                      <h3>{job.title}</h3>
                      <p className="company">{job.company}</p>
                      <p className="location">{job.location || 'Remote'}</p>
                      <div className="job-actions">
                        <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn">
                          Apply
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Global loading overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
        </div>
      )}

      {/* Error toast */}
      {error && (
        <div className="toast error">
          {error}
          <button onClick={() => setError('')} className="close-btn">×</button>
        </div>
      )}
    </div>
  );
}
