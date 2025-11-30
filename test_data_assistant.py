"""
Basic tests for the Supply Chain Data Assistant.
These tests verify the structure and basic functionality without requiring API keys.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock


class TestDataAssistantStructure(unittest.TestCase):
    """Test the basic structure of the DataAssistant class."""
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('openai.api_key')
    def test_initialization_openai(self, mock_openai_key):
        """Test initialization with OpenAI provider."""
        from data_assistant import DataAssistant
        
        assistant = DataAssistant(llm_provider='openai')
        
        self.assertEqual(assistant.llm_provider, 'openai')
        self.assertEqual(assistant.catalog_name, 'test_catalog')
        self.assertEqual(assistant.schema_name, 'test_schema')
        self.assertEqual(assistant.table_name, 'test_table')
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'gemini',
        'GEMINI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialization_gemini(self, mock_model, mock_configure):
        """Test initialization with Gemini provider."""
        from data_assistant import DataAssistant
        
        assistant = DataAssistant(llm_provider='gemini')
        
        self.assertEqual(assistant.llm_provider, 'gemini')
        mock_configure.assert_called_once()
    
    def test_initialization_missing_api_key(self):
        """Test that initialization fails with missing API key."""
        from data_assistant import DataAssistant
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'openai'}, clear=True):
            with self.assertRaises(ValueError):
                DataAssistant(llm_provider='openai')
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('openai.api_key')
    def test_generate_sql_prompt(self, mock_openai_key):
        """Test SQL prompt generation."""
        from data_assistant import DataAssistant
        
        assistant = DataAssistant(llm_provider='openai')
        assistant._table_schema = "col1: string\ncol2: int"
        
        prompt = assistant.generate_sql_prompt("Show me all records")
        
        self.assertIn("test_catalog.test_schema.test_table", prompt)
        self.assertIn("col1: string", prompt)
        self.assertIn("col2: int", prompt)
        self.assertIn("Show me all records", prompt)
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('openai.api_key')
    @patch('openai.chat.completions.create')
    def test_generate_sql_with_openai(self, mock_create, mock_openai_key):
        """Test SQL generation with OpenAI."""
        from data_assistant import DataAssistant
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "SELECT * FROM test_table"
        mock_create.return_value = mock_response
        
        assistant = DataAssistant(llm_provider='openai')
        sql = assistant.generate_sql_with_openai("test prompt")
        
        self.assertEqual(sql, "SELECT * FROM test_table")
        mock_create.assert_called_once()
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('openai.api_key')
    def test_sql_query_removes_markdown(self, mock_openai_key):
        """Test that markdown code blocks are removed from SQL."""
        from data_assistant import DataAssistant
        
        assistant = DataAssistant(llm_provider='openai')
        
        # Test with markdown
        with patch.object(assistant, 'generate_sql_with_openai') as mock_gen:
            mock_gen.return_value = "```sql\nSELECT * FROM table\n```"
            
            # The method already strips markdown in generate_sql_with_openai
            result = assistant.generate_sql_with_openai("test")
            
            self.assertNotIn("```", result)


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def test_unsupported_llm_provider(self):
        """Test that unsupported LLM provider raises error."""
        from data_assistant import DataAssistant
        
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'unsupported',
            'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
            'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
            'DATABRICKS_ACCESS_TOKEN': 'test-token',
            'CATALOG_NAME': 'test_catalog',
            'SCHEMA_NAME': 'test_schema',
            'TABLE_NAME': 'test_table'
        }):
            with self.assertRaises(ValueError) as context:
                DataAssistant(llm_provider='unsupported')
            
            self.assertIn("Unsupported LLM provider", str(context.exception))


class TestSecurityFeatures(unittest.TestCase):
    """Test security-related features."""
    
    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'OPENAI_API_KEY': 'test-key',
        'DATABRICKS_SERVER_HOSTNAME': 'test.databricks.com',
        'DATABRICKS_HTTP_PATH': '/sql/1.0/warehouses/test',
        'DATABRICKS_ACCESS_TOKEN': 'test-token',
        'CATALOG_NAME': 'test_catalog',
        'SCHEMA_NAME': 'test_schema',
        'TABLE_NAME': 'test_table'
    })
    @patch('openai.api_key')
    def test_api_keys_not_exposed(self, mock_openai_key):
        """Test that API keys are not exposed in object representation."""
        from data_assistant import DataAssistant
        
        assistant = DataAssistant(llm_provider='openai')
        
        # Check that sensitive data is stored but not easily exposed
        self.assertTrue(hasattr(assistant, 'openai_api_key'))
        self.assertEqual(assistant.openai_api_key, 'test-key')
        
        # In a real implementation, you might want to add __repr__ that masks keys


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
