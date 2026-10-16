import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const InterviewExperienceForm = ({ onExperienceCreated, onCancel, editExperience = null }) => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        company: editExperience?.company || '',
        position: editExperience?.position || '',
        experience_text: editExperience?.experience_text || '',
        interview_type: editExperience?.interview_type || 'technical',
        difficulty_rating: editExperience?.difficulty_rating || 3,
        outcome: editExperience?.outcome || '',
        interview_date: editExperience?.interview_date ? 
            new Date(editExperience.interview_date).toISOString().split('T')[0] : '',
        location: editExperience?.location || '',
        interview_rounds: editExperience?.interview_rounds || 1,
        preparation_time: editExperience?.preparation_time || '',
        questions_asked: editExperience?.questions_asked?.join('\n') || '',
        tips: editExperience?.tips?.join('\n') || '',
        tags: editExperience?.tags?.join(', ') || '',
        anonymous: editExperience?.anonymous || false
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const token = localStorage.getItem('auth_token');
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

            // Prepare data
            const experienceData = {
                ...formData,
                difficulty_rating: parseInt(formData.difficulty_rating),
                interview_rounds: parseInt(formData.interview_rounds),
                questions_asked: formData.questions_asked.split('\n').filter(q => q.trim()),
                tips: formData.tips.split('\n').filter(tip => tip.trim()),
                tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
                interview_date: formData.interview_date || null
            };

            const url = editExperience 
                ? `${API_BASE}/api/experiences/${editExperience.id}`
                : `${API_BASE}/api/experiences`;
            
            const method = editExperience ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(experienceData)
            });

            const result = await response.json();

            if (result.success) {
                onExperienceCreated && onExperienceCreated(result.experience);
            } else {
                alert(result.message || 'Failed to save interview experience');
            }
        } catch (error) {
            console.error('Error saving experience to local storage:', error);
            alert('Failed to save interview experience');
        } finally {
            setLoading(false);
        }
    };

    const getDifficultyLabel = (rating) => {
        const labels = {
            1: 'Very Easy',
            2: 'Easy',
            3: 'Medium',
            4: 'Hard',
            5: 'Very Hard'
        };
        return labels[rating] || 'Medium';
    };

    return (
        <div className="interview-experience-form">
            <div className="form-header">
                <h2>{editExperience ? 'Edit Interview Experience' : 'Share Your Interview Experience'}</h2>
                <p>Help others by sharing your interview journey and insights</p>
            </div>

            <form onSubmit={handleSubmit} className="experience-form">
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="company">Company *</label>
                        <input
                            type="text"
                            id="company"
                            name="company"
                            value={formData.company}
                            onChange={handleChange}
                            required
                            placeholder="e.g., Google, Microsoft, Startup Inc."
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="position">Position *</label>
                        <input
                            type="text"
                            id="position"
                            name="position"
                            value={formData.position}
                            onChange={handleChange}
                            required
                            placeholder="e.g., Software Engineer, Product Manager"
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="experience_text">Interview Experience *</label>
                    <textarea
                        id="experience_text"
                        name="experience_text"
                        value={formData.experience_text}
                        onChange={handleChange}
                        required
                        rows="8"
                        placeholder="Share your detailed interview experience, what happened, how it went, what you learned..."
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="interview_type">Interview Type *</label>
                        <select
                            id="interview_type"
                            name="interview_type"
                            value={formData.interview_type}
                            onChange={handleChange}
                            required
                        >
                            <option value="technical">Technical</option>
                            <option value="hr">HR/Behavioral</option>
                            <option value="behavioral">Behavioral</option>
                            <option value="case-study">Case Study</option>
                            <option value="group">Group Discussion</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="difficulty_rating">
                            Difficulty Rating: {getDifficultyLabel(formData.difficulty_rating)}
                        </label>
                        <input
                            type="range"
                            id="difficulty_rating"
                            name="difficulty_rating"
                            min="1"
                            max="5"
                            value={formData.difficulty_rating}
                            onChange={handleChange}
                            className="difficulty-slider"
                        />
                        <div className="slider-labels">
                            <span>Very Easy</span>
                            <span>Very Hard</span>
                        </div>
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="outcome">Interview Outcome</label>
                        <select
                            id="outcome"
                            name="outcome"
                            value={formData.outcome}
                            onChange={handleChange}
                        >
                            <option value="">Select outcome</option>
                            <option value="selected">Selected</option>
                            <option value="rejected">Rejected</option>
                            <option value="pending">Pending</option>
                            <option value="withdrawn">Withdrawn</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="interview_date">Interview Date</label>
                        <input
                            type="date"
                            id="interview_date"
                            name="interview_date"
                            value={formData.interview_date}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="location">Location</label>
                        <input
                            type="text"
                            id="location"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            placeholder="e.g., Bangalore, Remote, New York"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="interview_rounds">Number of Rounds</label>
                        <input
                            type="number"
                            id="interview_rounds"
                            name="interview_rounds"
                            min="1"
                            max="10"
                            value={formData.interview_rounds}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="preparation_time">Preparation Time</label>
                    <input
                        type="text"
                        id="preparation_time"
                        name="preparation_time"
                        value={formData.preparation_time}
                        onChange={handleChange}
                        placeholder="e.g., 2 weeks, 1 month, 3 days"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="questions_asked">Questions Asked (one per line)</label>
                    <textarea
                        id="questions_asked"
                        name="questions_asked"
                        value={formData.questions_asked}
                        onChange={handleChange}
                        rows="5"
                        placeholder="What are your strengths?&#10;Explain a challenging project&#10;Why do you want to work here?"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="tips">Tips & Advice (one per line)</label>
                    <textarea
                        id="tips"
                        name="tips"
                        value={formData.tips}
                        onChange={handleChange}
                        rows="4"
                        placeholder="Practice coding problems daily&#10;Research the company thoroughly&#10;Prepare STAR format answers"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="tags">Skills/Technologies (comma-separated)</label>
                    <input
                        type="text"
                        id="tags"
                        name="tags"
                        value={formData.tags}
                        onChange={handleChange}
                        placeholder="React, Node.js, System Design, Leadership"
                    />
                </div>

                <div className="form-group checkbox-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="anonymous"
                            checked={formData.anonymous}
                            onChange={handleChange}
                        />
                        <span className="checkmark"></span>
                        Share anonymously (your name won't be displayed)
                    </label>
                </div>

                <div className="form-actions">
                    <button type="button" onClick={onCancel} className="btn-secondary">
                        Cancel
                    </button>
                    <button type="submit" disabled={loading} className="btn-primary">
                        {loading ? 'Saving...' : (editExperience ? 'Update Experience' : 'Share Experience')}
                    </button>
                </div>
            </form>

            <style>{`
                .interview-experience-form {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }

                .form-header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .form-header h2 {
                    color: #1f2937;
                    margin-bottom: 8px;
                }

                .form-header p {
                    color: #6b7280;
                    margin: 0;
                }

                .experience-form {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }

                .form-row {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }

                .form-group {
                    display: flex;
                    flex-direction: column;
                }

                .form-group label {
                    font-weight: 600;
                    color: #374151;
                    margin-bottom: 6px;
                    font-size: 14px;
                }

                .form-group input,
                .form-group textarea,
                .form-group select {
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: border-color 0.2s;
                }

                .form-group input:focus,
                .form-group textarea:focus,
                .form-group select:focus {
                    outline: none;
                    border-color: #3b82f6;
                }

                .form-group textarea {
                    resize: vertical;
                    min-height: 100px;
                }

                .difficulty-slider {
                    padding: 0 !important;
                    height: 8px;
                    background: #e5e7eb;
                    border-radius: 4px;
                    outline: none;
                    -webkit-appearance: none;
                }

                .difficulty-slider::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    appearance: none;
                    width: 20px;
                    height: 20px;
                    background: #3b82f6;
                    border-radius: 50%;
                    cursor: pointer;
                }

                .difficulty-slider::-moz-range-thumb {
                    width: 20px;
                    height: 20px;
                    background: #3b82f6;
                    border-radius: 50%;
                    cursor: pointer;
                    border: none;
                }

                .slider-labels {
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: #6b7280;
                    margin-top: 4px;
                }

                .checkbox-group {
                    flex-direction: row;
                    align-items: center;
                }

                .checkbox-label {
                    display: flex;
                    align-items: center;
                    cursor: pointer;
                    font-size: 14px;
                    color: #374151;
                }

                .checkbox-label input[type="checkbox"] {
                    margin-right: 8px;
                }

                .form-actions {
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                }

                .btn-primary,
                .btn-secondary {
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    border: none;
                }

                .btn-primary {
                    background: #3b82f6;
                    color: white;
                }

                .btn-primary:hover:not(:disabled) {
                    background: #2563eb;
                }

                .btn-primary:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                .btn-secondary {
                    background: #f3f4f6;
                    color: #374151;
                    border: 1px solid #d1d5db;
                }

                .btn-secondary:hover {
                    background: #e5e7eb;
                }

                @media (max-width: 768px) {
                    .form-row {
                        grid-template-columns: 1fr;
                    }
                    
                    .interview-experience-form {
                        padding: 16px;
                        margin: 16px;
                    }
                }
            `}</style>
        </div>
    );
};

export default InterviewExperienceForm;
