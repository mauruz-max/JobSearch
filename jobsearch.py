import logging
import os
import pandas as pd
import traceback
import sys
import asyncio

from Sheets.GoogleSheetsManager import GoogleSheetsManager
from Utils.LoadUtils import LoadUtils
from dotenv import load_dotenv
from datetime import datetime

# Loading Agents
from Agents.GeminiLLMAgent import GeminiLLMAgent
from Agents.OpenAILLMAgent import OpenAILLMAgent
from Agents.ClaudeLLMAgent import ClaudeLLMAgent

# Load environment variables from .env file
load_dotenv()

# Loading job scraper classes
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, OnSiteOrRemoteFilters, SalaryBaseFilters

# Generate a timestamped filename for the log file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f"./Logs/app_log_{timestamp}.log"

if __name__ == '__main__':

    # Configure the logging module
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,  # Set the minimum logging level
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get a logger instance
    logger = logging.getLogger(__name__)

    # Initialize the Google Sheets manager
    manager = GoogleSheetsManager(
        credentials_file=os.environ['google_sheets_credentials'],
        spreadsheet_id=os.environ['spreadsheet_id'],
        sheet_name='Jobs'
    )

full_resume = LoadUtils.get_full_resume()

# Fired once for each successfully processed job
def on_data(data: EventData):
    #print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link, data.insights,
    #      len(data.description))
    job_postings.append([data.job_id, data.location, data.title, data.company,data.place, data.date, data.date_text,
        data.link, data.apply_link, data.insights, data.description, data.skills])

# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))

def on_error(error):
    print('[ON_ERROR]', error)

def on_end():
    print('[ON_END]')

scraper = LinkedinScraper(
    chrome_executable_path=f"C:\chromedriver-win64\chromedriver.exe",  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_binary_location=f"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Custom path to Chrome/Chromium binary (e.g. /foo/bar/chrome-mac/Chromium.app/Contents/MacOS/Chromium)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=0.5,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=240  # Page load timeout (in seconds)    
)

# Creating all Agents
GeminiAgent = GeminiLLMAgent()
OpenAIAgent = OpenAILLMAgent()
ClaudeAgent = ClaudeLLMAgent()

run_open_ai = False # Set to false if you do not want to run OpenAI LLM
run_claude_ai = False # Set to false if you do not want to run Anthropic Claude LLM

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='Product Manager',
        options=QueryOptions(
            locations=['United States'],
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            page_offset=0,  # How many pages to skip
            limit=150,
            filters=QueryFilters(
                #company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.DAY,
                #type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                type=TypeFilters.FULL_TIME,
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE]
                #experience=[ExperienceLevelFilters.MID_SENIOR],
                #base_salary=SalaryBaseFilters.SALARY_160K
            )
        )
    ),
]

existing_records = manager.read_all_records()

# Skip header row if it exists
data_rows = existing_records[1:] if len(existing_records) > 1 else []

job_postings = []
scraper.run(queries)
df = pd.DataFrame(job_postings, columns=['Job_ID','Location','Title', 'Company','Place','Date', 'Date_Text','Link','Apply_Link','Inisghts', 'Description', 'Skills'])
logger.info("Using Scraper")
#df = pd.read_csv("./jobs.csv")
#logger.info("Using CSV")

#df.to_csv("jobs.csv")

# Create a set of existing URLs for O(1) lookup (index 7 is the URL)
#existing_urls = {row[7] for row in data_rows if len(row) > 7}
#It is better to check for duplicates using the job_id
existing_ids = {row[0] for row in data_rows if len(row) > 0}

