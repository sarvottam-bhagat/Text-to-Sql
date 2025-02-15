import os
from typing import Dict, Any
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIManager:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.llm = GoogleGenerativeAI(model="gemini-exp-1206", temperature=0)
        
        self.sql_prompt = PromptTemplate(
            input_variables=["table_info", "question"],
            template="""You are an expert SQL query generator. Given the following table information and question, generate a SQL query that answers the question.

Table Information:
{table_info}

Question: {question}

Generate only the SQL query without any explanation, markdown formatting, or code blocks. The query should be valid SQLite syntax.
SQL Query:"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.sql_prompt)

    def format_table_info(self, table_info: Dict[str, Any]) -> str:
        """Format table information for the prompt"""
        info = f"Table name: {table_info['table_name']}\n"
        info += "Columns and their types:\n"
        for col, dtype in table_info['column_descriptions'].items():
            info += f"- {col}: {dtype}\n"
        
        info += "\nSample data:\n"
        for row in table_info['sample_data'][:3]:
            info += f"{row}\n"
        
        return info

    async def generate_sql_query(self, table_info: Dict[str, Any], question: str) -> str:
        """Generate SQL query from natural language question"""
        formatted_info = self.format_table_info(table_info)
        response = await self.chain.arun(table_info=formatted_info, question=question)
        
        # Clean the response of any markdown formatting or code blocks
        cleaned_response = response.strip()
        cleaned_response = cleaned_response.replace('```sql', '').replace('```sqlite', '').replace('```', '')
        cleaned_response = cleaned_response.strip()
        
        return cleaned_response 