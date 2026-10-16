import React from 'react';
import { Link } from 'react-router-dom';

const LandingPreview = () => {
  return (
    <div className="landing-preview">
      <div className="preview-header">
        <h1>🚀 Career Guidance Platform</h1>
        <p>Your AI-powered career development companion</p>
      </div>

      <div className="preview-features">
        <div className="preview-grid">
          <div className="preview-card">
            <div className="preview-icon">💼</div>
            <h3>Smart Job Matching</h3>
            <p>Upload your resume and get personalized job recommendations using advanced AI analysis.</p>
            <div className="preview-demo">
              <div className="demo-upload-area">
                <span>📄 Drop your resume here</span>
                <small>PDF, DOC, or text format</small>
              </div>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-icon">🎤</div>
            <h3>AI Interview Practice</h3>
            <p>Practice interviews with AI-generated questions and get real-time feedback on your performance.</p>
            <div className="preview-demo">
              <div className="demo-interview">
                <div className="demo-question">
                  <strong>Sample Question:</strong>
                  <p>"Tell me about a challenging project you worked on..."</p>
                </div>
                <div className="demo-controls">
                  <button className="demo-btn">🎙️ Start Recording</button>
                </div>
              </div>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-icon">💻</div>
            <h3>Coding Challenges</h3>
            <p>Solve programming problems and improve your technical skills with our curated problem set.</p>
            <div className="preview-demo">
              <div className="demo-code">
                <div className="code-header">
                  <span>Problem: Two Sum</span>
                  <span className="difficulty easy">Easy</span>
                </div>
                <div className="code-snippet">
                  <code>def two_sum(nums, target):</code>
                  <code>    # Your solution here</code>
                </div>
              </div>
            </div>
          </div>

          <div className="preview-card">
            <div className="preview-icon">📊</div>
            <h3>Skill Gap Analysis</h3>
            <p>Identify areas for improvement and get personalized learning recommendations.</p>
            <div className="preview-demo">
              <div className="demo-skills">
                <div className="skill-bar">
                  <span>JavaScript</span>
                  <div className="progress"><div className="fill" style={{width: '85%'}}></div></div>
                </div>
                <div className="skill-bar">
                  <span>React</span>
                  <div className="progress"><div className="fill" style={{width: '70%'}}></div></div>
                </div>
                <div className="skill-bar">
                  <span>Node.js</span>
                  <div className="progress"><div className="fill" style={{width: '60%'}}></div></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="preview-stats">
        <div className="stat-item">
          <div className="stat-number">10,000+</div>
          <div className="stat-label">Job Matches Made</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">5,000+</div>
          <div className="stat-label">Interviews Practiced</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">95%</div>
          <div className="stat-label">Success Rate</div>
        </div>
      </div>

      <div className="preview-cta">
        <h2>Ready to accelerate your career?</h2>
        <p>Join thousands of professionals who have advanced their careers with our platform</p>
      </div>

      <style>{`
        .landing-preview {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          font-family: 'Inter', sans-serif;
        }

        .preview-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .preview-header h1 {
          font-size: 3rem;
          font-weight: 800;
          color: #1a1a1a;
          margin-bottom: 1rem;
        }

        .preview-header p {
          font-size: 1.25rem;
          color: #666;
          margin: 0;
        }

        .preview-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
          margin-bottom: 3rem;
        }

        .preview-card {
          background: white;
          border-radius: 16px;
          padding: 2rem;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          border: 1px solid #f0f0f0;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .preview-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        }

        .preview-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .preview-card h3 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 1rem;
        }

        .preview-card p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 1.5rem;
        }

        .preview-demo {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 1rem;
          border: 1px solid #e9ecef;
        }

        .demo-upload-area {
          text-align: center;
          padding: 2rem;
          border: 2px dashed #007bff;
          border-radius: 8px;
          background: #f8f9ff;
        }

        .demo-upload-area span {
          display: block;
          font-weight: 600;
          color: #007bff;
          margin-bottom: 0.5rem;
        }

        .demo-upload-area small {
          color: #666;
        }

        .demo-question {
          margin-bottom: 1rem;
        }

        .demo-question strong {
          color: #1a1a1a;
        }

        .demo-question p {
          margin: 0.5rem 0 0 0;
          font-style: italic;
          color: #555;
        }

        .demo-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 6px;
          font-size: 0.9rem;
          cursor: pointer;
        }

        .code-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .difficulty.easy {
          background: #d4edda;
          color: #155724;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 600;
        }

        .code-snippet {
          background: #2d3748;
          color: #e2e8f0;
          padding: 1rem;
          border-radius: 6px;
          font-family: 'Monaco', 'Consolas', monospace;
          font-size: 0.9rem;
        }

        .code-snippet code {
          display: block;
          margin-bottom: 0.25rem;
        }

        .skill-bar {
          display: flex;
          align-items: center;
          margin-bottom: 0.75rem;
        }

        .skill-bar span {
          width: 80px;
          font-size: 0.9rem;
          font-weight: 600;
        }

        .progress {
          flex: 1;
          height: 8px;
          background: #e9ecef;
          border-radius: 4px;
          overflow: hidden;
          margin-left: 1rem;
        }

        .fill {
          height: 100%;
          background: linear-gradient(90deg, #007bff, #0056b3);
          transition: width 0.3s ease;
        }

        .preview-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 2rem;
          margin: 3rem 0;
          text-align: center;
        }

        .stat-item {
          padding: 1.5rem;
        }

        .stat-number {
          font-size: 2.5rem;
          font-weight: 800;
          color: #007bff;
          margin-bottom: 0.5rem;
        }

        .stat-label {
          color: #666;
          font-weight: 600;
        }

        .preview-cta {
          text-align: center;
          padding: 3rem 2rem;
          background: linear-gradient(135deg, #007bff, #0056b3);
          border-radius: 16px;
          color: white;
          margin-top: 3rem;
        }

        .preview-cta h2 {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 1rem;
        }

        .preview-cta p {
          font-size: 1.1rem;
          opacity: 0.9;
          margin: 0;
        }

        @media (max-width: 768px) {
          .preview-header h1 {
            font-size: 2rem;
          }
          
          .preview-grid {
            grid-template-columns: 1fr;
          }
          
          .preview-stats {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default LandingPreview;
