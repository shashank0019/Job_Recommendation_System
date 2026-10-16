import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';

const InterviewExperienceList = ({ onEditExperience }) => {
    const { user } = useAuth();
    const [experiences, setExperiences] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        interview_type: '',
        difficulty: '',
        company: '',
        outcome: ''
    });
    const [page, setPage] = useState(1);

    const fetchExperiences = async () => {
        try {
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';
            const params = new URLSearchParams({
                page: page.toString(),
                limit: '20',
                ...Object.fromEntries(
                    Object.entries(filters).filter(([_, value]) => value !== '')
                )
            });

            const response = await fetch(`${API_BASE}/api/experiences?${params}`);
            const result = await response.json();

            if (result.success) {
                setExperiences(result.experiences || []);
            } else {
                console.error('Failed to fetch experiences:', result.message);
                setExperiences([]);
            }
        } catch (error) {
            console.error('Error fetching experiences:', error);
            setExperiences([]);
        } finally {
            setLoading(false);
        }
    };    useEffect(() => {
        fetchExperiences();
    }, [filters, page]);

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
        setPage(1); // Reset to first page when filtering
    };

    const deleteExperience = async (experienceId) => {
        if (!window.confirm('Are you sure you want to delete this experience?')) {
            return;
        }

        try {
            const token = localStorage.getItem('auth_token');
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

            const response = await fetch(`${API_BASE}/api/experiences/${experienceId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const result = await response.json();

            if (result.success) {
                // Remove from UI immediately
                setExperiences(experiences.filter(exp => exp.id !== experienceId));
                alert('Interview experience deleted successfully');
            } else {
                alert(result.message || 'Failed to delete interview experience');
            }
        } catch (error) {
            console.error('Error deleting experience:', error);
            alert('Failed to delete interview experience');
        }
    };

    const handleVote = async (experienceId, isHelpful) => {
        try {
            const token = localStorage.getItem('auth_token');
            const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

            const response = await fetch(`${API_BASE}/api/experiences/${experienceId}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ is_helpful: isHelpful })
            });

            const result = await response.json();

            if (result.success) {
                // Update the experience in the list
                setExperiences(experiences.map(exp => 
                    exp.id === experienceId 
                        ? { 
                            ...exp, 
                            helpful_votes: result.helpful_votes,
                            total_votes: result.total_votes,
                            helpfulness_ratio: result.helpfulness_ratio
                          }
                        : exp
                ));
            } else {
                alert(result.message || 'Failed to record vote');
            }
        } catch (error) {
            console.error('Error voting:', error);
            alert('Failed to record vote');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Date not specified';
        return new Date(dateString).toLocaleDateString();
    };

    const getDifficultyColor = (rating) => {
        const colors = {
            1: '#22c55e', // green
            2: '#84cc16', // lime
            3: '#f59e0b', // amber
            4: '#f97316', // orange
            5: '#ef4444'  // red
        };
        return colors[rating] || '#6b7280';
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

    const getOutcomeColor = (outcome) => {
        const colors = {
            'selected': '#10b981',
            'rejected': '#ef4444',
            'pending': '#f59e0b',
            'withdrawn': '#6b7280'
        };
        return colors[outcome] || '#6b7280';
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Loading interview experiences...</p>
            </div>
        );
    }

    return (
        <div className="interview-experience-list">
            <div className="filters-section">
                <div className="filters-row">
                    <input
                        type="text"
                        name="search"
                        placeholder="Search experiences, companies, or skills..."
                        value={filters.search}
                        onChange={handleFilterChange}
                        className="search-input"
                    />
                    
                    <select
                        name="interview_type"
                        value={filters.interview_type}
                        onChange={handleFilterChange}
                        className="filter-select"
                    >
                        <option value="">All Interview Types</option>
                        <option value="technical">Technical</option>
                        <option value="hr">HR/Behavioral</option>
                        <option value="behavioral">Behavioral</option>
                        <option value="case-study">Case Study</option>
                        <option value="group">Group Discussion</option>
                    </select>

                    <select
                        name="difficulty"
                        value={filters.difficulty}
                        onChange={handleFilterChange}
                        className="filter-select"
                    >
                        <option value="">All Difficulties</option>
                        <option value="1">Very Easy</option>
                        <option value="2">Easy</option>
                        <option value="3">Medium</option>
                        <option value="4">Hard</option>
                        <option value="5">Very Hard</option>
                    </select>

                    <input
                        type="text"
                        name="company"
                        placeholder="Company"
                        value={filters.company}
                        onChange={handleFilterChange}
                        className="filter-input"
                    />

                    <select
                        name="outcome"
                        value={filters.outcome}
                        onChange={handleFilterChange}
                        className="filter-select"
                    >
                        <option value="">All Outcomes</option>
                        <option value="selected">Selected</option>
                        <option value="rejected">Rejected</option>
                        <option value="pending">Pending</option>
                        <option value="withdrawn">Withdrawn</option>
                    </select>
                </div>
            </div>

            <div className="experiences-grid">
                {experiences.length === 0 ? (
                    <div className="no-experiences">
                        <h3>No interview experiences found</h3>
                        <p>Try adjusting your filters or be the first to share an experience!</p>
                    </div>
                ) : (
                    experiences.map(experience => (
                        <div key={experience.id} className="experience-card">
                            <div className="experience-header">
                                <div className="experience-title-section">
                                    <h3 className="experience-title">{experience.position}</h3>
                                    <p className="experience-company">{experience.company}</p>
                                </div>
                                <div className="experience-badges">
                                    <span className="interview-type-badge">
                                        {experience.interview_type}
                                    </span>
                                    <span 
                                        className="difficulty-badge"
                                        style={{ backgroundColor: getDifficultyColor(experience.difficulty_rating) }}
                                    >
                                        {getDifficultyLabel(experience.difficulty_rating)}
                                    </span>
                                    {experience.outcome && (
                                        <span 
                                            className="outcome-badge"
                                            style={{ backgroundColor: getOutcomeColor(experience.outcome) }}
                                        >
                                            {experience.outcome}
                                        </span>
                                    )}
                                </div>
                            </div>

                            <div className="experience-details">
                                <div className="experience-info">
                                    {experience.location && (
                                        <span className="experience-location">📍 {experience.location}</span>
                                    )}
                                    <span className="experience-rounds">
                                        🔄 {experience.interview_rounds} round{experience.interview_rounds > 1 ? 's' : ''}
                                    </span>
                                    {experience.preparation_time && (
                                        <span className="preparation-time">⏱️ {experience.preparation_time}</span>
                                    )}
                                </div>

                <p className="experience-text">
                    {experience.experience_text && experience.experience_text.length > 200 
                        ? `${experience.experience_text.substring(0, 200)}...`
                        : experience.experience_text || 'No experience text available'
                    }
                </p>

                {experience.questions_asked && Array.isArray(experience.questions_asked) && experience.questions_asked.length > 0 && (
                    <div className="questions-section">
                        <h4>Questions Asked:</h4>
                        <ul className="questions-list">
                            {experience.questions_asked.slice(0, 3).map((question, index) => (
                                <li key={index}>{question}</li>
                            ))}
                                            {experience.questions_asked.length > 3 && (
                                                <li className="more-questions">
                                                    +{experience.questions_asked.length - 3} more questions
                                                </li>
                                            )}
                                        </ul>
                                    </div>
                                )}

                {experience.tips && Array.isArray(experience.tips) && experience.tips.length > 0 && (
                    <div className="tips-section">
                        <h4>Tips & Advice:</h4>
                        <ul className="tips-list">
                            {experience.tips.slice(0, 2).map((tip, index) => (
                                <li key={index}>{tip}</li>
                            ))}
                            {experience.tips.length > 2 && (
                                <li className="more-tips">
                                    +{experience.tips.length - 2} more tips
                                </li>
                            )}
                        </ul>
                    </div>
                )}

                {experience.tags && Array.isArray(experience.tags) && experience.tags.length > 0 && (
                    <div className="experience-tags">
                        {experience.tags.slice(0, 5).map((tag, index) => (
                            <span key={index} className="experience-tag">{tag}</span>
                        ))}
                        {experience.tags.length > 5 && (
                            <span className="experience-tag more">+{experience.tags.length - 5} more</span>
                        )}
                    </div>
                )}

                                <div className="experience-meta">
                                    <span className="experience-posted">
                                        {experience.anonymous ? 'Anonymous' : `Shared by ${experience.shared_by || 'User'}`}
                                    </span>
                                    <span className="experience-date">
                                        Interview: {formatDate(experience.interview_date)}
                                    </span>
                                </div>
                            </div>

                            <div className="experience-actions">
                                <div className="voting-section">
                                    <button 
                                        onClick={() => handleVote(experience.id, true)}
                                        className="vote-btn helpful"
                                        title="Mark as helpful"
                                    >
                                        👍 {experience.helpful_votes || 0}
                                    </button>
                                    <button 
                                        onClick={() => handleVote(experience.id, false)}
                                        className="vote-btn not-helpful"
                                        title="Mark as not helpful"
                                    >
                                        👎 {(experience.total_votes || 0) - (experience.helpful_votes || 0)}
                                    </button>
                                    <span className="helpfulness-ratio">
                                        {experience.total_votes > 0 
                                            ? `${Math.round((experience.helpfulness_ratio || 0) * 100)}% helpful`
                                            : 'No votes yet'
                                        }
                                    </span>
                                </div>

                                {user && !experience.anonymous && experience.shared_by && (
                                    experience.shared_by === user.id || 
                                    experience.shared_by === user._id || 
                                    experience.shared_by === String(user.id) || 
                                    experience.shared_by === String(user._id)
                                ) && (
                                    <div className="owner-actions">
                                        <button 
                                            onClick={() => onEditExperience && onEditExperience(experience)}
                                            className="btn-edit"
                                        >
                                            Edit
                                        </button>
                                        <button 
                                            onClick={() => deleteExperience(experience.id)}
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
                .interview-experience-list {
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
                    flex-wrap: wrap;
                }

                .search-input,
                .filter-select,
                .filter-input {
                    padding: 10px 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 14px;
                    min-width: 150px;
                }

                .search-input {
                    flex: 1;
                    min-width: 300px;
                }

                .experiences-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
                    gap: 24px;
                }

                .experience-card {
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .experience-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }

                .experience-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 16px;
                }

                .experience-title {
                    font-size: 18px;
                    font-weight: 700;
                    color: #1f2937;
                    margin: 0 0 4px 0;
                }

                .experience-company {
                    font-size: 14px;
                    color: #6b7280;
                    margin: 0;
                }

                .experience-badges {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }

                .interview-type-badge,
                .difficulty-badge,
                .outcome-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    color: white;
                    text-transform: capitalize;
                }

                .interview-type-badge {
                    background: #8b5cf6;
                }

                .experience-info {
                    display: flex;
                    gap: 16px;
                    margin-bottom: 12px;
                    font-size: 14px;
                    color: #6b7280;
                    flex-wrap: wrap;
                }

                .experience-text {
                    color: #374151;
                    line-height: 1.6;
                    margin-bottom: 16px;
                }

                .questions-section,
                .tips-section {
                    margin-bottom: 16px;
                }

                .questions-section h4,
                .tips-section h4 {
                    font-size: 14px;
                    font-weight: 600;
                    color: #374151;
                    margin: 0 0 8px 0;
                }

                .questions-list,
                .tips-list {
                    margin: 0;
                    padding-left: 20px;
                    color: #6b7280;
                    font-size: 14px;
                }

                .questions-list li,
                .tips-list li {
                    margin-bottom: 4px;
                }

                .more-questions,
                .more-tips {
                    color: #9ca3af;
                    font-style: italic;
                }

                .experience-tags {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 16px;
                    flex-wrap: wrap;
                }

                .experience-tag {
                    background: #f3f4f6;
                    color: #374151;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 500;
                }

                .experience-tag.more {
                    background: #e5e7eb;
                    color: #6b7280;
                }

                .experience-meta {
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: #9ca3af;
                    margin-bottom: 16px;
                }

                .experience-actions {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 12px;
                }

                .voting-section {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .vote-btn {
                    background: #f3f4f6;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.2s;
                }

                .vote-btn:hover {
                    background: #e5e7eb;
                }

                .helpfulness-ratio {
                    font-size: 12px;
                    color: #6b7280;
                }

                .owner-actions {
                    display: flex;
                    gap: 8px;
                }

                .btn-edit,
                .btn-delete {
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: 600;
                    border: none;
                    cursor: pointer;
                    transition: all 0.2s;
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

                .no-experiences {
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 60px 20px;
                    color: #6b7280;
                }

                .no-experiences h3 {
                    margin-bottom: 8px;
                    color: #374151;
                }

                @media (max-width: 768px) {
                    .experiences-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .experience-header {
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
                    
                    .experience-actions {
                        flex-direction: column;
                        align-items: stretch;
                    }
                }
            `}</style>
        </div>
    );
};

export default InterviewExperienceList;
