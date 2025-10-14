import os
import json
import logging
import asyncio

from Agents import Prompt 
from Utils.LoadUtils import LoadUtils
from typing import Dict, Optional, List, Tuple, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class GeminiLLMAgent:
    def __init__(self, model='gemini-2.0-flash', temperature=0):

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.environ['google_api_key'],
            temperature=temperature
            #, max_output_tokens=500
        )
        
        self.base_prompt_template = Prompt.RESUME_PROMPT
        self.base_customization_resume_template = Prompt.RESUME_CUSTOMIZATION

    def execute_agent(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
            Execute a call using Gemini LLM .
        
            Args:
                job_description: The job description
                resume_text: All the content of your resume
                            
            Returns:
                Dictionary with 'score' (int), 'recommendation' (str), 'ats_score (str) and 'ats_issues' (str) keys
        """
        logger.info("Starting Gemini Agent Execution")

        
        #print(f"Prompt: {enhanced_prompt}")
        try:
            enhanced_prompt = self.base_prompt_template.format(
                full_resume = resume_text,
                job_desc = job_description
            )
            #logger.warning(f"Enhanced Gemini Prompt: {enhanced_prompt}")

            response = self.llm.invoke(enhanced_prompt,
                                     response_format={"type": "json_object"}
                                       )
            #logger.warning(f"Response Gemini Agent Prompt: {response}")
            #print(type(response))
            json_response = LoadUtils.convert_to_json(response)
            logger.info(f"Scoring Values: {json_response['scoring_breakdown']}")

            return json_response 
        except Exception as e:
            print(f"Execute Gemini Agent Failure: {e}")
            return None
        
    def LLM_Resume_Customization(self, job_description: str, resume_text: str, recommendations: str, ats_recommendations: str ):
        """
            Execute an Asynchronous call using Gemini LLM to get a Resume taylor to the job description.
        
            Args:
                job_description: The job description
                resume_text: All the content of your resume
                recommendations: The recommendations from the previous LLM call
                ats_recommendations: ATS changes needed for the Resume to get a good ATS Score.
                            
            Returns:
                Updated Resume in a tring ready to be saved into a PDF.
        """
         
        enhanced_prompt = self.base_customization_resume_template.format(
            full_resume = resume_text,
            job_desc = job_description,
            recommendations = recommendations,
            ats_suggestions = ats_recommendations
        )
        logger.warning(f"Enhanced Gemini Prompt: {enhanced_prompt}")

        try:
            response = self.llm.invoke(enhanced_prompt)
            response_text = response.content
            #logger.warning(f"Enhanced Gemini Resume: {response}")

            return response_text 
        except Exception as e:
            print(f"Enhance Resume by Gemini Agent Failure: {e}")
            return None