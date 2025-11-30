"""
Example usage script for the Supply Chain Data Assistant.
Demonstrates various ways to use the assistant programmatically.
"""

from data_assistant import DataAssistant
import json


def example_basic_usage():
    """Basic usage example: Generate SQL without execution."""
    print("=" * 60)
    print("Example 1: Basic Usage - Generate SQL without execution")
    print("=" * 60)
    
    # Initialize the assistant
    assistant = DataAssistant()
    
    # Example query
    natural_query = "Show me the top 10 products by quantity"
    
    # Generate SQL without executing
    result = assistant.query(natural_query, execute=False)
    
    print(f"\nNatural Language Query: {result['natural_language_query']}")
    print(f"\nGenerated SQL Query:\n{result['sql_query']}")
    print("\n")


def example_with_execution():
    """Example with query execution."""
    print("=" * 60)
    print("Example 2: Generate and Execute SQL Query")
    print("=" * 60)
    
    # Initialize the assistant
    assistant = DataAssistant()
    
    # Example query
    natural_query = "What is the total count of records?"
    
    # Generate and execute SQL
    result = assistant.query(natural_query, execute=True)
    
    print(f"\nNatural Language Query: {result['natural_language_query']}")
    print(f"\nGenerated SQL Query:\n{result['sql_query']}")
    
    if result['status'] == 'success':
        print(f"\nQuery Results:")
        print(json.dumps(result['results'], indent=2, default=str))
    else:
        print(f"\nError: {result['error']}")
    print("\n")


def example_multiple_queries():
    """Example with multiple queries."""
    print("=" * 60)
    print("Example 3: Multiple Queries")
    print("=" * 60)
    
    # Initialize the assistant
    assistant = DataAssistant()
    
    # List of example queries
    queries = [
        "Show me all records from the last 7 days",
        "What is the average value by category?",
        "Find the top 5 items with highest values",
        "Count the number of unique categories"
    ]
    
    for i, natural_query in enumerate(queries, 1):
        print(f"\n{i}. Natural Query: {natural_query}")
        result = assistant.query(natural_query, execute=False)
        print(f"   SQL Query: {result['sql_query']}")
    
    print("\n")


def example_with_error_handling():
    """Example with proper error handling."""
    print("=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    try:
        # Initialize the assistant
        assistant = DataAssistant()
        print("✓ Assistant initialized successfully")
        
        # Get table schema
        schema = assistant.get_table_schema()
        print(f"\n✓ Retrieved table schema:\n{schema}")
        
        # Generate SQL
        natural_query = "Show me summary statistics"
        result = assistant.query(natural_query, execute=False)
        print(f"\n✓ Generated SQL:\n{result['sql_query']}")
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
    
    print("\n")


def example_switching_llm_providers():
    """Example switching between LLM providers."""
    print("=" * 60)
    print("Example 5: Switching LLM Providers")
    print("=" * 60)
    
    natural_query = "Show me the first 5 records"
    
    # Try with OpenAI
    try:
        print("\nUsing OpenAI:")
        assistant_openai = DataAssistant(llm_provider='openai')
        result = assistant_openai.query(natural_query, execute=False)
        print(f"SQL: {result['sql_query']}")
    except Exception as e:
        print(f"OpenAI Error: {e}")
    
    # Try with Gemini
    try:
        print("\nUsing Gemini:")
        assistant_gemini = DataAssistant(llm_provider='gemini')
        result = assistant_gemini.query(natural_query, execute=False)
        print(f"SQL: {result['sql_query']}")
    except Exception as e:
        print(f"Gemini Error: {e}")
    
    print("\n")


def example_databricks_notebook():
    """Example for use in Databricks notebook."""
    print("=" * 60)
    print("Example 6: Databricks Notebook Usage")
    print("=" * 60)
    
    example_code = '''
# In a Databricks notebook, set up environment variables:

import os

# Using Databricks secrets (recommended)
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="my_scope", key="openai_api_key")
os.environ['DATABRICKS_SERVER_HOSTNAME'] = 'your_workspace.cloud.databricks.com'
os.environ['DATABRICKS_HTTP_PATH'] = '/sql/1.0/warehouses/your_warehouse_id'
os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="my_scope", key="databricks_token")
os.environ['CATALOG_NAME'] = 'main'
os.environ['SCHEMA_NAME'] = 'supply_chain'
os.environ['TABLE_NAME'] = 'orders'

# Install dependencies
%pip install openai google-generativeai databricks-sql-connector python-dotenv pydantic

# Import and use the assistant
from data_assistant import DataAssistant

assistant = DataAssistant()

# Generate SQL
result = assistant.query("What are the top 10 orders by value?", execute=True)

# Display results
display(result['results'])
'''
    
    print("\nExample code for Databricks notebook:")
    print(example_code)
    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Supply Chain Data Assistant Examples" + " " * 10 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    # Check if environment is configured
    try:
        assistant = DataAssistant()
        print("✓ Environment is properly configured\n")
        
        # Run examples that don't require execution
        example_basic_usage()
        example_multiple_queries()
        example_with_error_handling()
        
        # Uncomment these if you want to test execution
        # example_with_execution()
        
        # This example just shows code
        example_switching_llm_providers()
        example_databricks_notebook()
        
        print("=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Environment configuration error: {e}")
        print("\nPlease ensure your .env file is properly configured.")
        print("See .env.example for the required configuration.")


if __name__ == "__main__":
    main()
