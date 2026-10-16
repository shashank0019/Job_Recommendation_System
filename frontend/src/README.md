# Career Guidance Platform - Project Report

## Project Information

**Institution:** Visvesvaraya Technological University (VTU), Belagavi  
**College:** Cambridge Institute of Technology, Bangalore  
**Department:** Information Science and Engineering  
**Semester:** VI  
**Academic Year:** 2024-2025  
**Report Type:** Phase-1 Project Report

---

## Project Team

| Name | USN | Role |
|------|-----|------|
| Veeresha | 1CD22IS178 | Team Member |
| Shridhar S P | 1CD22IS158 | Team Member |
| Shashank C A | 1CD22IS156 | Team Member |
| Dhananjaya D | 1CD23IS401 | Team Member |

**Project Guide:** Ms. Mamatha S, Assistant Professor, Dept. of ISE  
**Project Coordinator:** Dr. Priyanka Desai, Prof., Dept. of ISE  
**Head of Department:** Dr. Preethi S, Prof. & HOD, Dept. of ISE  

---

## Abstract

Choosing a career path is a critical yet often overwhelming decision for students and early professionals, especially without structured guidance. Traditional counseling methods lack scalability, personalization, and real-time feedback. 

This project introduces an **AI-powered career guidance platform** that uses advanced machine learning models like **Random Forest** and **BERT**, along with **NLP techniques**, to provide:

- **Personalized career recommendations**
- **Mock interview simulations** using DeepFace and Whisper for facial and speech analysis
- **Continuous support** through a multilingual GPT-based chatbot integrated with vector search (RAG)

Built with a modular architecture using **React.js, Flask, and MongoDB**, the platform delivers real-time, intelligent feedback and aligns with Sustainable Development Goals such as Quality Education and Decent Work.

**Key Features:**
- User progress tracking and skill development adaptation
- Personalized career roadmaps tailored to user interests
- User-friendly, device-responsive interface
- Scalable for institutions and customizable for individual users
- Data-driven decision support for confident career planning

---

## Table of Contents

