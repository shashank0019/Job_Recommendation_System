import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import NavBar from "./components/NavBar.jsx";
import SkillGapAnalysis from "./components/SkillGapAnalysis.jsx";
import SplitView from "./components/SplitView";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [parsed, setParsed] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [liveJobs, setLiveJobs] = useState([]);
  const [problems, setProblems] = useState([]);
  const [problemFilters, setProblemFilters] = useState({
    difficulty: "",
    topic: "",
    search: "",
  });
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [codeLang, setCodeLang] = useState("python");
  const [sourceCode, setSourceCode] = useState("");
  const [runResult, setRunResult] = useState(null);

  const [interviewOn, setInterviewOn] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [timer, setTimer] = useState(90);
  const timerRef = useRef(null);

  const notify = (msg) => {
    setError(String(msg || "Something went wrong"));
    setTimeout(() => setError(""), 6000);
  };

  // ---------------- Helper Functions ----------------
  const fetchRecommend = async (text) => {
    setLoading(true);
    try {
      console.log("🚀 Getting job recommendations...");
      const { data } = await axios.post(`${API_BASE}/recommend`, {
        resume_text: text,
      }, { timeout: 15000 }); // 15 second timeout
      console.log("📡 Recommend response:", data);
      if (data.success) {
        setParsed(data.parsed_resume || data.parsed || null);
        setJobs(data.recommendations || data.jobs || []);
        setLiveJobs(data.live_jobs || []);
        setInterviewOn(true);
        notify(`✅ Found ${(data.recommendations || data.jobs || []).length} job recommendations!`);
      } else {
        console.error("❌ Recommend failed:", data.error);
        notify(data.error || "Failed to get recommendations");
      }
    } catch (e) {
      console.error("❌ Recommend error:", e);
      notify(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const runOrSubmit = async (mode) => {
    if (!selectedProblem) return;
    try {
      const body = {
        problem_id: selectedProblem.id,
        language: codeLang,
        source_code: sourceCode,
        mode,
      };
      const { data } = await axios.post(`${API_BASE}/submissions`, body);
      if (!data.success) throw new Error(data.error || "Run failed");
      setRunResult(data);
    } catch (e) {
      notify(e.message);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    if (!resumeText.trim()) return;
    fetchRecommend(resumeText);
  };

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const form = new FormData();
    form.append("resume_file", file);
    setLoading(true);
    try {
      console.log("🚀 Starting file upload...");
      const { data } = await axios.post(`${API_BASE}/upload`, form, { 
        timeout: 30000, // 30 second timeout
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      console.log("📡 Upload response:", data);
      if (data.success) {
        setParsed(data.parsed_resume || data.parsed || null);
        setJobs(data.recommendations || data.jobs || []);
        setLiveJobs(data.live_jobs || []);
        setInterviewOn(true);
        notify("✅ File uploaded successfully!");
      } else {
        console.error("❌ Upload failed:", data.error);
        notify(data.error || "Upload failed");
      }
    } catch (e) {
      console.error("❌ Upload error:", e);
      notify(`Upload error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ---------------- Skill Extraction ----------------
  const extractJobSkills = (jobs) => {
    const allSkills = new Set();
    jobs.forEach((job) => {
      if (job.description) {
        const text = job.description.toLowerCase();
        const skillKeywords = [
          "python",
          "java",
          "javascript",
          "react",
          "angular",
          "vue",
          "node.js",
          "django",
          "flask",
          "spring",
          "sql",
          "mysql",
          "postgresql",
          "mongodb",
          "aws",
          "azure",
          "gcp",
          "docker",
          "kubernetes",
          "git",
          "jenkins",
          "machine learning",
          "ai",
          "data science",
          "agile",
        ];
        skillKeywords.forEach((skill) => {
          if (text.includes(skill)) allSkills.add(skill);
        });
      }
    });
    return Array.from(allSkills);
  };

  const jobSkills = extractJobSkills([...jobs, ...liveJobs]);

  // ---------------- Safe no-op stubs (prevents runtime errors if referenced) ----------------
  const renderProblemList = () => null;
  const renderCodeEditor = () => null;
  const renderProblemDetails = () => null;

  // ---------------- Render Main Content ----------------
  const renderJobsSection = () => (
    <div className="container">
      {/* Resume upload */}
      <div className="panel" style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Get Personalized Job Recommendations</h2>
        <form onSubmit={onSubmit} className="form-row" style={{ marginTop: 16 }}>
          <textarea
            className="textarea"
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste resume here..."
          />
          <div className="actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              Find Matches
            </button>
            <label className="btn btn-secondary" style={{ cursor: "pointer" }}>
              Upload PDF/TXT
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={onUpload}
                style={{ display: "none" }}
              />
            </label>
          </div>
        </form>
      </div>

      {/* Main Content Layout */}
      {parsed && (
        <div className="job-recommendations-layout">
          {/* Main Content */}
          <div className="main-content">
            {/* Parsed Resume */}
            <div className="panel" style={{ marginBottom: 20 }}>
              <div className="section-title">Parsed Resume</div>
              {parsed.skills && typeof parsed.skills === 'object' ? (
                // Display skills by category
                Object.entries(parsed.skills).map(([category, skillList]) => (
                  skillList && Array.isArray(skillList) && skillList.length > 0 && (
                    <div key={category} style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: 6, textTransform: 'capitalize' }}>
                        {category.replace(/_/g, ' ')}
                      </div>
                      <div className="pills">
                        {skillList.slice(0, 8).map((skill, i) => (
                          <span key={i} className="pill">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )
                ))
              ) : (
                // Fallback for array format
                <div className="pills">
                  {(Array.isArray(parsed.skills) ? parsed.skills : []).map((s, i) => (
                    <span key={i} className="pill">
                      {s}
                    </span>
                  ))}
                </div>
              )}
              
              {parsed.total_skills && (
                <div style={{ marginTop: 12, color: "#334155", fontWeight: 600 }}>
                  Total Skills Found: {parsed.total_skills}
                </div>
              )}
              
              {parsed.filename && (
                <div style={{ marginTop: 8, color: "#64748b", fontSize: '14px' }}>
                  📄 {parsed.filename}
                </div>
              )}
            </div>

            {/* Job Matches */}
            {Array.isArray(jobs) && jobs.length > 0 && (
              <div className="panel" style={{ marginBottom: 20 }}>
                <div className="section-title">Model Matches</div>
                <div className="grid">
                  {jobs.map((j, i) => (
                    <div key={i} className="card">
                      <h4>{j.title}</h4>
                      <div className="muted">
                        {j.company} • {j.location || "Remote/Hybrid"}
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <span className="badge">
                          Match {((j.similarity_score || 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Live Jobs */}
            {Array.isArray(liveJobs) && liveJobs.length > 0 && (
              <div className="panel" style={{ marginBottom: 20 }}>
                <div className="section-title">Live Jobs</div>
                <div className="grid">
                  {liveJobs.map((j, i) => (
                    <div key={i} className="card">
                      <h4>{j.title}</h4>
                      <div className="muted">
                        {j.company} • {j.location || "Remote/Hybrid"}
                      </div>
                      <div style={{ marginTop: 8 }}>
                        {j.url && (
                          <a
                            className="link"
                            href={j.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            View
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar Content */}
          <div className="sidebar-content">
            {/* Skill Gap Analysis */}
            {jobs.length > 0 && (
              <SkillGapAnalysis
                userSkills={
                  parsed.skills && typeof parsed.skills === 'object' && !Array.isArray(parsed.skills)
                    ? Object.values(parsed.skills).flat() // Flatten categorized skills
                    : Array.isArray(parsed.skills) 
                      ? parsed.skills 
                      : []
                }
                jobSkills={jobSkills}
                jobTitle={jobs[0]?.title || "Target Role"}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );

  // ---------------- Final Return ----------------
  const renderMainContent = () => {
    if (interviewOn) {
      return (
        <div className="interview-interface">
          {/* Interview interface code remains the same */}
        </div>
      );
    }

    if (!selectedProblem) {
      return (
        <div>
          <div className="page-header">
            <h1>Coding Problems</h1>
            <p>Browse problems, write code, and run against tests.</p>
          </div>
          <div className="problem-layout">
            {renderProblemList()}
            <div className="problem-details empty-state">
              <div className="empty-content">
                <h3>Welcome to Problem Solving</h3>
                <p>Select a problem from the list to get started</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="solving-layout">
        <div className="solving-header">
          <h2>Solving: {selectedProblem.title}</h2>
          <div className="problem-actions">
            <button 
              className="btn btn-secondary"
              onClick={() => setSelectedProblem(null)}
            >
              ← Back to Problems
            </button>
          </div>
        </div>
        <SplitView
          left={
            <div className="editor-container">
              {renderCodeEditor()}
            </div>
          }
          right={renderProblemDetails()}
          leftTitle="Editor"
          rightTitle="Problem Description"
        />
      </div>
    );
  };

  return (
    <div className="app">
      <NavBar title="Job Recommendations" />
      <main className="container">
        {renderJobsSection()}
        {/* Problem solving UI is available on /problems. Avoid rendering here to prevent
            undefined references causing a blank screen on the Job Recommendations page. */}
      </main>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
        </div>
      )}

      {!!error && (
        <div className="toast">
          <div>{error}</div>
          <button onClick={() => setError("")}>×</button>
        </div>
      )}
    </div>
  );
}