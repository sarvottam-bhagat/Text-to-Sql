# Text to SQL Assistant

A simple yet powerful application that allows you to query your CSV data using natural language. The application uses Google's Gemini AI to convert your English questions into SQL queries and fetch the relevant data.

## Features

- Upload CSV files and automatically convert them to a queryable database
- Ask questions in plain English about your data
- View the generated SQL queries
- See results in a clean, tabular format
- Modern, user-friendly interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Upload your CSV file using the file uploader
2. Review the data preview and schema
3. Enter your question in plain English
4. Click "Generate Answer" to see the SQL query and results

## Example Questions

- "What is the average value of column X?"
- "How many rows are there in total?"
- "Show me the top 5 rows sorted by column Y"
- "What is the maximum value in column Z?"

## Technologies Used

- Streamlit for the web interface
- Langchain for AI orchestration
- Google Gemini for natural language processing
- SQLite for database operations
- Pydantic for data validation
- Pandas for data manipulation

## Notes

- The application currently supports CSV files only
- All data is stored temporarily and is cleared when the application restarts
- The SQL queries are optimized for SQLite syntax 