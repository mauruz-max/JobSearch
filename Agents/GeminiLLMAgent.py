import os
import json
import logging

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

    def execute_agent(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
            Execute a call using Gemini LLM .
        
            Args:
                job_desc: The job description
                full_resume: All the content of your resume
                            
            Returns:
                Dictionary with 'score' (int), 'recommendation' (str), 'ats_score (str) and 'ats_issues' (str) keys
        """

        enhanced_prompt = self.base_prompt_template.format(
            full_resume = resume_text,
            job_desc = job_description
        )
        logger.warning(f"Enhanced Gemini Prompt: {enhanced_prompt}")
        #print(f"Prompt: {enhanced_prompt}")
        try:
            response = self.llm.invoke(enhanced_prompt,
                                     response_format={"type": "json_object"}
                                       )
            #print(f"Response LLM: {response}")
            #print(type(response))
            json_response = LoadUtils.convert_to_json(response)

            return json_response 
        except Exception as e:
            print(f"Execute Gemini Agent Failure: {e}")
            return None