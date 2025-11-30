# Supply Chain Data Assistant

A natural language to SQL converter for Databricks Unity Catalog tables, powered by generative AI LLMs (OpenAI GPT or Google Gemini).

## Overview

This application allows you to interact with your Databricks Unity Catalog tables using natural language queries. Simply ask questions in plain English, and the assistant will convert them to SQL queries and optionally execute them on your Databricks cluster.

### Features

- 🤖 **Multi-LLM Support**: Works with both OpenAI GPT-4 and Google Gemini
- 🗄️ **Unity Catalog Integration**: Seamlessly connects to Databricks Unity Catalog tables
- 🔄 **Automatic Schema Detection**: Retrieves and uses table schema for accurate SQL generation
- 💬 **Interactive Mode**: Chat-based interface for iterative querying
- 🚀 **Databricks Optimized**: Designed to run on Databricks compute clusters

## Prerequisites

- Python 3.8 or higher
- Access to Databricks workspace with Unity Catalog
- API key for either OpenAI or Google Gemini
- Databricks personal access token

## Installation

### On Local Machine or Databricks Notebook

1. **Clone the repository**:
   ```bash
   git clone https://github.com/alvinjchua888/supplychaindataassistant.git
   cd supplychaindataassistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your credentials:
   ```env
   # LLM Provider Configuration
   LLM_PROVIDER=openai  # or 'gemini'
   
   # OpenAI Configuration (if using OpenAI)
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4
   
   # Gemini Configuration (if using Gemini)
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-pro
   
   # Databricks Configuration
   DATABRICKS_SERVER_HOSTNAME=your_workspace.cloud.databricks.com
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your_warehouse_id
   DATABRICKS_ACCESS_TOKEN=your_databricks_access_token
   
   # Unity Catalog Configuration
   CATALOG_NAME=your_catalog_name
   SCHEMA_NAME=your_schema_name
   TABLE_NAME=your_table_name
   ```

### On Databricks Cluster

#### Method 1: Using Databricks Notebook

1. **Upload files to Databricks**:
   - Upload `data_assistant.py` and `requirements.txt` to your Databricks workspace
   
2. **Install dependencies in a notebook cell**:
   ```python
   %pip install -r /path/to/requirements.txt
   ```

3. **Set environment variables in notebook**:
   ```python
   import os
   
   os.environ['LLM_PROVIDER'] = 'openai'
   os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="your_scope", key="openai_api_key")
   os.environ['DATABRICKS_SERVER_HOSTNAME'] = 'your_workspace.cloud.databricks.com'
   os.environ['DATABRICKS_HTTP_PATH'] = '/sql/1.0/warehouses/your_warehouse_id'
   os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="your_scope", key="databricks_token")
   os.environ['CATALOG_NAME'] = 'your_catalog'
   os.environ['SCHEMA_NAME'] = 'your_schema'
   os.environ['TABLE_NAME'] = 'your_table'
   ```

4. **Import and use the assistant**:
   ```python
   from data_assistant import DataAssistant
   
   assistant = DataAssistant()
   result = assistant.query("Show me the top 10 products by quantity")
   print(result['sql_query'])
   ```

#### Method 2: Using Databricks Job

1. **Create a library**:
   - Package the application as a wheel or egg file
   - Upload to DBFS or Unity Catalog volume

2. **Create a Databricks job**:
   - Attach the library to the job cluster
   - Use environment variables or Databricks secrets for configuration
   - Set the job to run `data_assistant.py`

## Configuration

### Getting Databricks Credentials

1. **Server Hostname**: Found in your Databricks workspace URL (e.g., `dbc-12345678-9abc.cloud.databricks.com`)

2. **HTTP Path**: 
   - Go to your SQL Warehouse in Databricks
   - Click "Connection Details"
   - Copy the HTTP Path (e.g., `/sql/1.0/warehouses/abc123def456`)

3. **Access Token**:
   - In Databricks, go to User Settings → Developer → Access Tokens
   - Generate a new token
   - Store securely (use Databricks Secrets for production)

### Using Databricks Secrets (Recommended for Production)

Instead of storing API keys in environment variables, use Databricks Secrets:

```python
import os
from databricks import sql

