# Databricks Deployment Guide

This guide provides detailed instructions for deploying and running the Supply Chain Data Assistant on Databricks compute.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: Databricks Notebook](#method-1-databricks-notebook)
3. [Method 2: Databricks Job](#method-2-databricks-job)
4. [Method 3: Databricks App](#method-3-databricks-app)
5. [Configuration Best Practices](#configuration-best-practices)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Access

- Databricks workspace access
- SQL Warehouse with Unity Catalog enabled
- Permission to create and manage Databricks Secrets
- Permission to read from Unity Catalog tables

### Required API Keys

- OpenAI API key (if using OpenAI) OR Google Gemini API key (if using Gemini)
- Databricks personal access token

## Method 1: Databricks Notebook

This is the quickest method for getting started and ideal for interactive exploration.

### Step 1: Create a Databricks Notebook

1. In your Databricks workspace, create a new Python notebook
2. Name it `Supply_Chain_Data_Assistant`

### Step 2: Upload Application Files

Option A: Upload via Workspace UI
1. Upload `data_assistant.py` to your workspace
2. Note the path (e.g., `/Workspace/Users/your_email@company.com/data_assistant.py`)

Option B: Use Git integration
1. Link your Databricks workspace to this Git repository
2. Clone the repository into your workspace

### Step 3: Install Dependencies

In the first cell of your notebook:

```python
%pip install openai google-generativeai databricks-sql-connector python-dotenv pydantic typing-extensions
```

### Step 4: Configure Secrets

#### Create Databricks Secret Scope

Run this in a notebook cell (one-time setup):

```python
# This creates a secret scope (only needs to be done once)
# Note: You may need to use Databricks CLI for this
# databricks secrets create-scope --scope my_secrets
```

Or use the Databricks CLI:

```bash
databricks secrets create-scope --scope supply_chain_assistant
databricks secrets put --scope supply_chain_assistant --key openai_api_key
databricks secrets put --scope supply_chain_assistant --key databricks_token
```

#### Set Environment Variables

In a notebook cell:

```python
import os

# LLM Configuration
os.environ['LLM_PROVIDER'] = 'openai'  # or 'gemini'

# OpenAI Configuration (if using OpenAI)
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="supply_chain_assistant", key="openai_api_key")
os.environ['OPENAI_MODEL'] = 'gpt-4'

# OR Gemini Configuration (if using Gemini)
# os.environ['GEMINI_API_KEY'] = dbutils.secrets.get(scope="supply_chain_assistant", key="gemini_api_key")
# os.environ['GEMINI_MODEL'] = 'gemini-pro'

# Databricks Configuration
os.environ['DATABRICKS_SERVER_HOSTNAME'] = 'your_workspace.cloud.databricks.com'
os.environ['DATABRICKS_HTTP_PATH'] = '/sql/1.0/warehouses/your_warehouse_id'
os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="supply_chain_assistant", key="databricks_token")

# Unity Catalog Configuration
os.environ['CATALOG_NAME'] = 'main'
os.environ['SCHEMA_NAME'] = 'supply_chain'
os.environ['TABLE_NAME'] = 'orders'
```

### Step 5: Import and Use

```python
# Import the assistant
import sys
sys.path.append('/Workspace/Users/your_email@company.com/')  # Adjust path as needed
from data_assistant import DataAssistant

# Initialize
assistant = DataAssistant()

# Use it
result = assistant.query("Show me the top 10 products by quantity", execute=True)
display(result['results'])
```

### Complete Notebook Example

```python
# Cell 1: Install dependencies
%pip install openai google-generativeai databricks-sql-connector python-dotenv pydantic typing-extensions

# Cell 2: Configure environment
import os

os.environ['LLM_PROVIDER'] = 'openai'
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="supply_chain_assistant", key="openai_api_key")
os.environ['OPENAI_MODEL'] = 'gpt-4'
os.environ['DATABRICKS_SERVER_HOSTNAME'] = 'your_workspace.cloud.databricks.com'
os.environ['DATABRICKS_HTTP_PATH'] = '/sql/1.0/warehouses/your_warehouse_id'
os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="supply_chain_assistant", key="databricks_token")
os.environ['CATALOG_NAME'] = 'main'
os.environ['SCHEMA_NAME'] = 'supply_chain'
os.environ['TABLE_NAME'] = 'orders'

# Cell 3: Import and initialize
import sys
sys.path.append('/Workspace/Users/your_email@company.com/')
from data_assistant import DataAssistant

assistant = DataAssistant()
print(f"✓ Assistant initialized with {assistant.llm_provider.upper()}")

# Cell 4: Use the assistant
# Generate SQL only
result = assistant.query("What are the top 5 products by revenue?", execute=False)
print(f"Generated SQL:\n{result['sql_query']}")

# Cell 5: Execute queries
result = assistant.query("Show me orders from the last 7 days", execute=True)
display(result['results'])
```

## Method 2: Databricks Job

For scheduled or automated execution.

### Step 1: Package the Application

Create a wheel file:

1. Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="supply-chain-data-assistant",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
        "databricks-sql-connector>=2.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
    ],
)
```

2. Build the wheel:

```bash
python setup.py bdist_wheel
```

### Step 2: Upload to DBFS or Unity Catalog Volume

```bash
# Upload to DBFS
databricks fs cp dist/supply_chain_data_assistant-1.0.0-py3-none-any.whl dbfs:/libraries/

# OR upload to Unity Catalog Volume
databricks fs cp dist/supply_chain_data_assistant-1.0.0-py3-none-any.whl /Volumes/main/default/libraries/
```

### Step 3: Create a Databricks Job

1. Go to Workflows → Create Job
2. Configure the job:
   - **Task Name**: Supply Chain Data Assistant
   - **Type**: Python script
   - **Source**: Workspace or Git
   - **Script Path**: `/Workspace/Users/your_email@company.com/data_assistant.py`
3. Add libraries:
   - Add the wheel file from DBFS or Volume
4. Set environment variables in the job configuration:
   - Under "Advanced options" → "Environment variables"
   - Add all required environment variables
5. Configure the cluster:
   - Use a cluster with Unity Catalog enabled
   - Runtime: DBR 13.3 LTS or higher recommended

### Step 4: Add Job Parameters

If you want to pass queries as parameters:

```python
# Modify data_assistant.py to accept parameters
import sys

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Show me the top 10 records"
    
    assistant = DataAssistant()
    result = assistant.query(query, execute=True)
    print(result)
```

Then pass the query as a job parameter.

## Method 3: Databricks App

For building a Streamlit or Gradio web interface.

### Using Streamlit

Create `streamlit_app.py`:

```python
import streamlit as st
import os
from data_assistant import DataAssistant

# Configure environment
os.environ['LLM_PROVIDER'] = st.secrets["LLM_PROVIDER"]
os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]
# ... other configurations from secrets

st.title("🤖 Supply Chain Data Assistant")

# Initialize assistant
@st.cache_resource
def get_assistant():
    return DataAssistant()

assistant = get_assistant()

# User input
user_query = st.text_input("Ask a question about your data:")

if st.button("Generate SQL"):
    if user_query:
        with st.spinner("Generating SQL..."):
            result = assistant.query(user_query, execute=False)
            st.code(result['sql_query'], language='sql')
            
            if st.button("Execute Query"):
                result = assistant.query(user_query, execute=True)
                if result['status'] == 'success':
                    st.dataframe(result['results'])
                else:
                    st.error(result['error'])
```

Deploy on Databricks:

```bash
databricks apps create supply-chain-assistant \
  --source-code-path ./streamlit_app.py \
  --description "Natural language to SQL assistant"
```

## Configuration Best Practices

### 1. Use Databricks Secrets

Never hardcode credentials:

```python
# ✗ Bad
os.environ['OPENAI_API_KEY'] = 'sk-abc123...'

# ✓ Good
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="my_scope", key="openai_key")
```

### 2. Use Unity Catalog Volumes for Files

Store application files in Unity Catalog Volumes:

```python
# Upload files
databricks fs cp data_assistant.py /Volumes/main/default/apps/