for idx, item in df.iterrows():
    try:
        record_pd = item.tolist()
        description = record_pd[10] if len(record_pd) > 10 else ''
        # Get a logger instance
        logger.info(f"Title: {record_pd[2]} ")
        logger.info(f"Company: {record_pd[3]} ")
        logger.info(f"Len of record_pd: {len(record_pd)}")
        
        #logger.debug(f"Description Variable: {description} ")
        
        #logger.debug(f"PD Values: {record_pd} ")
        

        # Extra safety: ensure it's a string
        if not isinstance(description, str):
            description = str(description) if description else ''
        
        salary_info = LoadUtils.extract_salary_info(description)
        #print(f"description: {salary_info}")
        logger.info(f"Has Salary : {salary_info['has_salary']} ")
        logger.info(f"Has Salary : {salary_info['salary_text']} ")
        logger.info(f"Has Salary : {salary_info['amount']} ")

        if salary_info['has_salary']:
            has_salary = True
            
            if salary_info['salary_text'] is None:
                Salary_in_Threshold = True
            else:
                Salary_in_Threshold = LoadUtils.meets_minimum_salary(description,160000,'any')
            """
            if salary_info['salary_text']:
                
                print(f"💰 Salary found: {salary_info['salary_text']} and Salary Amount: {salary_info['amount']}")
                print(f"Range: {LoadUtils.parse_salary_range(description)}")
            else:
                print(f"💰 Salary keywords detected")
            """
        else:
            has_salary = False
            Salary_in_Threshold = True
            #print(f"⊘ No salary info")

        logger.info(f"Has Salary in Threshold: {Salary_in_Threshold} ")
        # Check if URL already exists (index 8)
        #url = record_pd[8] if len(record_pd) > 8 else None
        # Check if ID exist
        record_pd_job_id = record_pd[0] if len(record_pd) > 0 else None

        if Salary_in_Threshold:
            if record_pd_job_id in existing_ids:
                print(f"Value exists: {record_pd[3]}")
                logger.info(f"Job already in Google Sheets ")
            else:
                print(f"Record does not exist:x {record_pd[3]}")
                logger.info(f"Job will be added to Google Sheets ")
                
                llm_response = GeminiAgent.execute_agent(description, full_resume)
                
                logger.info(f"Gemini LLM responses: ")
                
                recommendations = llm_response['improvement_recommendations']
                formatted_list = '\n'.join([
                    f"• [{rec['priority']}] {rec['category']}: {rec['recommendation']}, before: {rec['example_before']} , after: {rec['example_after']} " 
                    for rec in recommendations
                ])
                
                logger.info(f"Score: {llm_response['overall_score']} ")
                logger.info(f"Recommendations: {formatted_list} ")
                logger.info(f"ATS Score: {llm_response['ats_compatibility']['score']} ")
                logger.info(f"ATS Issues: {llm_response['ats_compatibility']['issues']} ")

                if llm_response['overall_score'] >= 80:
                    llm_customization_resume_response = GeminiAgent.LLM_Resume_Customization(description, full_resume, formatted_list, llm_response['ats_compatibility']['issues'])
                    logger.warning(f"Gemini LLM responses for Resume Customization:  {llm_customization_resume_response}")

                    if llm_customization_resume_response is not None:
                        resume_writing_response = LoadUtils.save_to_pdf(llm_customization_resume_response, record_pd[0], record_pd[2])
                        if resume_writing_response:
                            print(f"Saving Custimized Resume correctly.")

                record_pd.append(salary_info['salary_text'])
                record_pd.append(llm_response['overall_score'])
                record_pd.append(formatted_list)
                record_pd.append(llm_response['ats_compatibility']['score'])
                record_pd.append(llm_response['ats_compatibility']['issues'])

                if run_open_ai:
                    OpenAIllm_response = OpenAIAgent.execute_agent(description, full_resume)

                    logger.info(f"OpenAI LLM responses: ")
                
                    OpenAIrecommendations = OpenAIllm_response['improvement_recommendations']
                    OpenAIformatted_list = '\n'.join([
                        f"• [{OAIrec['priority']}] {OAIrec['category']}: {OAIrec['recommendation']}" 
                        for OAIrec in OpenAIrecommendations
                    ])
                    
                    logger.info(f"Open AI Score: {OpenAIllm_response['overall_score']} ")
                    logger.info(f"Open AI Recommendations: {OpenAIformatted_list} ")
                    logger.info(f"Open AI ATS Score: {OpenAIllm_response['ats_compatibility']['score']} ")
                    logger.info(f"Open AI ATS Issues: {OpenAIllm_response['ats_compatibility']['issues']} ")

                    record_pd.append(OpenAIllm_response['overall_score'])
                    record_pd.append(OpenAIformatted_list)
                    record_pd.append(OpenAIllm_response['ats_compatibility']['score'])
                    record_pd.append(OpenAIllm_response['ats_compatibility']['issues'])

                if run_claude_ai:
                    Claudellm_response = ClaudeAgent.execute_agent(description, full_resume)

                    logger.info(f"Claude LLM responses: ")
                
                    Clauderecommendations = Claudellm_response['improvement_recommendations']
                    Claudeformatted_list = '\n'.join([
                        f"• [{CLrec['priority']}] {CLrec['category']}: {CLrec['recommendation']}" 
                        for CLrec in Clauderecommendations
                    ])
                    
                    logger.info(f"Open AI Score: {Claudellm_response['overall_score']} ")
                    logger.info(f"Open AI Recommendations: {Claudeformatted_list} ")
                    logger.info(f"Open AI ATS Score: {Claudellm_response['ats_compatibility']['score']} ")
                    logger.info(f"Open AI ATS Issues: {Claudellm_response['ats_compatibility']['issues']} ")

                    record_pd.append(Claudellm_response['overall_score'])
                    record_pd.append(Claudeformatted_list)
                    record_pd.append(Claudellm_response['ats_compatibility']['score'])
                    record_pd.append(Claudellm_response['ats_compatibility']['issues'])

                #print(f"Record: {record_pd}")
                result = manager.add_record(record_pd,key_columns=[8])
                
                if result['added']:
                    existing_ids.add(record_pd_job_id)
        else:
            logger.info(f"Skipping Record, salary : {record_pd[2]} , Salary Info Low: {salary_info['salary_text']}")

    except Exception as e:
        print(f"Error in Jobs Search: {e}")
        break