"""
Supply Chain Data Assistant
A natural language to SQL converter for Databricks Unity Catalog tables.
Supports both OpenAI and Google Gemini LLMs.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from databricks import sql


class DataAssistant:
    """Main class for the data assistant that converts natural language to SQL."""
    
    def __init__(self, llm_provider: str = None):
        """
        Initialize the DataAssistant.
        
        Args:
            llm_provider: The LLM provider to use ('openai' or 'gemini'). 
                         If None, reads from environment variable.
        """
        load_dotenv()
        
        # LLM Configuration
        self.llm_provider = llm_provider or os.getenv('LLM_PROVIDER', 'openai')
        
        # Databricks Configuration
        self.server_hostname = os.getenv('DATABRICKS_SERVER_HOSTNAME')
        self.http_path = os.getenv('DATABRICKS_HTTP_PATH')
        self.access_token = os.getenv('DATABRICKS_ACCESS_TOKEN')
        
        # Unity Catalog Configuration
        self.catalog_name = os.getenv('CATALOG_NAME')
        self.schema_name = os.getenv('SCHEMA_NAME')
        self.table_name = os.getenv('TABLE_NAME')
        
        # Initialize LLM
        self._initialize_llm()
        
        # Cache for table schema
        self._table_schema = None
    
    def _initialize_llm(self):
        """Initialize the selected LLM provider."""
        if self.llm_provider == 'openai':
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
            self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            openai.api_key = self.openai_api_key
            
        elif self.llm_provider == 'gemini':
            self.gemini_api_key = os.getenv('GEMINI_API_KEY')
            self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-pro')
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_client = genai.GenerativeModel(self.gemini_model)
            
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def get_databricks_connection(self):
        """Create and return a Databricks SQL connection."""
        if not all([self.server_hostname, self.http_path, self.access_token]):
            raise ValueError("Databricks configuration incomplete. Check environment variables.")
        
        return sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.access_token
        )
    
    def get_table_schema(self) -> str:
        """
        Retrieve the schema of the Unity Catalog table.
        
        Returns:
            A string representation of the table schema.
        """
        if self._table_schema:
            return self._table_schema
        
        full_table_name = f"{self.catalog_name}.{self.schema_name}.{self.table_name}"
        
        with self.get_databricks_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE TABLE {full_table_name}")
                columns = cursor.fetchall()
                
                schema_info = []
                for col in columns:
                    col_name = col[0]
                    col_type = col[1]
                    schema_info.append(f"  - {col_name}: {col_type}")
                
                self._table_schema = "\n".join(schema_info)
                return self._table_schema
    
    def generate_sql_prompt(self, natural_language_query: str) -> str:
        """
        Create a prompt for the LLM to convert natural language to SQL.
        
        Args:
            natural_language_query: The user's natural language question.
            
        Returns:
            The prompt string for the LLM.
        """
        table_schema = self.get_table_schema()
        full_table_name = f"{self.catalog_name}.{self.schema_name}.{self.table_name}"
        
        prompt = f"""You are a SQL expert. Convert the following natural language query into a SQL query for a Databricks Unity Catalog table.

Table: {full_table_name}

Table Schema:
{table_schema}

Natural Language Query: {natural_language_query}

Important Guidelines:
1. Generate ONLY the SQL query without any explanation or markdown formatting
2. Use the exact table name: {full_table_name}
3. Use proper SQL syntax compatible with Databricks SQL
4. Include appropriate WHERE, GROUP BY, ORDER BY, and LIMIT clauses as needed
5. Make sure column names match exactly as shown in the schema
6. Return only the SQL query, nothing else

