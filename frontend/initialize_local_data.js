// Initialize local storage with sample data for testing
// Run this in browser console: copy and paste the contents of this file

const sampleExperiences = [
    {
        id: "1",
        company: "Google",
        position: "Software Engineer",
        experience_text: "Had a great interview experience at Google. The process was well structured with multiple rounds including coding, system design, and behavioral interviews. The interviewers were friendly and encouraging. They asked me to solve problems step by step and explain my thought process clearly.",
        interview_type: "technical",
        difficulty_rating: 4,
        outcome: "selected",
        interview_date: "2024-10-15",
        location: "Mountain View, CA",
        interview_rounds: 5,
        preparation_time: "3 months",
        questions_asked: [
            "Implement a LRU Cache",
            "Design a URL shortener",
            "Tell me about a time you faced a technical challenge",
            "Why Google?"
        ],
        tips: [
            "Practice coding problems on LeetCode daily",
            "Study system design fundamentals",
            "Research Google's culture and values",
            "Practice explaining your thought process out loud"
        ],
        tags: ["Python", "System Design", "Data Structures", "Algorithms"],
        anonymous: false,
        created_at: "2024-10-16T10:30:00Z",
        updated_at: "2024-10-16T10:30:00Z",
        shared_by: "user123",
        helpful_votes: 15,
        total_votes: 18,
        helpfulness_ratio: 0.83
    },
    {
        id: "2",
        company: "Microsoft",
        position: "Product Manager",
        experience_text: "The Microsoft interview process was comprehensive and well-organized. They focused heavily on product thinking, customer empathy, and technical understanding. The case study round was particularly challenging but rewarding.",
        interview_type: "case-study",
        difficulty_rating: 3,
        outcome: "pending",
        interview_date: "2024-10-20",
        location: "Seattle, WA",
        interview_rounds: 4,
        preparation_time: "6 weeks",
        questions_asked: [
            "How would you improve Microsoft Teams?",
            "Design a product for small businesses",
            "Prioritize features for a new app",
            "How do you handle conflicting stakeholder requirements?"
        ],
        tips: [
            "Understand Microsoft's product ecosystem",
            "Practice case study frameworks",
            "Show customer empathy in answers",
            "Prepare technical PM questions"
        ],
        tags: ["Product Management", "Strategy", "Analytics", "Customer Research"],
        anonymous: false,
        created_at: "2024-10-21T14:20:00Z",
        updated_at: "2024-10-21T14:20:00Z",
        shared_by: "user456",
        helpful_votes: 8,
        total_votes: 10,
        helpfulness_ratio: 0.8
    },
    {
        id: "3",
        company: "Amazon",
        position: "Data Scientist",
        experience_text: "Amazon's interview process was intense but fair. They really emphasize their leadership principles throughout the process. The technical rounds covered statistics, machine learning, and coding. The behavioral questions were deeply focused on leadership principles.",
        interview_type: "technical",
        difficulty_rating: 4,
        outcome: "rejected",
        interview_date: "2024-09-28",
        location: "Remote",
        interview_rounds: 6,
        preparation_time: "2 months",
        questions_asked: [
            "Explain A/B testing methodology",
            "Code a recommendation system",
            "Tell me about a time you had to innovate",
            "How would you handle disagreement with your manager?"
        ],
        tips: [
            "Study Amazon's leadership principles thoroughly",
            "Practice SQL and Python coding",
            "Prepare STAR format examples",
            "Understand statistics and ML concepts deeply"
        ],
        tags: ["Machine Learning", "Statistics", "Python", "SQL", "A/B Testing"],
        anonymous: true,
        created_at: "2024-09-29T09:15:00Z",
        updated_at: "2024-09-29T09:15:00Z",
        shared_by: "anonymous",
        helpful_votes: 12,
        total_votes: 16,
        helpfulness_ratio: 0.75
    },
    {
        id: "4",
        company: "Startup XYZ",
        position: "Full Stack Developer",
        experience_text: "Great experience interviewing at a fast-growing startup. The process was more relaxed and focused on practical skills. They gave me a take-home project which I really enjoyed working on. The team was very collaborative during the interview.",
        interview_type: "technical",
        difficulty_rating: 2,
        outcome: "selected",
        interview_date: "2024-10-25",
        location: "San Francisco, CA",
        interview_rounds: 3,
        preparation_time: "1 week",
        questions_asked: [
            "Build a simple web application",
            "Explain your approach to debugging",
            "How do you stay updated with technology?",
            "What interests you about startups?"
        ],
        tips: [
            "Be ready to show practical coding skills",
            "Demonstrate problem-solving approach",
            "Show enthusiasm for the startup environment",
            "Ask good questions about the company"
        ],
        tags: ["React", "Node.js", "JavaScript", "MongoDB", "REST APIs"],
        anonymous: false,
        created_at: "2024-10-26T16:45:00Z",
        updated_at: "2024-10-26T16:45:00Z",
        shared_by: "user789",
        helpful_votes: 5,
        total_votes: 6,
        helpfulness_ratio: 0.83
    }
];

// Initialize local storage
console.log('Initializing local storage with sample interview experiences...');
localStorage.setItem('interview_experiences', JSON.stringify(sampleExperiences));
console.log('✅ Sample data added to local storage!');
console.log('You can now refresh your React app to see the sample interview experiences.');

// Verify the data was saved
const saved = localStorage.getItem('interview_experiences');
if (saved) {
    const parsed = JSON.parse(saved);
    console.log(`📊 Total experiences saved: ${parsed.length}`);
    parsed.forEach((exp, index) => {
        console.log(`${index + 1}. ${exp.company} - ${exp.position} (${exp.outcome})`);
    });
} else {
    console.error('❌ Failed to save data to local storage');
}