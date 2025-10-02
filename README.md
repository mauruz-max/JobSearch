AI Agent for LinkedIn Job Search Scraper
An intelligent job search automation tool that scrapes LinkedIn job postings, analyzes them against your resume using AI, and provides personalized recommendations to help you focus on the best opportunities.
Overview
This Python-based tool streamlines your job search by:

Scraping job listings from LinkedIn over a specified time period
Using an LLM agent to compare job descriptions against your resume, choose your favorite from Gemini, OpenAI, Claude
Providing a qualification score for each position
Generating tailored recommendations on whether to apply
Automatically storing all results in Google Sheets for easy tracking

Features

Automated Job Scraping: Retrieves multiple job postings from LinkedIn based on your search criteria
You can get the Linkedin Job Scraper used for this project from here:
https://github.com/spinlud/py-linkedin-jobs-scraper
AI-Powered Analysis: Leverages LangChain to intelligently evaluate job fit
Qualification Scoring: Get an objective score showing how well you match each position
Personalized Recommendations: Receive specific advice on whether to apply and how to improve your application
Google Sheets Integration: All data is automatically organized and stored for easy reference and tracking

Who Is This For?
This tool is designed for job seekers who want to:

Save time by focusing on the most relevant opportunities
Understand how well they match job requirements
Make data-driven decisions about where to apply
Track their job search progress efficiently

Note: This project requires premium LinkedIn functionality for optimal performance.
Prerequisites
Before you begin, ensure you have:

Python 3.7 or higher installed
A LinkedIn account, you will need to gather the Auth cookie.
Google Sheets API credentials
An API key for your chosen LLM provider
  - Gemini
  - OpenAI
  - Claude

Installation

Clone this repository:

bashgit clone https://github.com/yourusername/linkedin-job-scraper.git
cd linkedin-job-scraper

Install required dependencies:

bashpip install linkedin_jobs_scraper langchain GoogleSheetsManager

Set up your configuration file with:

LinkedIn credentials
LLM API key
Google Sheets credentials
Your resume information



Usage

Configure your job search parameters (location, keywords, time range)
Upload or link your resume
Run the scraper:

bash python jobsearch.py

Review your results in the generated Google Sheet

How It Works

Scraping: The tool searches LinkedIn for jobs matching your criteria within your specified timeframe
Analysis: Each job description is sent to an LLM agent along with your resume
Scoring: The AI evaluates your qualifications and assigns a compatibility score
Recommendations: You receive specific feedback on whether to apply and what to emphasize
Storage: All data is automatically saved to Google Sheets for tracking and review

Dependencies

linkedin_jobs_scraper - For scraping job listings from LinkedIn
langchain - For LLM agent integration and job analysis
GoogleSheetsManager - For storing and organizing results

Configuration
Create a .env file with the following structure:
LI_AT_COOKIE = 

google_api_key = 

OPENAI_API_KEY = 

google_sheets_credentials = .json

spreadsheet_id = 

pdf_resume = .pdf

pdf_directory = 

Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
Disclaimer
This tool is for educational and personal use only. Please review and comply with LinkedIn's Terms of Service when using this scraper. Use responsibly and respect rate limits.
Support

I am not a developer, so this is my first try with Python, and I am pretty sure there are things that can be improved, so feel free to make any modifications.
If you encounter any issues or have questions, please open an issue on GitHub.

Happy Job Hunting! 🎯
