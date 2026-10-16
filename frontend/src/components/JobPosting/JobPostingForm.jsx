import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const JobPostingForm = ({ onJobCreated, onCancel, editJob = null }) => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: editJob?.title || '',
        company: editJob?.company || '',
        description: editJob?.description || '',
        requirements: editJob?.requirements?.join('\n') || '',
        location: editJob?.location || '',
        salary_range: editJob?.salary_range || '',
        job_type: editJob?.job_type || 'full-time',
        experience_level: editJob?.experience_level || 'entry',
        contact_email: editJob?.contact_email || '',
        application_url: editJob?.application_url || '',
        tags: editJob?.tags?.join(', ') || '',
        remote_allowed: editJob?.remote_allowed || false,
        application_deadline: editJob?.application_deadline ? 
            new Date(editJob.application_deadline).toISOString().split('T')[0] : ''
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
            const jobData = {
                ...formData,
                requirements: formData.requirements.split('\n').filter(req => req.trim()),
                tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
                application_deadline: formData.application_deadline || null
            };

            const url = editJob 
                ? `${API_BASE}/api/jobs/${editJob.id}`
                : `${API_BASE}/api/jobs`;
            
            const method = editJob ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(jobData)
            });

            const result = await response.json();

            if (result.success) {
                onJobCreated && onJobCreated(result.job);
            } else {
                alert(result.message || 'Failed to save job posting');
            }
        } catch (error) {
            console.error('Error saving job:', error);
            alert('Failed to save job posting');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="job-posting-form">
            <div className="form-header">
                <h2>{editJob ? 'Edit Job Posting' : 'Post a New Job'}</h2>
                <p>Share job opportunities with the community</p>
            </div>

            <form onSubmit={handleSubmit} className="job-form">
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="title">Job Title *</label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            required
                            placeholder="e.g., Senior React Developer"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="company">Company *</label>
                        <input
                            type="text"
                            id="company"
                            name="company"
                            value={formData.company}
                            onChange={handleChange}
                            required
                            placeholder="e.g., Google, Microsoft"
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label htmlFor="description">Job Description *</label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                        rows="6"
                        placeholder="Describe the role, responsibilities, and what you're looking for..."
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="requirements">Requirements (one per line)</label>
                    <textarea
                        id="requirements"
                        name="requirements"
                        value={formData.requirements}
                        onChange={handleChange}
                        rows="4"
                        placeholder="React.js experience&#10;3+ years of JavaScript&#10;Bachelor's degree in CS"
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="location">Location *</label>
                        <input
                            type="text"
                            id="location"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            required
                            placeholder="e.g., San Francisco, CA or Remote"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="salary_range">Salary Range *</label>
                        <input
                            type="text"
                            id="salary_range"
                            name="salary_range"
                            value={formData.salary_range}
                            onChange={handleChange}
                            required
                            placeholder="e.g., $80,000 - $120,000"
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="job_type">Job Type *</label>
                        <select
                            id="job_type"
                            name="job_type"
                            value={formData.job_type}
                            onChange={handleChange}
                            required
                        >
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                            <option value="internship">Internship</option>
                        </select>
                    </div>
                    <div className="form-group">
                        <label htmlFor="experience_level">Experience Level</label>
                        <select
                            id="experience_level"
                            name="experience_level"
                            value={formData.experience_level}
                            onChange={handleChange}
                        >
                            <option value="entry">Entry Level</option>
                            <option value="mid">Mid Level</option>
                            <option value="senior">Senior Level</option>
                        </select>
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="contact_email">Contact Email</label>
                        <input
                            type="email"
                            id="contact_email"
                            name="contact_email"
                            value={formData.contact_email}
                            onChange={handleChange}
                            placeholder="hiring@company.com"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="application_url">Application URL</label>
                        <input
                            type="url"
                            id="application_url"
                            name="application_url"
                            value={formData.application_url}
                            onChange={handleChange}
                            placeholder="https://company.com/careers/job-id"
                        />
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="tags">Skills/Technologies (comma-separated)</label>
                        <input
                            type="text"
                            id="tags"
                            name="tags"
                            value={formData.tags}
                            onChange={handleChange}
                            placeholder="React, Node.js, Python, AWS"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="application_deadline">Application Deadline</label>
                        <input
                            type="date"
                            id="application_deadline"
                            name="application_deadline"
                            value={formData.application_deadline}
                            onChange={handleChange}
                        />
                    </div>
                </div>

                <div className="form-group checkbox-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="remote_allowed"
                            checked={formData.remote_allowed}
                            onChange={handleChange}
                        />
                        <span className="checkmark"></span>
                        Remote work allowed
                    </label>
                </div>

                <div className="form-actions">
                    <button type="button" onClick={onCancel} className="btn-secondary">
                        Cancel
                    </button>
                    <button type="submit" disabled={loading} className="btn-primary">
                        {loading ? 'Saving...' : (editJob ? 'Update Job' : 'Post Job')}
                    </button>
                </div>
            </form>

            <style>{`
                .job-posting-form {
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

                .job-form {
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
                    
                    .job-posting-form {
                        padding: 16px;
                        margin: 16px;
                    }
                }
            `}</style>
        </div>
    );
};

export default JobPostingForm;
