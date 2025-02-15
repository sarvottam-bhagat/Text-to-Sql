import streamlit as st
import asyncio
from database import DatabaseManager
from ai_manager import AIManager
from schema import QueryRequest, QueryResponse, DatasetInfo
import os
import pandas as pd
import time

st.set_page_config(page_title="Text to SQL Assistant", page_icon="🤖", layout="wide")

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'ai_manager' not in st.session_state:
    st.session_state.ai_manager = AIManager()
if 'current_table_info' not in st.session_state:
    st.session_state.current_table_info = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("🤖 Text to SQL Assistant")
st.markdown("""
This application helps you query your CSV data using natural language. 
Simply upload your CSV file and ask questions in plain English!
""")

# File upload section
st.subheader("1. Upload Your Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Save the uploaded file temporarily
    with open("temp.csv", "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Load the CSV into the database
    table_name = "data"  # Using a fixed table name for simplicity
    try:
        table_info = st.session_state.db_manager.load_csv("temp.csv", table_name)
        st.session_state.current_table_info = table_info
        st.success("✅ Data loaded successfully!")
        
        # Display table information in an expander
        with st.expander("View Data Preview", expanded=False):
            st.subheader("2. Data Preview")
            st.write("Table Schema:")
            schema_df = pd.DataFrame(
                [(col, dtype) for col, dtype in table_info["column_descriptions"].items()],
                columns=["Column Name", "Data Type"]
            )
            st.table(schema_df)
            
            st.write("Sample Data:")
            sample_df = pd.DataFrame(table_info["sample_data"])
            st.dataframe(sample_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists("temp.csv"):
            os.remove("temp.csv")

# Chat interface
if st.session_state.current_table_info:
    st.subheader("3. Chat with Your Data")
    
    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                if "query" in message:
                    st.code(message["query"], language="sql")
                if "results" in message:
                    results_df = pd.DataFrame(message["results"])
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                    
                    # Add download button for results with unique key
                    if len(results_df) > 0:  # Only show download button if there are results
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            "Download Results as CSV",
                            csv,
                            f"query_results_{idx}_{int(time.time())}.csv",
                            "text/csv",
                            key=f'download-csv-{idx}-{message.get("timestamp", int(time.time()))}'
                        )
    
    # Chat input
    if question := st.chat_input("Ask a question about your data..."):
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user", 
            "content": question,
            "timestamp": int(time.time())
        })
        
        with st.chat_message("user"):
            st.write(question)
        
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Generate SQL query
                    sql_query = asyncio.run(
                        st.session_state.ai_manager.generate_sql_query(
                            st.session_state.current_table_info,
                            question
                        )
                    )
                    
                    # Execute query and get results
                    results = st.session_state.db_manager.execute_query(sql_query)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "query": sql_query,
                        "results": results,
                        "timestamp": int(time.time())
                    })
                    
                    # Display current response
                    st.code(sql_query, language="sql")
                    if results:
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True, hide_index=True)
                        
                        # Add download button for results with unique key
                        if len(results_df) > 0:
                            csv = results_df.to_csv(index=False)
                            current_time = int(time.time())
                            st.download_button(
                                "Download Results as CSV",
                                csv,
                                f"query_results_{len(st.session_state.chat_history)-1}_{current_time}.csv",
                                "text/csv",
                                key=f'download-csv-current-{current_time}'
                            )
                    else:
                        st.info("No results found for your query.")
                    
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
            # Add error message to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "timestamp": int(time.time())
            })
    
    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
        
else:
    st.info("Please upload a CSV file to start querying!") 