# Configure using Databricks secrets
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="my_scope", key="openai_api_key")
os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="my_scope", key="databricks_token")

from data_assistant import DataAssistant
assistant = DataAssistant()
```

## Usage

### Command Line Interface

Run the interactive assistant:

```bash
python data_assistant.py
```

This will start an interactive session where you can type natural language queries.

### Programmatic Usage

```python
from data_assistant import DataAssistant

# Initialize the assistant
assistant = DataAssistant()

# Generate SQL without executing
result = assistant.query("What are the top 5 suppliers by order volume?", execute=False)
print(f"Generated SQL: {result['sql_query']}")

# Generate and execute SQL
result = assistant.query("Show me all orders from last month", execute=True)
print(f"SQL: {result['sql_query']}")
print(f"Results: {result['results']}")
```

### Example Queries

Here are some example natural language queries you can try:

- "Show me the top 10 products by quantity"
- "What is the total revenue by region?"
- "Find all orders from the last 30 days"
- "Which suppliers have the highest order value?"
- "Show me the average delivery time by product category"
- "List all items that are low in stock (quantity < 100)"

### Switching Between LLM Providers

You can switch between OpenAI and Gemini by changing the `LLM_PROVIDER` environment variable:

```python
# Use OpenAI
assistant = DataAssistant(llm_provider='openai')

# Use Gemini
assistant = DataAssistant(llm_provider='gemini')
```

## Architecture

```
┌─────────────────┐
│  Natural        │
│  Language Query │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Assistant │
│  - Schema Cache │
│  - LLM Client   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌──────────┐
│ OpenAI │  │  Gemini  │
│  GPT   │  │   Pro    │
└────┬───┘  └─────┬────┘
     │            │
     └─────┬──────┘
           │
           ▼
    ┌──────────────┐
    │  SQL Query   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────────┐
    │   Databricks     │
    │  Unity Catalog   │
    └──────────────────┘
```

## Best Practices

1. **Use Databricks Secrets**: Never hardcode API keys or tokens in your code
2. **Cache Schema**: The assistant caches table schema to minimize database calls
3. **Review Generated SQL**: Always review generated SQL before executing on production data
4. **Start Simple**: Begin with simple queries and gradually increase complexity
5. **Limit Results**: Use LIMIT clauses for large tables to avoid overwhelming results
6. **Monitor Costs**: LLM API calls incur costs; monitor usage in production

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**:
   - Ensure your `.env` file is in the same directory as the script
   - Check that the API key is correctly set in the environment

2. **"Databricks configuration incomplete"**:
   - Verify all Databricks credentials are set
   - Test connection to SQL warehouse separately

3. **"Table not found"**:
   - Verify the catalog, schema, and table names are correct
   - Ensure your Databricks token has access to the Unity Catalog table

4. **SQL Generation Issues**:
   - Provide more specific queries
   - Check if the table schema is correctly retrieved
   - Try switching between OpenAI and Gemini

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from data_assistant import DataAssistant
assistant = DataAssistant()
```

## Security Considerations

- **API Keys**: Store API keys securely using Databricks Secrets or environment variables
- **Access Control**: Ensure Databricks token has appropriate permissions (least privilege)
- **SQL Injection**: The assistant uses parameterized queries where possible
- **Data Privacy**: Be cautious about sending sensitive data to external LLM APIs

## Performance

- **Schema Caching**: Table schema is cached after first retrieval
- **Connection Pooling**: Databricks connections are created per query
- **LLM Response Time**: Typically 1-3 seconds for SQL generation
- **Query Execution**: Depends on Databricks cluster and query complexity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review Databricks and LLM provider documentation

## Acknowledgments

- Built for Databricks Unity Catalog
- Powered by OpenAI GPT and Google Gemini
- Inspired by the need for accessible data analytics
