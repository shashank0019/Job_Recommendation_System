// Local storage utilities for offline functionality

// Generate unique ID
export const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9);

// Initialize sample data if not present
export const initializeSampleData = () => {
  // Initialize sample interview experiences
  const existingExperiences = localStorage.getItem('local_experiences');
  if (!existingExperiences) {
    const sampleExperiences = [
      {
        id: generateId(),
        company: "Google",
        position: "Software Engineer",
        experience_text: "The interview process was quite comprehensive. Started with a technical phone screen covering basic algorithms and data structures. The onsite had 4 rounds - 2 coding, 1 system design, and 1 behavioral. The coding questions were challenging but fair, focusing on arrays, trees, and dynamic programming. The interviewers were friendly and provided hints when needed.",
        interview_type: "technical",
        difficulty_rating: 4,
        outcome: "selected",
        interview_date: "2024-09-15",
        location: "Bangalore, India",
        interview_rounds: 4,
        preparation_time: "3 months",
        questions_asked: [
          "Implement LRU Cache",
          "Design a URL shortener",
          "Tell me about a challenging project",
          "Why Google?"
        ],
        tips: [
          "Practice system design extensively",
          "Review Google's leadership principles",
          "Practice coding on a whiteboard",
          "Prepare for behavioral questions using STAR method"
        ],
        tags: ["Java", "System Design", "Algorithms", "Data Structures"],
        anonymous: false,
        shared_by: "sample_user_1",
        created_at: new Date('2024-10-01').toISOString(),
        helpful_votes: 15,
        total_votes: 18,
        helpfulness_ratio: 0.83
      },
      {
        id: generateId(),
        company: "Microsoft",
        position: "Product Manager",
        experience_text: "Great experience overall! The process started with a recruiter call, followed by a case study presentation, and then a final round with the hiring manager and team. The case study was about improving user engagement for Teams. They really valued data-driven thinking and user empathy.",
        interview_type: "case-study",
        difficulty_rating: 3,
        outcome: "selected",
        interview_date: "2024-08-20",
        location: "Remote",
        interview_rounds: 3,
        preparation_time: "6 weeks",
        questions_asked: [
          "How would you improve Microsoft Teams?",
          "Estimate the market size for video conferencing",
          "Tell me about a product you built",
          "How do you handle conflicting priorities?"
        ],
        tips: [
          "Understand Microsoft's products deeply",
          "Practice market sizing problems",
          "Prepare customer scenarios",
          "Show analytical thinking process"
        ],
        tags: ["Product Strategy", "Market Analysis", "User Research", "Data Analysis"],
        anonymous: false,
        shared_by: "sample_user_2",
        created_at: new Date('2024-09-10').toISOString(),
        helpful_votes: 22,
        total_votes: 25,
        helpfulness_ratio: 0.88
      },
      {
        id: generateId(),
        company: "Amazon",
        position: "Software Development Engineer",
        experience_text: "Amazon's interview process was intense but well-structured. Heavy focus on their leadership principles throughout all rounds. The coding rounds covered a good mix of problems - strings, trees, graphs, and some system design concepts. Bar raiser round was particularly challenging.",
        interview_type: "technical",
        difficulty_rating: 5,
        outcome: "rejected",
        interview_date: "2024-07-25",
        location: "Seattle, USA",
        interview_rounds: 5,
        preparation_time: "4 months",
        questions_asked: [
          "Two Sum variations",
          "Design a distributed cache",
          "Tell me about a time you had to work with difficult stakeholders",
          "Describe your most challenging project"
        ],
        tips: [
          "Master Amazon's 16 leadership principles",
          "Practice behavioral questions extensively",
          "Study system design patterns",
          "Be prepared for follow-up questions on your solutions"
        ],
        tags: ["Python", "System Design", "Leadership Principles", "Distributed Systems"],
        anonymous: false,
        shared_by: "sample_user_3",
        created_at: new Date('2024-08-15').toISOString(),
        helpful_votes: 8,
        total_votes: 12,
        helpfulness_ratio: 0.67
      }
    ];
    localStorage.setItem('local_experiences', JSON.stringify(sampleExperiences));
  }

  // Initialize sample job postings
  const existingJobs = localStorage.getItem('local_jobs');
  if (!existingJobs) {
    const sampleJobs = [
      {
        id: generateId(),
        title: "Senior Software Engineer",
        company: "Tech Innovations Inc",
        location: "San Francisco, CA",
        salary: "$120,000 - $150,000",
        description: "We are looking for a Senior Software Engineer to join our growing team. You will be responsible for designing and implementing scalable web applications using modern technologies.",
        requirements: "5+ years of experience with React, Node.js, and cloud platforms. Strong problem-solving skills and experience with agile methodologies.",
        benefits: "Health insurance, 401k matching, flexible PTO, remote work options",
        employment_type: "Full-time",
        experience_level: "Senior",
        posted_date: new Date('2024-10-25').toISOString(),
        application_deadline: new Date('2024-11-25').toISOString(),
        tags: ["React", "Node.js", "AWS", "JavaScript", "Remote"],
        remote_friendly: true,
        created_by: "hr_manager_1"
      },
      {
        id: generateId(),
        title: "Product Manager",
        company: "StartupXYZ",
        location: "New York, NY",
        salary: "$90,000 - $120,000",
        description: "Join our fast-paced startup as a Product Manager. Lead cross-functional teams to deliver innovative products that solve real customer problems.",
        requirements: "3+ years of product management experience, strong analytical skills, experience with user research and data analysis.",
        benefits: "Equity package, health benefits, learning budget, flexible hours",
        employment_type: "Full-time",
        experience_level: "Mid",
        posted_date: new Date('2024-10-20').toISOString(),
        application_deadline: new Date('2024-12-01').toISOString(),
        tags: ["Product Strategy", "Analytics", "User Research", "Agile"],
        remote_friendly: false,
        created_by: "founder_1"
      },
      {
        id: generateId(),
        title: "Frontend Developer",
        company: "Digital Agency Pro",
        location: "Austin, TX",
        salary: "$70,000 - $90,000",
        description: "We're seeking a talented Frontend Developer to create amazing user experiences for our clients. Work with the latest technologies in a collaborative environment.",
        requirements: "2+ years experience with React/Vue.js, strong CSS skills, experience with responsive design and modern build tools.",
        benefits: "Health insurance, professional development budget, team outings, casual dress code",
        employment_type: "Full-time",
        experience_level: "Mid",
        posted_date: new Date('2024-10-22').toISOString(),
        application_deadline: new Date('2024-11-30').toISOString(),
        tags: ["React", "CSS", "JavaScript", "UI/UX", "Responsive Design"],
        remote_friendly: true,
        created_by: "hiring_manager_1"
      }
    ];
    localStorage.setItem('local_jobs', JSON.stringify(sampleJobs));
  }

  // Initialize sample users (for demo purposes)
  const existingUsers = localStorage.getItem('local_users');
  if (!existingUsers) {
    const sampleUsers = [
      {
        id: "sample_user_1",
        name: "Alice Johnson",
        email: "alice@example.com",
        password: "password123", // In real app, this would be hashed
        created_at: new Date('2024-01-15').toISOString()
      },
      {
        id: "sample_user_2", 
        name: "Bob Smith",
        email: "bob@example.com",
        password: "password123",
        created_at: new Date('2024-02-20').toISOString()
      },
      {
        id: "sample_user_3",
        name: "Charlie Brown", 
        email: "charlie@example.com",
        password: "password123",
        created_at: new Date('2024-03-10').toISOString()
      }
    ];
    localStorage.setItem('local_users', JSON.stringify(sampleUsers));
  }

  console.log('✅ Sample data initialized in localStorage');
};

