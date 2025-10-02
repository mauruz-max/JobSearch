import os
import json
import logging
import openai

from Agents import Prompt 
from Utils.LoadUtils import LoadUtils
from typing import Dict, Optional, List, Tuple, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


logger = logging.getLogger(__name__)

class OpenAILLMAgent:
    def __init__(self, model='gpt-4o-mini', temperature=0):

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature
            #, max_output_tokens=500
        ).bind(
            response_format={"type": "json_object"}
        )
        
        self.base_prompt_template = Prompt.RESUME_PROMPT

    def execute_agent(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
            Execute a call using OpenAI LLM .
        
            Args:
                job_desc: The job description
                full_resume: All the content of your resume
                            
            Returns:
                Dictionary with 'score' (int), 'recommendation' (str), 'ats_score (str) and 'ats_issues' (str) keys
        """

        try:
            prompt = PromptTemplate.from_template (
                template = self.base_prompt_template,
                input_variables = ["full_resume","job_desc"]
            )

            enhanced_prompt = prompt.format(full_resume = resume_text, job_desc = job_description )
            logger.warning(f"Enhanced OpenAI Prompt: {enhanced_prompt}")

            response = self.llm.invoke(enhanced_prompt)

            # Parse the JSON response
            result = json.loads(response.content)
            return result

        except Exception as e:
            print(f"Execute OpenAI Agent Failure: {e}")
            return None