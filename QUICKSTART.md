# Quick Start Guide

Get up and running with the Supply Chain Data Assistant in 5 minutes!

## Prerequisites

- Python 3.8+
- Databricks workspace access
- OpenAI or Gemini API key

## 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/alvinjchua888/supplychaindataassistant.git
cd supplychaindataassistant

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Required configuration:

```env
# Choose your LLM provider
LLM_PROVIDER=openai

# OpenAI credentials (if using OpenAI)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Databricks credentials
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=your-token-here

# Your Unity Catalog table
CATALOG_NAME=main
SCHEMA_NAME=supply_chain
TABLE_NAME=orders
```

## 3. Get Your Credentials

### OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and paste it in your `.env` file

### Databricks Credentials

1. **Server Hostname**: Your workspace URL (e.g., `dbc-12345678-9abc.cloud.databricks.com`)
2. **HTTP Path**:
   - Go to SQL Warehouses in Databricks
   - Click on your warehouse
   - Click "Connection details"
   - Copy the HTTP Path
3. **Access Token**:
   - Click your profile icon → User Settings
   - Go to Developer → Access Tokens
   - Click "Generate new token"
   - Copy the token

## 4. Run the Assistant

### Interactive Mode

```bash
python data_assistant.py
```

You'll see:

```
Supply Chain Data Assistant
==================================================
✓ Initialized with OPENAI LLM provider
✓ Connected to table: main.supply_chain.orders

Interactive Mode (type 'exit' to quit)
==================================================

Enter your question: Show me the top 10 products by quantity
```

### Programmatic Usage

Create a Python script:

```python
from data_assistant import DataAssistant

# Initialize
assistant = DataAssistant()

# Generate SQL
result = assistant.query("What are the top 5 suppliers by revenue?")
print(f"SQL: {result['sql_query']}")

# Execute query
result = assistant.query("Show orders from last week", execute=True)
print(f"Results: {result['results']}")
```

## 5. Test It Out

Try these example queries:

1. **Simple selection**: "Show me the first 10 records"
2. **Aggregation**: "What is the total revenue by region?"
3. **Filtering**: "Find all orders from the last 30 days"
4. **Sorting**: "Show the top 5 products by quantity"
5. **Complex query**: "Which suppliers have orders above $10,000 in the last quarter?"

## Databricks Quick Start

### In a Databricks Notebook

```python
# Cell 1: Install dependencies
%pip install openai google-generativeai databricks-sql-connector python-dotenv pydantic

# Cell 2: Configure (using secrets)
import os
os.environ['LLM_PROVIDER'] = 'openai'
os.environ['OPENAI_API_KEY'] = dbutils.secrets.get(scope="my_scope", key="openai_key")
os.environ['DATABRICKS_SERVER_HOSTNAME'] = 'your-workspace.cloud.databricks.com'
os.environ['DATABRICKS_HTTP_PATH'] = '/sql/1.0/warehouses/your-warehouse-id'
os.environ['DATABRICKS_ACCESS_TOKEN'] = dbutils.secrets.get(scope="my_scope", key="db_token")
os.environ['CATALOG_NAME'] = 'main'
os.environ['SCHEMA_NAME'] = 'supply_chain'
os.environ['TABLE_NAME'] = 'orders'

# Cell 3: Upload data_assistant.py to workspace and import
import sys
sys.path.append('/Workspace/Users/your-email@company.com/')
from data_assistant import DataAssistant

# Cell 4: Use it!
assistant = DataAssistant()
result = assistant.query("Show top 10 products", execute=True)
display(result['results'])
```

## Troubleshooting

### "OPENAI_API_KEY not found"

- Make sure your `.env` file is in the same directory as `data_assistant.py`
- Check that the variable name is exactly `OPENAI_API_KEY` (case-sensitive)

### "Table not found"

- Verify your catalog, schema, and table names are correct
- Check that you have permissions to access the table
- Try running this in Databricks: `SELECT * FROM catalog.schema.table LIMIT 1`

### "Connection timeout"

- Ensure your SQL Warehouse is running
- Check that the HTTP path is correct
- Verify your access token is valid

### "Rate limit exceeded"

- You're making too many API calls to OpenAI/Gemini
- Wait a few minutes and try again
- Consider using a paid API tier for higher limits

## Next Steps

1. ✅ **Read the full README**: [README.md](README.md)
2. ✅ **Explore examples**: [examples.py](examples.py)
3. ✅ **Deploy on Databricks**: [DATABRICKS_DEPLOYMENT.md](DATABRICKS_DEPLOYMENT.md)
4. ✅ **Customize prompts**: Edit the prompt in `data_assistant.py`
5. ✅ **Add more features**: Extend the `DataAssistant` class

## Common Use Cases

### 1. Data Exploration

```python
assistant.query("Show me the schema of the table")
assistant.query("How many records are in the table?")
assistant.query("What are the unique values in the status column?")
```

### 2. Business Analytics

```python
assistant.query("What is the revenue trend over the last 6 months?")
assistant.query("Which products have declining sales?")
assistant.query("Show me the customer retention rate")
```

### 3. Supply Chain Monitoring

```python
assistant.query("Which items are low in stock?")
assistant.query("What is the average delivery time by supplier?")
assistant.query("Find orders that are delayed")
```

## Tips for Better Results

1. **Be specific**: "Show top 10 products by revenue in 2024" vs "Show products"
2. **Use table columns**: Mention actual column names if you know them
3. **Specify limits**: Always include "top 10" or "limit 100" to avoid huge results
4. **Iterate**: If the first query isn't perfect, refine your question
5. **Review SQL**: Always check the generated SQL before executing

## Getting Help

- 📖 Documentation: See [README.md](README.md)
- 🐛 Issues: Open an issue on GitHub
- 💬 Questions: Check existing issues or create a discussion

Happy querying! 🚀