// Clear all local storage data
export const clearAllLocalData = () => {
  const keys = ['local_experiences', 'local_jobs', 'local_users', 'local_problems', 'user_votes', 'auth_token', 'user_data'];
  keys.forEach(key => localStorage.removeItem(key));
  console.log('🗑️ All local data cleared');
};

// Export data for backup
export const exportLocalData = () => {
  const data = {
    experiences: JSON.parse(localStorage.getItem('local_experiences') || '[]'),
    jobs: JSON.parse(localStorage.getItem('local_jobs') || '[]'),
    users: JSON.parse(localStorage.getItem('local_users') || '[]'),
    problems: JSON.parse(localStorage.getItem('local_problems') || '[]'),
    votes: JSON.parse(localStorage.getItem('user_votes') || '{}')
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `career-platform-backup-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  console.log('📁 Local data exported');
};

// Import data from backup
export const importLocalData = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        
        if (data.experiences) localStorage.setItem('local_experiences', JSON.stringify(data.experiences));
        if (data.jobs) localStorage.setItem('local_jobs', JSON.stringify(data.jobs));
        if (data.users) localStorage.setItem('local_users', JSON.stringify(data.users));
        if (data.problems) localStorage.setItem('local_problems', JSON.stringify(data.problems));
        if (data.votes) localStorage.setItem('user_votes', JSON.stringify(data.votes));
        
        console.log('📁 Local data imported successfully');
        resolve(data);
      } catch (error) {
        console.error('Failed to import data:', error);
        reject(error);
      }
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
};