import json
import pandas as pd
import numpy as np 
import logging

# Google Sheets imports
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional

class GoogleSheetsManager:
    """
    Manager class for Google Sheets operations with record validation.
    """

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, credentials_file: str, spreadsheet_id: str, sheet_name: str = 'Sheet1'):
        """
        Initialize the Google Sheets Manager.
        
        Args:
            credentials_file: Path to service account JSON credentials file
            spreadsheet_id: The ID of the Google Spreadsheet
            sheet_name: Name of the sheet tab (default: 'Sheet1')
        """
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.service = self._authenticate(credentials_file)

    def _authenticate(self, credentials_file: str):
        """Authenticate and return Google Sheets service."""
        creds = Credentials.from_service_account_file(
            credentials_file, 
            scopes=self.SCOPES
        )
        return build('sheets', 'v4', credentials=creds)
    
    def _clean_record(self, record: List[Any]) -> List[Any]:
        """
        Clean a record by converting NaN, None, and other non-serializable values.
        
        Args:
            record: The record to clean
            
        Returns:
            Cleaned record with JSON-serializable values
        """
        cleaned = []

        try:
        
            for value in record:
                 # Check if the value is a collection type (like a list or array) first
                if isinstance(value, (list, np.ndarray, pd.Series)):
                    # If it's a collection, you might want to handle it differently.
                    # For this cleaning function, perhaps convert it to a string representation
                    # or recursively clean it. For simplicity, let's convert to string:
                    cleaned.append(str(value)) 
                
                # Handle NaN from pandas/numpy for scalar values
                elif pd.isna(value): 
                    cleaned.append('')
                
                # Handle None
                elif value is None:
                    cleaned.append('')
                
                # Convert other types to string if needed
                else:
                    cleaned.append(value)
            return cleaned
        except Exception as e:
            print(f"Clean Record Failure: {e}")
    
    def read_all_records(self) -> List[List[Any]]:
        """
        Read all records from the sheet.
        
        Returns:
            List of rows, where each row is a list of cell values
        """
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!A:Z'
        ).execute()
        
        return result.get('values', [])
    
    def record_exists(self, record: List[Any], key_columns: Optional[List[int]] = None) -> bool:
        """
        Check if a record exists in the sheet based on key columns.
        
        Args:
            record: The record to check (list of values)
            key_columns: List of column indices to use as keys (0-indexed).
                        If None, uses all columns for matching.
        
        Returns:
            True if record exists, False otherwise
        """
        existing_records = self.read_all_records()
        
        # Skip header row if it exists
        if len(existing_records) > 1:
            data_rows = existing_records[1:]
        else:
            data_rows = existing_records
        
        for row in data_rows:
            # Pad row with empty strings if shorter than record
            padded_row = row + [''] * (len(record) - len(row))
            
            if key_columns:
                # Compare only specified key columns
                match = all(
                    padded_row[i] == record[i] 
                    for i in key_columns 
                    if i < len(padded_row) and i < len(record)
                )
            else:
                # Compare all columns
                match = padded_row[:len(record)] == record
            
            if match:
                return True
        
        return False
    
    def add_record(self, record: List[Any], skip_if_exists: bool = True, 
                   key_columns: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Add a record to the sheet if it doesn't exist.
        
        Args:
            record: The record to add (list of values)
            skip_if_exists: If True, skip adding if record exists
            key_columns: List of column indices to use for existence check
        
        Returns:
            Dictionary with 'added' (bool) and 'message' (str) keys
        """
        """if skip_if_exists and self.record_exists(record, key_columns):
            return {
                'added': False,
                'message': 'Record already exists, skipped'
            }
        """
        #print(f"Record to add: {record}")
        #print(f"Record types: {[type(v) for v in record]}")

        # Clean the record - convert None to empty string and ensure JSON serializable
        cleaned_record = self._clean_record(record)
        
        # Append the record
        body = {'values': [cleaned_record]}
        try:
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f'{self.sheet_name}!A:A',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            return {
                'added': True,
                'message': f"Record added. Updated {result.get('updates', {}).get('updatedRows', 0)} rows",
                'result': result
            }
        except Exception as e:
            print(f"Failure Adding the record: {e}")
            return {
                'added': False,
                'message': 'Record insert failure'
            }
    
