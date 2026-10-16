# 🚀 Quick Start Guide

Get the Career Guidance Platform running in minutes!

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Option 1: Automated Setup (Recommended)

1. **Clone or download the project**
   ```bash
   # If you have git:
   git clone <repository-url>
   cd Final_pro
   
   # Or just extract the downloaded ZIP file
   ```

2. **Run the automated setup**
   ```bash
   python setup.py
   ```
   
   This will automatically:
   - Install all dependencies
   - Download the spaCy model
   - Train the job matching model
   - Test the system
   - Create configuration files

3. **Start the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to: http://localhost:5000

## Option 2: Manual Setup

If you prefer to set things up manually:

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Train the model**
   ```bash
   python train_model.py
   ```

4. **Test the system**
   ```bash
   python test_system.py
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

## 🎯 Using the Platform

1. **Open the web interface** at http://localhost:5000

2. **Paste your resume** in the text area

3. **Click "Find Job Matches"** to get personalized recommendations

4. **Review the results** - jobs are ranked by similarity score

## 🔧 Configuration (Optional)

For live job data from APIs:

1. **Get a RapidAPI key** from [RapidAPI](https://rapidapi.com)
2. **Edit the `.env` file** and add your API key
3. **Restart the application**

## 📁 Project Structure

```
Final_pro/
├── app.py                 # Main Flask application
├── resume_parser.py       # Resume parsing and skill extraction
├── job_matcher.py         # TF-IDF job matching algorithm
├── api_client.py          # Live job API integration
├── train_model.py         # Model training script
├── test_system.py         # System testing script
├── setup.py               # Automated setup script
├── requirements.txt       # Python dependencies
├── data/                  # Job dataset and trained models
│   └── job_dataset.csv   # Sample job data
├── templates/             # Web interface templates
│   └── index.html        # Main web page
└── README.md              # Detailed documentation
```

## 🚨 Troubleshooting

### Common Issues

1. **"spaCy model not found"**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **"Model not trained"**
   ```bash
   python train_model.py
   ```

3. **Import errors**
   ```bash
   pip install -r requirements.txt
   ```

4. **Port already in use**
   Change the port in `app.py` or kill the process using port 5000

### Getting Help

- Check the logs in the terminal for error messages
- Ensure all dependencies are installed correctly
- Verify Python version compatibility (3.7+)
- Check that the data directory and CSV file exist

## 🎉 Success!

Once everything is working, you should see:
- ✅ Model training completed
- ✅ All system tests passed
- ✅ Web interface accessible at http://localhost:5000
- ✅ Job recommendations working

## 🔄 Next Steps

- **Customize the job dataset** by editing `data/job_dataset.csv`
- **Add your own skills** to the resume parser
- **Integrate with other job APIs** by modifying `api_client.py`
- **Deploy to production** by configuring environment variables

---

**Need help?** Check the main README.md for detailed documentation! 