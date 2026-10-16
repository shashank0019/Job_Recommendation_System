import React, { useState } from 'react';
import NavBar from '../components/NavBar.jsx';
import InterviewExperienceList from '../components/InterviewExperience/InterviewExperienceList';
import InterviewExperienceForm from '../components/InterviewExperience/InterviewExperienceForm';

const InterviewExperiences = () => {
    const [showForm, setShowForm] = useState(false);
    const [editingExperience, setEditingExperience] = useState(null);
    const [refreshList, setRefreshList] = useState(0);

    const handleCreateExperience = () => {
        setEditingExperience(null);
        setShowForm(true);
    };

    const handleEditExperience = (experience) => {
        setEditingExperience(experience);
        setShowForm(true);
    };

    const handleExperienceSaved = (experience) => {
        setShowForm(false);
        setEditingExperience(null);
        setRefreshList(prev => prev + 1); // Trigger list refresh
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingExperience(null);
    };

    if (showForm) {
        return (
            <>
                <NavBar title="Career Guidance Platform" />
                <InterviewExperienceForm
                    editExperience={editingExperience}
                    onExperienceCreated={handleExperienceSaved}
                    onCancel={handleCancel}
                />
            </>
        );
    }

    return (
        <>
            <NavBar title="Career Guidance Platform" />
            <div className="interview-experiences-page">
                <div className="page-header">
                    <div className="header-content">
                        <div className="header-text">
                            <h1>Interview Experiences</h1>
                            <p>Learn from real interview experiences shared by the community</p>
                        </div>
                        <button onClick={handleCreateExperience} className="btn-create-experience">
                            <span className="plus-icon">+</span>
                            Share Experience
                        </button>
                    </div>
                </div>

                <InterviewExperienceList
                    key={refreshList}
                    onEditExperience={handleEditExperience}
                />

                <style>{`
                .interview-experiences-page {
                    min-height: 100vh;
                    background: #f9fafb;
                }

                .page-header {
                    background: white;
                    border-bottom: 1px solid #e5e7eb;
                    padding: 24px 0;
                }

                .header-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .header-text h1 {
                    font-size: 32px;
                    font-weight: 800;
                    color: #1f2937;
                    margin: 0 0 8px 0;
                }

                .header-text p {
                    font-size: 16px;
                    color: #6b7280;
                    margin: 0;
                }

                .btn-create-experience {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: #10b981;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .btn-create-experience:hover {
                    background: #059669;
                }

                .plus-icon {
                    font-size: 18px;
                    font-weight: bold;
                }

                @media (max-width: 768px) {
                    .header-content {
                        flex-direction: column;
                        gap: 16px;
                        text-align: center;
                    }

                    .header-text h1 {
                        font-size: 28px;
                    }
                }
            `}</style>
            </div>
        </>
    );
};

export default InterviewExperiences;
