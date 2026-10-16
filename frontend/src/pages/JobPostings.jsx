import React, { useState } from 'react';
import NavBar from '../components/NavBar.jsx';
import JobPostingList from '../components/JobPosting/JobPostingList';
import JobPostingForm from '../components/JobPosting/JobPostingForm';

const JobPostings = () => {
    const [showForm, setShowForm] = useState(false);
    const [editingJob, setEditingJob] = useState(null);
    const [refreshList, setRefreshList] = useState(0);

    const handleCreateJob = () => {
        setEditingJob(null);
        setShowForm(true);
    };

    const handleEditJob = (job) => {
        setEditingJob(job);
        setShowForm(true);
    };

    const handleJobSaved = (job) => {
        setShowForm(false);
        setEditingJob(null);
        setRefreshList(prev => prev + 1); // Trigger list refresh
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingJob(null);
    };

    if (showForm) {
        return (
            <>
                <NavBar title="Career Guidance Platform" />
                <JobPostingForm
                    editJob={editingJob}
                    onJobCreated={handleJobSaved}
                    onCancel={handleCancel}
                />
            </>
        );
    }

    return (
        <>
            <NavBar title="Career Guidance Platform" />
            <div className="job-postings-page">
                <div className="page-header">
                    <div className="header-content">
                        <div className="header-text">
                            <h1>Job Postings</h1>
                            <p>Discover opportunities and share job openings with the community</p>
                        </div>
                        <button onClick={handleCreateJob} className="btn-create-job">
                            <span className="plus-icon">+</span>
                            Post a Job
                        </button>
                    </div>
                </div>

                <JobPostingList
                    key={refreshList}
                    onEditJob={handleEditJob}
                />

                <style>{`
                .job-postings-page {
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

                .btn-create-job {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .btn-create-job:hover {
                    background: #2563eb;
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

export default JobPostings;
