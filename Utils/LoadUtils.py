import json
import os
import pandas as pd
import re
import logging

from typing import Dict, Optional, List, Tuple

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
#from markdown_pdf import MarkdownPdf, Section
from md2pdf.core import md2pdf

logger = logging.getLogger(__name__)

class LoadUtils:
    """
    Initialize the Load Utils Manager.
    """
    # Salary keywords to search for
    salary_keywords = [
        'salary', 'compensation', 'pay', 'wage',
        '$', '€', '£', '¥', 'usd', 'eur', 'gbp',
        'k/year', 'k per year', 'k annually',
        '/year', '/yr', 'per year', 'annually',
        '/hour', '/hr', 'per hour', 'hourly',
        'base pay', 'total comp', 'cash compensation',
        'range:', 'paying', 'offered', 'Base pay:', 'Salary range',
        '100k', '150k', '200k', '160K','250K','300K'  # Common salary patterns
    ]

    # Regex patterns for salary extraction
    SALARY_PATTERNS = [
        # $100,000 - $150,000 or $100,000 to $150,000
        r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[-–to]+\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        # $100k - $150k or $100k to $150k
        r'\$\s*(\d{1,3})k\s*[-–to]+\s*\$?\s*(\d{1,3})k',
        # 100k-150k or 100-150k
        r'(\d{1,3})k?\s*[-–to]+\s*(\d{1,3})k',
        # $100,000 (single amount)
        r'\$\s*(\d{1,3}(?:,\d{3})*)',
        # 100k (single amount)
        r'(\d{1,3})k(?:\s|/|$)',
    ]

    @staticmethod
    def has_salary_info (description:str) -> bool:
        """
        Check if the job description contains salary information.
        
        Args:
            description: Job description text
            
        Returns:
            True if salary info found, False otherwise
        """

        if not description or pd.isna(description):
            return False
        
        description_lower = str(description).lower()

        # Check if any keyword exists
        return any(keyword in description_lower for keyword in LoadUtils.salary_keywords)
    
    @staticmethod
    def extract_salary_info(description: str) -> Dict[str, any]:
        """
        Extract salary information from job description.
        
        Returns:
            Dictionary containing:
                - has_salary (bool): Whether salary info was found
                - salary_text (str): The matched salary text
                - amount (tuple): Extracted numeric amounts
        """
        #print(f"Description salary info: {description}")
        if description is None or pd.isna(description) or description == '':
            return {'has_salary': False, 'salary_text': None, 'amount': None}
        
        try:
            description_str = str(description).strip()
            if not description_str:
                return {
                    'has_salary': False,
                    'salary_text': None,
                    'amount': None
                }
        except Exception:
            return {
                'has_salary': False,
                'salary_text': None,
                'amount': None
            }

        try:
            for idx, pattern in enumerate(LoadUtils.SALARY_PATTERNS):
                match = re.search(pattern, description_str, re.IGNORECASE)
                if match:
                    return {
                        'has_salary': True,
                        'salary_text': match.group(0),
                        'amount': match.groups()
                    }
            
            # Fallback to keyword search
            keyword_found = LoadUtils.has_salary_info(description)
            return {'has_salary': keyword_found, 'salary_text': None, 'amount': None}
        except Exception as e:
            print(f"extract_salary_info exception: {e}")
            return {'has_salary': False, 'salary_text': None, 'amount': None}

    @staticmethod
    def parse_salary_range(description: str) -> Optional[Tuple[float, float]]:
        """
        Parse and return salary range as numeric values.
        
        Args:
            description: Job description text
            
        Returns:
            Tuple of (min_salary, max_salary) or None if not found
        """
        salary_info = LoadUtils.extract_salary_info(description)
        
        if not salary_info['has_salary'] or not salary_info['amount']:
            return None
        
        amounts = salary_info['amount']
        
        try:
            # Convert to float, handling 'k' notation and commas
            def to_number(s):
                if not s:
                    return None
                s = s.replace(',', '').strip()
                num = float(s)
                # If it's in 'k' format (usually < 1000), multiply by 1000
                if num < 1000:
                    num *= 1000
                return num
            
            if len(amounts) >= 2:
                # Range found
                min_sal = to_number(amounts[0])
                max_sal = to_number(amounts[1])
                return (min_sal, max_sal) if min_sal and max_sal else None
            elif len(amounts) == 1:
                # Single amount
                sal = to_number(amounts[0])
                return (sal, sal) if sal else None
                
        except (ValueError, AttributeError):
            return None
        
        return None
    
    @staticmethod
    def meets_minimum_salary(description: str, min_threshold: float, 
                            check_type: str = 'any') -> bool:

        """
        Check if salary meets a minimum threshold.
        
        Args:
            description: Job description text
            min_threshold: Minimum salary threshold (e.g., 160000)
            check_type: How to check - 'min', 'max', 'avg', or 'any'
                - 'min': Minimum salary must be >= threshold
                - 'max': Maximum salary must be >= threshold
                - 'avg': Average salary must be >= threshold
                - 'any': Either min or max must be >= threshold
            
        Returns:
            True if salary meets threshold, False otherwise
        """
        salary_range = LoadUtils.parse_salary_range(description)

        if not salary_range:
            return False
        
        min_sal, max_sal = salary_range
        
        if check_type == 'min':
            return min_sal >= min_threshold
        elif check_type == 'max':
            return max_sal >= min_threshold
        elif check_type == 'avg':
            avg_sal = (min_sal + max_sal) / 2
            return avg_sal >= min_threshold
        elif check_type == 'any':
            return min_sal >= min_threshold or max_sal >= min_threshold
        else:
            return False

    @staticmethod
    def get_full_resume() -> str:
        """
            Get the full content of all pages in your Resume

            Returns:
                str: Extracted text from PDF
        """
        
        try:
            # Reload the PDF to get full page content
            loader = PyPDFLoader(os.environ['pdf_resume'])
            pages = loader.load()
            
            context_resume = ' '.join(page.page_content for page in pages) 
            context_resume = context_resume.replace('\n', ' ').replace('_', '')

            return context_resume
                
        except Exception as e:
            print(f"Error loading full page resume: {e}")
            return None
        
    @staticmethod
    def convert_to_json(input_str):
        """
            Convert String into JSON
            Args:
                input_str: String that needs to be converted to JSON
            Returns:
                str: JSON Output format
        """
        
        json_match = re.search(r'```json\n(.*?)\n```', input_str.content, re.DOTALL)

        if json_match:
            try:
                parsed_json = json.loads(json_match.group(1))
                #return parsed_json
            except Exception as e:
                    print(f"Error during LLM Output to JSON: {e}")
        
        #print(f"Result: {parsed_json}")
        return parsed_json

    @staticmethod
    def save_to_pdf(input_str, jobid: str, job_title: str ) -> bool:
        """
            Save a string into a PDF Document
            Args:
                input_str: String that needs to be converted to PDF
            Returns:
                bool: True if the PDF is created, False if it fails
        """
        pdf_file_name = os.path.join(os.environ['pdf_directory'], f"{jobid}-{job_title}.pdf")

        try:
            md2pdf(pdf_file_name, md_content=input_str)
            #pdf = MarkdownPdf()
            #pdf.meta["title"] = 'Mauricio Ruiz Resume'
            #pdf.add_section(Section(input_str, toc=False))
            #pdf.save(pdf_file_name)

            return True
        except Exception as e:
            logger.info(f"Saving to PDF Failure: {e}")
            return False
    