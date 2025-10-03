import os
import json
import logging

from Agents import Prompt 
from Utils.LoadUtils import LoadUtils
from typing import Dict, Optional, List, Tuple, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class ClaudeLLMAgent:
    def __init__(self, model='claude-3-haiku-20240307', temperature=0):
        self.llm = ChatAnthropic(
            model=model,
            temperature=temperature
            #, max_output_tokens=500
        )
        
        self.base_prompt_template = Prompt.RESUME_PROMPT

    def execute_agent(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """
            Execute a call using Claude LLM .
        
            Args:
                job_desc: The job description
                full_resume: All the content of your resume
                            
            Returns:
                Dictionary with 'score' (int), 'recommendation' (str), 'ats_score (str) and 'ats_issues' (str) keys
        """

        try:
            prompt = PromptTemplate.from_template (
                template = self.base_prompt_template
                #, input_variables = ["full_resume","job_desc"]
            )

            enhanced_prompt = prompt.format(full_resume = resume_text, job_desc = job_description )
            logger.warning(f"Enhanced Claude Prompt: {enhanced_prompt}")

            response = self.llm.invoke(enhanced_prompt)

            # Parse the JSON response
            result = json.loads(response.content)
            return result

        except Exception as e:
            print(f"Execute Claude Agent Failure: {e}")
            return None
