import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

const JobPostingList = ({ onEditJob }) => {
    const { user } = useAuth();
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        job_type: '',
        experience_level: '',
        location: '',
        remote_allowed: false
    });
    const [page, setPage] = useState(1);

    const fetchJobs = async () => {
        try {
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';
            const params = new URLSearchParams({
                page: page.toString(),
                limit: '20',
                ...Object.fromEntries(
                    Object.entries(filters).filter(([_, value]) => 
                        value !== '' && value !== false
                    )
                )
            });

            console.log('🔍 Fetching jobs from:', `${API_BASE}/api/jobs?${params}`);
            
            const response = await fetch(`${API_BASE}/api/jobs?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('📡 Jobs API response status:', response.status);

            if (response.status === 401) {
                console.error('❌ 401 Unauthorized - but this endpoint should not require auth!');
                console.log('🔍 Response headers:', Object.fromEntries(response.headers.entries()));
                const errorText = await response.text();
                console.log('🔍 Error response:', errorText);
                return;
            }

            const result = await response.json();
            console.log('📊 Jobs API result:', result);

            if (result.success) {
                setJobs(result.jobs);
                console.log(`✅ Loaded ${result.jobs.length} jobs`);
            } else {
                console.error('Failed to fetch jobs:', result.message);
            }
        } catch (error) {
            console.error('Error fetching jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
    }, [filters, page]);

    const handleFilterChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
        setPage(1); // Reset to first page when filtering
    };

    const handleDeleteJob = async (jobId) => {
        if (!confirm('Are you sure you want to delete this job posting?')) {
            return;
        }

        try {
            const token = localStorage.getItem('auth_token');
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

            const response = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const result = await response.json();

            if (result.success) {
                setJobs(jobs.filter(job => job.id !== jobId));
            } else {
                alert(result.message || 'Failed to delete job posting');
            }
        } catch (error) {
            console.error('Error deleting job:', error);
            alert('Failed to delete job posting');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'No deadline';
        return new Date(dateString).toLocaleDateString();
    };

    const getJobTypeColor = (jobType) => {
        const colors = {
            'full-time': '#10b981',
            'part-time': '#f59e0b',
            'contract': '#8b5cf6',
            'internship': '#06b6d4'
        };
        return colors[jobType] || '#6b7280';
    };

    const getExperienceColor = (level) => {
        const colors = {
            'entry': '#22c55e',
            'mid': '#f59e0b',
            'senior': '#ef4444'
        };
        return colors[level] || '#6b7280';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading job postings...</p>
            </div>
        );
    }

    return (
        <div className="job-posting-list">
            <div className="filters-section">
                <div className="filters-row">
                    <input
                        type="text"
                        name="search"
                        placeholder="Search jobs, companies, or skills..."
                        value={filters.search}
                        onChange={handleFilterChange}
                        className="search-input"
                    />
                    
                    <select
                        name="job_type"
                        value={filters.job_type}
                        onChange={handleFilterChange}
                        className="filter-select"
                    >
                        <option value="">All Job Types</option>
                        <option value="full-time">Full-time</option>
                        <option value="part-time">Part-time</option>
                        <option value="contract">Contract</option>
                        <option value="internship">Internship</option>
                    </select>

                    <select
                        name="experience_level"
                        value={filters.experience_level}
                        onChange={handleFilterChange}
                        className="filter-select"
                    >
                        <option value="">All Levels</option>
                        <option value="entry">Entry Level</option>
                        <option value="mid">Mid Level</option>
                        <option value="senior">Senior Level</option>
                    </select>

                    <input
                        type="text"
                        name="location"
                        placeholder="Location"
                        value={filters.location}
                        onChange={handleFilterChange}
                        className="filter-input"
                    />
                </div>

                <div className="filters-row">
                    <label className="checkbox-filter">
                        <input
                            type="checkbox"
                            name="remote_allowed"
                            checked={filters.remote_allowed}
                            onChange={handleFilterChange}
                        />
                        Remote work allowed
                    </label>
                </div>
            </div>

            <div className="jobs-grid">
                {jobs.length === 0 ? (
                    <div className="no-jobs">
                        <h3>No job postings found</h3>
                        <p>Try adjusting your filters or check back later for new opportunities.</p>
                    </div>
                ) : (
                    jobs.map(job => (
                        <div key={job.id} className="job-card">
                            <div className="job-header">
                                <div className="job-title-section">
                                    <h3 className="job-title">{job.title}</h3>
                                    <p className="job-company">{job.company}</p>
                                </div>
                                <div className="job-badges">
                                    <span 
                                        className="job-type-badge"
                                        style={{ backgroundColor: getJobTypeColor(job.job_type) }}
                                    >
                                        {job.job_type}
                                    </span>
                                    <span 
                                        className="experience-badge"
                                        style={{ backgroundColor: getExperienceColor(job.experience_level) }}
                                    >
                                        {job.experience_level}
                                    </span>
                                </div>
                            </div>

                            <div className="job-details">
                                <div className="job-info">
                                    <span className="job-location">📍 {job.location}</span>
                                    <span className="job-salary">💰 {job.salary_range}</span>
                                    {job.remote_allowed && (
                                        <span className="remote-badge">🏠 Remote OK</span>
                                    )}
                                </div>

                                <p className="job-description">
                                    {job.description.length > 150 
                                        ? `${job.description.substring(0, 150)}...`
                                        : job.description
                                    }
                                </p>

                                {job.tags && job.tags.length > 0 && (
                                    <div className="job-tags">
                                        {job.tags.slice(0, 5).map((tag, index) => (
                                            <span key={index} className="job-tag">{tag}</span>
                                        ))}
                                        {job.tags.length > 5 && (
                                            <span className="job-tag more">+{job.tags.length - 5} more</span>
                                        )}
                                    </div>
                                )}

                                <div className="job-meta">
                                    <span className="job-posted">
                                        Posted {new Date(job.created_at).toLocaleDateString()}
                                    </span>
                                    <span className="job-deadline">
                                        Deadline: {formatDate(job.application_deadline)}
                                    </span>
                                </div>
                            </div>

                            <div className="job-actions">
                                {job.application_url && (
                                    <a 
                                        href={job.application_url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="btn-apply"
                                    >
                                        Apply Now
                                    </a>
                                )}
                                
                                {job.contact_email && (
                                    <a 
                                        href={`mailto:${job.contact_email}`}
                                        className="btn-contact"
                                    >
                                        Contact
                                    </a>
                                )}

                                {user && job.posted_by === user.id && (
                                    <div className="owner-actions">
                                        <button 
                                            onClick={() => onEditJob && onEditJob(job)}
                                            className="btn-edit"
                                        >
                                            Edit
                                        </button>
                                        <button 
                                            onClick={() => handleDeleteJob(job.id)}
                                            className="btn-delete"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>

            <style>{`
                .job-posting-list {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }

                .loading-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 60px 20px;
                    color: #6b7280;
                }

                .loading-spinner {
                    width: 40px;
                    height: 40px;
                    border: 4px solid #f3f4f6;
                    border-top: 4px solid #3b82f6;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 16px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .filters-section {
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    margin-bottom: 24px;
                }

                .filters-row {
                    display: flex;
                    gap: 16px;
                    margin-bottom: 16px;
                    flex-wrap: wrap;
                }

                .filters-row:last-child {
                    margin-bottom: 0;
                }

                .search-input,
                .filter-select,
                .filter-input {
                    padding: 10px 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 14px;
                    min-width: 200px;
                }

                .search-input {
                    flex: 1;
                    min-width: 300px;
                }

                .checkbox-filter {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 14px;
                    color: #374151;
                    cursor: pointer;
                }

                .jobs-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                    gap: 24px;
                }

                .job-card {
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .job-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }

                .job-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 16px;
                }

                .job-title {
                    font-size: 18px;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0 0 4px 0;
                }

                .job-company {
                    font-size: 14px;
                    color: #6b7280;
                    margin: 0;
                }

                .job-badges {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }

                .job-type-badge,
                .experience-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    color: white;
                    text-transform: capitalize;
                }

                .job-info {
                    display: flex;
                    gap: 16px;
                    margin-bottom: 12px;
                    font-size: 14px;
                    color: #6b7280;
                    flex-wrap: wrap;
                }

                .remote-badge {
                    background: #10b981;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                }

                .job-description {
                    color: #374151;
                    line-height: 1.6;
                    margin-bottom: 16px;
                }

                .job-tags {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 16px;
                    flex-wrap: wrap;
                }

                .job-tag {
                    background: #f3f4f6;
                    color: #374151;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }

                .job-tag.more {
                    background: #e5e7eb;
                    color: #6b7280;
                }

                .job-meta {
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: #9ca3af;
                    margin-bottom: 16px;
                }

                .job-actions {
                    display: flex;
                    gap: 12px;
                    flex-wrap: wrap;
                    align-items: center;
                }

                .btn-apply,
                .btn-contact,
                .btn-edit,
                .btn-delete {
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 600;
                    text-decoration: none;
                    border: none;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .btn-apply {
                    background: #3b82f6;
                    color: white;
                }

                .btn-apply:hover {
                    background: #2563eb;
                }

                .btn-contact {
                    background: #10b981;
                    color: white;
                }

                .btn-contact:hover {
                    background: #059669;
                }

                .owner-actions {
                    display: flex;
                    gap: 8px;
                    margin-left: auto;
                }

                .btn-edit {
                    background: #f59e0b;
                    color: white;
                }

                .btn-edit:hover {
                    background: #d97706;
                }

                .btn-delete {
                    background: #ef4444;
                    color: white;
                }

                .btn-delete:hover {
                    background: #dc2626;
                }

                .no-jobs {
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 60px 20px;
                    color: #6b7280;
                }

                .no-jobs h3 {
                    margin-bottom: 8px;
                    color: #374151;
                }

                @media (max-width: 768px) {
                    .jobs-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .job-header {
                        flex-direction: column;
                        gap: 12px;
                    }
                    
                    .filters-row {
                        flex-direction: column;
                    }
                    
                    .search-input,
                    .filter-select,
                    .filter-input {
                        min-width: unset;
                        width: 100%;
                    }
                }
            `}</style>
        </div>
    );
};

export default JobPostingList;
