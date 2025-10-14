# AI Agent for LinkedIn Job Search Scraper

An intelligent job search automation tool that scrapes LinkedIn job postings, analyzes them against your resume using AI, and provides personalized recommendations to help you focus on the best opportunities.

## Overview

This Python-based tool streamlines your job search by:
- Scraping job listings from LinkedIn over a specified time period
- Using an LLM agent to compare job descriptions against your resume
- Providing a qualification score for each position
- Generating tailored recommendations on whether to apply
- Automatically storing all results in Google Sheets for easy tracking
- If the score is above certain treshold then it will create a customized resume for you

## Features

- **Automated Job Scraping**: Retrieves multiple job postings from LinkedIn based on your search criteria
      You can get the Linkedin Job Scraper used for this project from here:
      **https://github.com/spinlud/py-linkedin-jobs-scraper**
- **AI-Powered Analysis**: Leverages LangChain to intelligently evaluate job fit
- **Qualification Scoring**: Get an objective score showing how well you match each position
- **Personalized Recommendations**: Receive specific advice on whether to apply and how to improve your application
- **Google Sheets Integration**: All data is automatically organized and stored for easy reference and tracking
- **Customized Resume**: Update resume with recommendations to tailor it to the job description.

## Who Is This For?

This tool is designed for job seekers who want to:
- Save time by focusing on the most relevant opportunities
- Understand how well they match job requirements
- Make data-driven decisions about where to apply
- Track their job search progress efficiently

## Prerequisites

Before you begin, ensure you have:
- Python 3.7 or higher installed
- A LinkedIn account
- Google Sheets API credentials
- An API key for your chosen LLM provider
  - Gemini
  - OpenAI
  - Claude

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/linkedin-job-scraper.git
cd linkedin-job-scraper
```
2. Install required dependencies:
```bash
pip install linkedin_jobs_scraper langchain langchain_google_genai langchain_openai langchain_core langchain_community google.oauth2 googleapiclient
```
3. Set up your configuration file with:
   - LinkedIn credentials
   - LLM API key
   - Google Sheets credentials
   - Your resume information

## Usage

1. Configure your job search parameters (location, keywords, time range, type of job, seniority, on site or remote)
2. Setup your resume in the pdf_resume path
3. Run the scraper:
```bash
python jobsearch.py
```
4. Review your results in the generated Google Sheett

## How It Works

1. **Scraping**: The tool searches LinkedIn for jobs matching your criteria within your specified timeframe
2. **Analysis**: Each job description is sent to an LLM agent along with your resume
3. **Scoring**: The AI evaluates your qualifications and assigns a compatibility score
4. **Recommendations**: You receive specific feedback on whether to apply and what to emphasize
5. **Storage**: All data is automatically saved to Google Sheets for tracking and review

## Dependencies

- `linkedin_jobs_scraper` - For scraping job listings from LinkedIn
- `langchain` - For LLM agent integration and job analysis
- `googleapiclient` - For storing and organizing results into Google Sheets
- `google.oauth2` - For Google Authentication
- `langchain_google_genai` - For Google Gemini LLM integration with LangChain
- `langchain_openai` - For OpenAI LLM integration with LangChain

## Configuration

Create a `.env` file with the following structure:
```
LI_AT_COOKIE = 
google_api_key = 
OPENAI_API_KEY = 
google_sheets_credentials = .json
spreadsheet_id = 
pdf_resume = .pdf
pdf_directory = 
```
You will need a service account for Google and export to a json file, that is what you reference in the google sheet credentials.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Please review and comply with LinkedIn's Terms of Service when using this scraper. Use responsibly and respect rate limits.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
I am not a developer, so this is my first try with Python, and I am pretty sure there are things that can be improved, so feel free to make any modifications.

Happy Job Hunting! 🎯