SQL Query:"""
        
        return prompt
    
    def generate_sql_with_openai(self, prompt: str) -> str:
        """
        Generate SQL query using OpenAI API.
        
        Args:
            prompt: The prompt to send to OpenAI.
            
        Returns:
            The generated SQL query.
            
        Raises:
            ValueError: If the API call fails due to configuration or rate limits.
        """
        try:
            response = openai.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a SQL expert that converts natural language to SQL queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            sql_query = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            return sql_query
        except openai.AuthenticationError as e:
            raise ValueError(f"OpenAI authentication failed. Please check your API key: {e}")
        except openai.RateLimitError as e:
            raise ValueError(f"OpenAI rate limit exceeded. Please try again later: {e}")
        except openai.APIError as e:
            raise ValueError(f"OpenAI API error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error calling OpenAI API: {e}")
    
    def generate_sql_with_gemini(self, prompt: str) -> str:
        """
        Generate SQL query using Google Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini.
            
        Returns:
            The generated SQL query.
            
        Raises:
            ValueError: If the API call fails.
        """
        try:
            response = self.gemini_client.generate_content(prompt)
            sql_query = response.text.strip()
            # Remove markdown code blocks if present
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            return sql_query
        except Exception as e:
            # Gemini API exceptions may vary, catch broadly and provide helpful message
            raise ValueError(f"Gemini API error: {e}. Please check your API key and rate limits.")
    
    def natural_language_to_sql(self, natural_language_query: str) -> str:
        """
        Convert a natural language query to SQL using the configured LLM.
        
        Args:
            natural_language_query: The user's question in natural language.
            
        Returns:
            The generated SQL query.
        """
        prompt = self.generate_sql_prompt(natural_language_query)
        
        if self.llm_provider == 'openai':
            return self.generate_sql_with_openai(prompt)
        elif self.llm_provider == 'gemini':
            return self.generate_sql_with_gemini(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def validate_sql_query(self, sql_query: str) -> bool:
        """
        Validate SQL query for basic safety checks.
        
        Args:
            sql_query: The SQL query to validate.
            
        Returns:
            True if the query passes basic validation.
            
        Raises:
            ValueError: If the query contains suspicious patterns.
        """
        # Convert to uppercase for checking
        sql_upper = sql_query.upper()
        
        # List of dangerous SQL operations that should not be allowed
        dangerous_operations = [
            'DROP ', 'DELETE ', 'TRUNCATE ', 'INSERT ', 'UPDATE ',
            'CREATE ', 'ALTER ', 'GRANT ', 'REVOKE ', 'EXEC ',
            'EXECUTE ', '--', '/*', '*/', 'xp_', 'sp_'
        ]
        
        for operation in dangerous_operations:
            if operation in sql_upper:
                raise ValueError(
                    f"SQL query contains potentially dangerous operation: '{operation.strip()}'. "
                    f"Only SELECT queries are allowed for safety."
                )
        
        # Ensure query starts with SELECT
        if not sql_upper.strip().startswith('SELECT'):
            raise ValueError(
                "Only SELECT queries are allowed. Query must start with SELECT."
            )
        
        return True
    
    def execute_sql(self, sql_query: str) -> list:
        """
        Execute a SQL query on Databricks and return the results.
        
        Args:
            sql_query: The SQL query to execute.
            
        Returns:
            A list of dictionaries containing the query results.
            
        Raises:
            ValueError: If the query fails validation.
        """
        # Validate SQL query before execution
        self.validate_sql_query(sql_query)
        
        with self.get_databricks_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
                return [dict(zip(columns, row)) for row in results]
    
    def query(self, natural_language_query: str, execute: bool = False) -> Dict[str, Any]:
        """
        Main method to convert natural language to SQL and optionally execute it.
        
        Args:
            natural_language_query: The user's question in natural language.
            execute: Whether to execute the generated SQL query.
            
        Returns:
            A dictionary containing the SQL query and optionally the results.
        """
        sql_query = self.natural_language_to_sql(natural_language_query)
        
        result = {
            "natural_language_query": natural_language_query,
            "sql_query": sql_query
        }
        
        if execute:
            try:
                results = self.execute_sql(sql_query)
                result["results"] = results
                result["status"] = "success"
            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)
        
        return result


def main():
    """Example usage of the DataAssistant."""
    print("Supply Chain Data Assistant")
    print("=" * 50)
    
    # Initialize the assistant
    try:
        assistant = DataAssistant()
        print(f"✓ Initialized with {assistant.llm_provider.upper()} LLM provider")
        print(f"✓ Connected to table: {assistant.catalog_name}.{assistant.schema_name}.{assistant.table_name}")
    except Exception as e:
        print(f"✗ Error initializing assistant: {e}")
        return
    
    # Example queries
    example_queries = [
        "Show me the top 10 products by quantity",
        "What is the total revenue by region?",
        "Find all orders from the last 30 days"
    ]
    
    print("\nExample Queries:")
    print("-" * 50)
    
    for i, query in enumerate(example_queries, 1):
        print(f"\n{i}. Natural Language: {query}")
        try:
            result = assistant.query(query, execute=False)
            print(f"   SQL Query: {result['sql_query']}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("Interactive Mode (type 'exit' to quit)")
    print("=" * 50)
    
    while True:
        user_query = input("\nEnter your question: ").strip()
        
        if user_query.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
        
        try:
            result = assistant.query(user_query, execute=False)
            print(f"\nGenerated SQL:\n{result['sql_query']}")
            
            execute_choice = input("\nExecute this query? (y/n): ").strip().lower()
            if execute_choice == 'y':
                result = assistant.query(user_query, execute=True)
                if result['status'] == 'success':
                    print(f"\nResults: {len(result['results'])} rows returned")
                    for row in result['results'][:5]:  # Show first 5 results
                        print(row)
                    if len(result['results']) > 5:
                        print(f"... and {len(result['results']) - 5} more rows")
                else:
                    print(f"\nError executing query: {result['error']}")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