1. [Introduction](#chapter-1-introduction)
2. [Literature Survey](#chapter-2-literature-survey)
3. [System Analysis](#chapter-3-system-analysis)
4. [Modeling](#chapter-4-modeling)
5. [References](#references)

---

## Chapter 1: Introduction

### 1.1 Overview

Career planning is a crucial phase in every student's and professional's journey. With the rapid evolution of technology, Artificial Intelligence (AI) can now deliver personalized, data-driven career guidance.

This project aims to build an **AI-powered web platform** that provides:
- Career recommendations
- Mock interview evaluations
- Chatbot-based mentorship
- Career roadmaps

This empowers users to make informed career choices and track their progress effectively.

### 1.2 Relevance of Project

The relevance of this project lies in its ability to **bridge the widening gap between academic learning and employability**. 

**Key Points:**
- More students graduate into diverse career markets but remain unaware of specific skills, roles, and industries suited to their potential
- Traditional counseling methods are resource-heavy and inconsistent
- This platform offers a scalable, automated, and highly accurate approach to career guidance
- Integrates real-time analytics and interactive AI tools to support lifelong learning and career transitions

### 1.3 Problem Statement

Despite access to a vast amount of career-related content, students and job seekers lack personalized support in interpreting it effectively. There is a noticeable absence of structured, technology-driven career guidance in most educational institutions.

**The proposed system aims to address this gap by:**
- Using machine learning and AI to analyze user data (educational background, skills, personal interests)
- Delivering real-time recommendations
- Providing mock interview evaluation
- Offering multilingual support
- Generating personalized career roadmaps

### 1.4 Objectives

- Build an AI system to recommend suitable career paths based on user profile
- Develop a mock interview analysis module using facial emotion and sentiment analysis
- Enable an intelligent career chatbot using GPT-based NLP models
- Visualize career guidance via personalized roadmap charts and dashboards
- Provide multi-language support and accessibility for diverse users
- Incorporate user profile tracking to continuously refine recommendations
- Offer institution-ready features for career management support
- Design a scalable architecture for deployment across universities and online platforms

### 1.5 Methodology

The system will be developed using a **modular, full-stack architecture** with:

**Frontend:**
- React.js and Tailwind CSS for an intuitive and responsive user interface

**Backend:**
- Python (Flask or FastAPI) to handle API requests and model integration

**Database:**
- MongoDB to store user data, profile inputs, feedback, and session details

**AI/ML Models:**
- Career prediction using Random Forest
- Mock Interview analysis via DeepFace and Whisper for multimodal input processing
- Multilingual chatbot built on GPT-3.5 integrated with a vector database using RAG

**Hosting:**
- Platforms like Render, Firebase, or Railway for cloud deployment

**Development Process:**
The methodology involves data collection, preprocessing, model training and integration, UI development, and real-time testing with iterative feedback.

---

## Chapter 2: Literature Survey

### 2.1 Introduction

This chapter explores existing literature relevant to AI-powered career guidance systems. It highlights the research and development in using machine learning, natural language processing, and other AI techniques to provide personalized and effective career support.

The reviewed works demonstrate the potential of AI to address the limitations of traditional career counseling by offering scalable, data-driven, and real-time guidance.

### 2.2 Related Works

**1. An Intelligent Career Guidance System using Machine Learning (Vignesh et al., 2021)**
- Proposes a machine learning-based system using classification algorithms
- Provides personalized career recommendations
- Addresses the confusion students face in choosing career paths after secondary education

**2. Envisioning Tomorrow: AI-Powered Career Counseling (Anushka, 2023)**
- Developed a modular AI system offering career recommendations
- Chat-based guidance with user-friendly interface
- Focuses on using AI to analyze student skills
- Provides tailored career advice

**3. Machine Learning-based Intelligent Career Counselling Chatbot (ICCC) (Goyal et al., 2023)**
- Introduces an AI chatbot utilizing NLP for career support
- Provides contextual conversation handling
- Answers student queries and promotes learning
- Guides students in selecting professional paths

---

## Chapter 3: System Analysis

### 3.1 Existing System

In the existing system, students often rely on:
- Manual counseling methods
- Generic online portals that fail to provide real-time, personalized career guidance
- Systems that lack AI integration and scalability
- Interactive guidance that is not responsive

**Limitations:**
- Not interactive or adaptive
- Fails to provide real-time, personalized career guidance
- Guidance is mostly based on predefined courses
- Lacks dynamic evaluation based on individual's skills, interests, and behavioral data
- Limited use of analytics or feedback mechanisms
- Mock interviews or skill evaluation features are either absent or handled superficially

### 3.2 Proposed System

The proposed system introduces an **AI-powered web platform** that bridges the gap between academic achievement and employability through a **modular and scalable solution**.

**Key Components:**

**Machine Learning Models:**
- Random Forest, SVM, and AdaBoost for generating personalized career recommendations
- Based on inputs: academic records, extracurricular activities, user interests

**Real-Time Features:**
- Mock interview analysis using DeepFace and Whisper
- Sentiment and speech assessment capabilities

**AI Support:**
- Multilingual GPT-based chatbot
- Vector search RAG system
- Dynamic dashboards
- Interactive roadmaps

**Additional Features:**
- User feedback loops
- Mobile accessibility
- Institution-ready integration

### 3.3 Hardware Requirements

| Component | Specification |
|-----------|---------------|
| **Processor** | Intel i5/i7 or AMD Ryzen equivalent |
| **RAM** | Minimum 8 GB (16 GB recommended) |
| **Storage** | 256 GB SSD or more |
| **GPU** | NVIDIA GTX/RTX 4GB+ (Optional for local model training) |
| **Input Devices** | Microphone and Webcam (for mock interview analysis) |
| **Internet Connection** | Minimum 5 Mbps (for video analysis and real-time response) |

### 3.4 Software Requirements

| Category | Tools/Technologies |
|----------|-------------------|
| **OS** | Windows 10/11, Ubuntu 20.04+, macOS Monterey+ |
| **IDE/Tools** | Visual Studio Code, Jupyter Notebook, Postman |
| **Frontend** | React.js, Tailwind CSS |
| **Backend** | Flask or FastAPI (Python) |
| **Database** | MongoDB Atlas |
| **Hosting Platforms** | Firebase, Render, Railway |
| **APIs** | DeepFace, Whisper (local or pretrained), GPT (open-source models for chatbot) |
| **Other Tools** | Git, GitHub, Docker, Figma (for UI Design) |

### 3.5 Libraries Description

**scikit-learn**
- Used for model training and evaluation (Random Forest, SVM, AdaBoost)
- Provides simple and efficient tools for predictive data analysis
- Built on NumPy, SciPy, and matplotlib

**Hugging Face Transformers**
- Deploy pre-trained language models like BERT and GPT
- Used for chatbots, resume parsing, and contextual question-answering modules

**DeepFace**
- Facial recognition and analysis library for Python
- Detects facial emotions during mock interviews
- Supports multiple backend models (VGG-Face, Facenet)

**Whisper**
- Speech recognition system by OpenAI
- Converts spoken responses into text during interviews
- Supports multiple languages

**Pandas & NumPy**
- Core libraries for data preprocessing, manipulation, and numerical computation
- Processes datasets collected from users

**Matplotlib & Seaborn**
- Visualization libraries for interactive graphs and charts
- Displays user progress and dashboard analytics

**Flask**
- Lightweight Python web framework
- Builds RESTful APIs for integrating frontend with backend models

**MongoEngine/PyMongo**
- Python drivers and ORM-like tools for MongoDB
- Manages data operations including user profiles and interaction history

**LangChain**
- Framework to orchestrate LLMs with external tools and vector databases
- Builds advanced Retrieval-Augmented Generation (RAG) pipelines

**OpenCV**
- Real-time video capture and preprocessing in mock interview module
- Supports face detection before analysis

**SpeechRecognition**
- Alternative to Whisper for lightweight speech-to-text conversion
- Used if cloud models are unavailable

---

## Chapter 4: Modeling

### 4.1 Purpose

The purpose of this project is to design and implement an **AI-powered career guidance platform** that delivers personalized, data-driven insights to students and job seekers.

**Key Goals:**
- Replace traditional, one-size-fits-all career counseling with scalable, real-time, and interactive guidance
- Enhance career decision-making through smart recommendations
- Improve interview preparedness with mock interview analysis
- Support ongoing skill development through chatbot support

By leveraging machine learning models and natural language processing, the platform bridges the gap between education and employability.

### 4.2 Levels of Software Design

**High-Level Design (HLD)**
- Defines the system's architecture
- Separates components: frontend (React.js), backend (Flask), database (MongoDB), and AI/ML modules (career recommendation engine, mock interview evaluator, chatbot)

**Mid-Level Design (MLD)**
- Specifies the design of individual functional modules
- Details how user profile data is processed
- Explains how predictions are triggered
- Describes how APIs connect modules (e.g., chatbot to database)

**Low-Level Design (LLD)**
- Details the internal logic of components
- Includes algorithms, database schemas, function-level flowcharts, and model integration logic
- Supports the implementation phase with precise structural blueprints

### 4.3 Scope

The project is aimed at:

**Students**
- Career path suggestions tailored to interests and strengths
- Performance tracking
- Interview practice tools

**Job Seekers**
- Better preparation through AI-driven feedback
- Emotional intelligence evaluation
- Skill-based guidance

**Institutions**
- Scalable platform supporting hundreds of students
- Centralized monitoring and analytics tools

**Future Enhancements**
- Internship integration
- Resume scoring
- Real-time mentor chat
- University data linking
- Expanded multilingual support

### 4.4 System Architecture

The platform consists of the following layers:

#### **1. Input Layer**
- **Camera:** Captures facial expressions during mock interviews
- **Microphone:** Captures spoken responses

#### **2. Frontend Interface (React.js)**
- **User Dashboard:** Main interface for input, viewing recommendations, and tracking progress
- **Chat UI:** Interactive chat interface for career-related questions

#### **3. Backend Layer (Flask/Node.js)**
Acts as the central controller:
- Receives inputs from the UI
- Routes them to appropriate AI modules
- Collects results for visualization on dashboard

#### **4. AI Modules**

**Facial Emotion Analyzer**
- Processes video input from camera using DeepFace
- Detects emotions: stress, confidence, engagement during mock interviews

**Speech-to-Text**
- Converts microphone input to text using Whisper or SpeechRecognition
- Enables sentiment or content analysis

**Career Recommendation Engine**
- Processes user profile data (skills, interests, education)
- Uses ML models (Random Forest, SVM) to suggest career paths

**GPT-3.5 Chatbot**
- Uses large language models to answer questions
- Combined with vector search (RAG) for contextual, multilingual guidance

#### **5. Data Management**
- **MongoDB:** Stores user data, interaction history, mock interview results, and career recommendations
- **ChromaDB / FAISS:** Vector databases for fast similarity search powering chatbot context understanding

#### **6. Output**
- **Feedback Dashboard:** Presents processed results visually
- Displays emotion scores, recommendation results, progress charts, and interaction logs

### 4.5 Methodology (Workflow)

**1. User Input Collection**
Gathers data directly from users through forms or dashboards:
- Skills, interests, educational background
- Resume data or spoken responses during mock interviews
- Career-related queries via chatbot

**2. Data Preprocessing**
Raw input data is cleaned and transformed:
- Handles missing values
- Standardizes formats
- Extracts relevant features (keywords from text, sentiment from audio)
- Ensures quality and consistency

**3. Model Training**
Machine learning models are trained using curated and preprocessed datasets:
- Random Forest for career recommendations
- DeepFace + Whisper for interview evaluation
- GPT-based chatbot for career Q&A
- Training performed offline or during initial platform setup

**4. Model Inference**
Trained models make predictions on new user data:
- Predicts top 3 careers for a user
- Evaluates facial expressions during interview
- Generates personalized recommendations in real-time

**5. Result Generation**
Results from inference are formatted and organized:
- Scores, rankings, and interpretations
- Career suggestions with confidence levels
- Feedback reports
- Results stored and sent to frontend for display

**6. Feedback Visualization**
Final output shown to user via interactive dashboards and charts:
- View progress
- Understand recommendations
- Reattempt interviews or explore other options
- Feedback loop refines future recommendations based on interaction history

### 4.6 Sequence Diagram

**Key Actors:**

**1. User**
Individual interacting with the AI-Powered Career Guidance Platform (student, job seeker, or anyone seeking career advice)

**2. Create Profile**
Initial step setting up account and providing essential information:
- Inputting skills (e.g., Python, Machine Learning, Communication)
- Adding education background (degree, university, GPA)
- Stating interests (e.g., AI, data science, marketing, creative arts)
- Crucial for building intelligent user profile for personalized recommendations

**3. Get Career Recommendation**
User requests career recommendations after creating profile:
- Career Recommendation Engine (AI/ML) uses models like Random Forest or BERT
- Takes user profile data as input
- Outputs suitable career paths with confidence scores and visual roadmap

**4. Take Mock Interview**
User practices interview skills with AI-driven feedback:
- Activates user's camera and microphone
- DeepFace/OpenCV assesses non-verbal cues via facial emotion analysis
- Whisper/Wav2Vec2 transcribes spoken answers to text
- Sentiment analysis (VADER/BERT) evaluates tone and content

**5. Receive Performance Feedback**
Detailed feedback provided immediately after mock interview:
- Confidence score
- Communication rating
- Expression trend based on facial and sentiment analysis
- Users understand strengths and weaknesses
- Supports interview performance improvement

**6. Ask Career Questions (Chatbot)**
Users interact with AI chatbot for specific queries:
- Career Chatbot based on GPT-3.5/LangChain + RAG
- Provides conversational AI support
- Answers FAQs, gives job suggestions, explains concepts
- Offers general career advice
- Provides continuous, interactive mentorship experience

---

## References

[1] S. Vignesh, C. Shivani Priyanka, H. Shree Manju, and K. Mythili, "An Intelligent Career Guidance System using Machine Learning," 2021.

[2] Anushka, "Envisioning Tomorrow: AI Powered Career Counseling," GitHub: AI-Powered-Counseling Project, 2023.

[3] R. Goyal, N. Chaudhary, and M. Singh, "Machine Learning based Intelligent Career Counselling Chatbot (ICCC)," 2023.

[4] H. Zhang, A. Jolfaei, and M. Alazab, "A Face Emotion Recognition Method Using Convolutional Neural Network and Image Edge Computing."

[5] T. Song, W. Zheng, C. Lu, Y. Yuanzong, X. Zhang, and Z. Cui, "MPED: A Multi-Modal Physiological Emotion Database for Discrete Emotion Recognition," IEEE Access, vol. 7, pp. 12177–12191, 2019.

[6] E. Batbaatar, M. Li, and K. H. Ryu, "Semantic-Emotion Neural Network for Emotion Recognition from Text," IEEE Access, vol. 7, pp. 111866–111878, 2019.

[7] M. A. Alimam, H. Seghiouer, and Y. Elyusufi, "Building profiles based on ontology for career recommendation in E-learning context," in 2014 International Conference on Multimedia Computing and Systems (ICMCS), Marrakech, Morocco, 2014, pp. 558-562, doi: 10.1109/ICMCS.2014.6911346.

[8] S. Angra and S. Ahuja, "Machine learning and its applications: A review," in 2017 International Conference on Big Data Analytics and Computational Intelligence (ICBDAC), Chirala, Andhra Pradesh, India, 2017, pp. 57-60, doi: 10.1109/ICBDACI.2017.8070809.

[9] M. Sharma, A. Kumari, and Jyotsna, "AI-Based Deep Learning Chatbot for Career and Personal Mentorship," in 2023 IEEE 3rd International Conference on Technology, Engineering, Management for Societal impact using Marketing, Entrepreneurship and Talent (TEMSMET), Mysuru, India, 2023, pp. 1-6, doi: 10.1109/TEMSMET56707.2023.10149907.

[10] M. Zafar, "Career Guidance in Career Planning among Secondary School Students," Asian Journal of Education and Social Studies, vol. 5, no. 1, pp. 30133, Jul. 2019, doi: 10.9734/ajess/2019/v5i130133.

[11] D. Mokashi, D. Rahude, D. Fegade, V. Dhembre, M. Shinde, and B. Bodkhe, "Career Prediction System using Big Data and Data Mining Techniques," International Research Journal of Engineering and Technology (IRJET), vol. 8, no. 3, pp. 2453-2457, Mar. 2021.

---

## Certification

This project has been successfully completed and approved by Cambridge Institute of Technology, Department of Information Science and Engineering, in partial fulfillment of the requirements for VI semester Bachelor of Engineering in Information Science and Engineering of Visvesvaraya Technological University, Belagavi, during the academic year 2024-2025.

**Academic Year:** 2025-2026  
**Department:** Information Science and Engineering  
**College:** Cambridge Institute of Technology, Bangalore