# Use in notebook
sys.path.append('/Volumes/main/default/apps/')
from data_assistant import DataAssistant
```

### 3. Use Cluster Policies

Create a cluster policy that ensures:
- Unity Catalog is enabled
- Appropriate runtime version (DBR 13.3 LTS or higher)
- Required libraries are pre-installed

### 4. Set Up Monitoring

Add logging to track usage:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In data_assistant.py, add logging
logger = logging.getLogger(__name__)
logger.info(f"Query executed: {natural_language_query}")
```

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure the path is added to sys.path:

```python
import sys
sys.path.append('/Workspace/Users/your_email@company.com/')
```

### Issue: "Secret not found"

**Solution**: Verify the secret scope and key exist:

```python
# List all scopes
dbutils.secrets.listScopes()

# List keys in a scope
dbutils.secrets.list("supply_chain_assistant")
```

### Issue: "Unity Catalog table not found"

**Solution**: Verify permissions:

```sql
-- Check if you can access the table
SHOW TABLES IN main.supply_chain;

-- Check table details
DESCRIBE TABLE main.supply_chain.orders;
```

### Issue: SQL Warehouse connection timeout

**Solution**: 
- Ensure the SQL Warehouse is running
- Check the HTTP path is correct
- Verify network connectivity

### Issue: LLM API rate limits

**Solution**:
- Implement retry logic
- Use exponential backoff
- Consider caching common queries

## Performance Optimization

### 1. Cache Table Schema

The assistant automatically caches table schema. To clear cache:

```python
assistant._table_schema = None
schema = assistant.get_table_schema()
```

### 2. Use Serverless SQL Warehouses

For faster startup and better cost efficiency:
- Enable Serverless SQL Warehouse in Databricks
- Update HTTP_PATH to point to serverless warehouse

### 3. Batch Queries

For multiple queries, reuse the assistant instance:

```python
assistant = DataAssistant()

for query in queries:
    result = assistant.query(query, execute=True)
    # Process result
```

## Security Checklist

- [ ] API keys stored in Databricks Secrets
- [ ] SQL Warehouse has appropriate access controls
- [ ] Unity Catalog tables have proper permissions
- [ ] Network access is restricted
- [ ] Audit logging is enabled
- [ ] Regular security reviews are scheduled

## Next Steps

1. Test the basic notebook implementation
2. Create a scheduled job for automated queries
3. Build a Streamlit app for end-users
4. Set up monitoring and alerting
5. Document custom queries for your team

## Support

For Databricks-specific issues:
- Check Databricks documentation: https://docs.databricks.com
- Review Unity Catalog guides
- Contact Databricks support

For application issues:
- Check the main README.md
- Review the troubleshooting section
- Open an issue on GitHub
