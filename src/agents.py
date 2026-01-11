"""
Multi-Agent System for Retail Insights Assistant
Implements three core agents:
1. Query Understanding Agent - Interprets natural language and converts to structured intent
2. Data Extraction Agent - Executes queries and retrieves data
3. Validation Agent - Validates results and generates insights
"""

from typing import TypedDict, Annotated, Sequence, Dict, Any, Union
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
import pandas as pd
from data_manager import DataManager
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the state that will be passed between agents
class AgentState(TypedDict):
    """State object that gets passed between agents"""
    user_query: str
    mode: str  # 'summarization' or 'qa'
    query_intent: Dict[str, Any]
    sql_query: str
    extracted_data: Any
    validation_result: Dict[str, Any]
    final_response: str
    messages: Sequence[Union[HumanMessage, AIMessage]]
    error: str


class MultiAgentSystem:
    """Orchestrates multiple agents using LangGraph"""
    
    def __init__(self, data_manager: DataManager, azure_endpoint: str, deployment_name: str = "gpt-4.1", api_version: str = "2024-12-01-preview"):
        self.data_manager = data_manager
        
        # Configure Azure OpenAI with DefaultAzureCredential
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), 
            "https://cognitiveservices.azure.com/.default"
        )
        
        self.llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=deployment_name,
            api_version=api_version,
            azure_ad_token_provider=token_provider,
            temperature=0
        )
        
        self.llm_creative = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=deployment_name,
            api_version=api_version,
            azure_ad_token_provider=token_provider,
            temperature=0.7
        )
        
        # Build the agent graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("query_understanding", self.query_understanding_agent)
        workflow.add_node("data_extraction", self.data_extraction_agent)
        workflow.add_node("validation", self.validation_agent)
        workflow.add_node("response_generation", self.response_generation_agent)
        
        # Define the flow
        workflow.set_entry_point("query_understanding")
        workflow.add_edge("query_understanding", "data_extraction")
        workflow.add_edge("data_extraction", "validation")
        workflow.add_edge("validation", "response_generation")
        workflow.add_edge("response_generation", END)
        
        return workflow.compile()
    
    def query_understanding_agent(self, state: AgentState) -> AgentState:
        """
        Agent 1: Query Understanding Agent
        Interprets natural language and converts to structured intent
        """
        logger.info("🤖 Query Understanding Agent activated")
        
        schema_info = self.data_manager.get_schema_description()
        
        system_prompt = f"""You are a Query Understanding Agent for a retail analytics system.

Available data schema:
{schema_info}

Your task is to:
1. Understand the user's natural language query
2. Identify the intent (summarization, comparison, trend analysis, specific metric, etc.)
3. Map to relevant tables and columns
4. Identify any filters, aggregations, or time periods mentioned
5. Determine if this is a summarization request or a Q&A request

Return a JSON object with:
- intent: Brief description of what user wants
- mode: "summarization" or "qa"
- tables_needed: List of table names
- columns_needed: List of column names
- filters: Any conditions or filters
- aggregations: Any sum, avg, count operations needed
- time_period: Any date/time filters
- comparison: Any comparison requested (YoY, regions, categories, etc.)
"""
        
        user_message = f"User query: {state['user_query']}"
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse the response
            try:
                query_intent = json.loads(response.content)
            except:
                # If not JSON, create structured intent
                query_intent = {
                    "intent": response.content,
                    "mode": state.get('mode', 'qa'),
                    "tables_needed": [],
                    "columns_needed": [],
                    "filters": [],
                    "aggregations": [],
                    "time_period": None,
                    "comparison": None
                }
            
            state['query_intent'] = query_intent
            state['mode'] = query_intent.get('mode', state.get('mode', 'qa'))
            
            logger.info(f"✓ Intent identified: {query_intent.get('intent', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Query understanding error: {str(e)}")
            state['error'] = f"Query understanding failed: {str(e)}"
        
        return state
    
    def data_extraction_agent(self, state: AgentState) -> AgentState:
        """
        Agent 2: Data Extraction Agent
        Generates and executes SQL queries based on intent
        """
        logger.info("🤖 Data Extraction Agent activated")
        
        query_intent = state.get('query_intent', {})
        
        # Get schema for SQL generation
        schema_info = self.data_manager.get_schema_description()
        
        # Get list of available tables for emphasis
        available_tables = ", ".join([f"`{t}`" for t in self.data_manager.get_all_tables()])
        
        system_prompt = f"""You are a Data Extraction Agent that generates SQL queries.

{schema_info}

**AVAILABLE TABLES**: {available_tables}

Based on the query intent, generate a valid DuckDB SQL query to extract the needed data.

Query Intent:
{json.dumps(query_intent, indent=2)}

CRITICAL Rules:
    1. **ONLY use table names from the Available Tables list above** - Do NOT invent table names like "all_sales", "sales_data", etc.
    2. Use exact table and column names as shown in the schema (case-sensitive)
    3. Use proper SQL syntax for DuckDB
    4. Include appropriate JOINs if multiple tables are needed (e.g., UNION ALL to combine data from multiple sales tables)
    5. Apply filters and aggregations as specified
6. Limit results to reasonable amounts (use LIMIT when appropriate)
7. **IMPORTANT**: When using SUM, AVG, or other numeric functions, check the column type:
   - If the column contains numbers stored as VARCHAR/TEXT, cast it first: CAST(column_name AS DOUBLE)
   - Example: SUM(CAST(amount AS DOUBLE)) instead of SUM(amount)
8. Use TRY_CAST for safer type conversions that won't fail on invalid data
9. **DATE HANDLING**: Date columns may contain invalid values (like "SKU", headers, etc.):
   - **CRITICAL**: Always filter out non-date rows BEFORE parsing dates
   - Use WHERE clause with LIKE: `WHERE date_column LIKE '[0-9]%'` (starts with digit)
   - Or use regex: `WHERE REGEXP_MATCHES(date_column, '^[0-9]')`
   - Then safely parse: `STRPTIME(date_column, '%m-%d-%y')`
   - Example: `SELECT STRFTIME('%Y-%m', STRPTIME(date, '%m-%d-%y')) AS month FROM table WHERE date LIKE '[0-9]%'`
   - Common formats: '%m-%d-%y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'
   - Never use STRPTIME on unfiltered columns that may contain text like "SKU"
10. **CTEs (WITH clauses)**: 
    - **STRONGLY PREFER simple queries without CTEs** - they're more reliable
    - Only use CTEs if absolutely necessary (complex multi-step logic)
    - If using CTEs, the final SELECT must reference an existing CTE or base table
    - Keep CTE queries simple - avoid nested or overly complex logic
    - Test: Can this be written as a single SELECT? If yes, do that instead!
11. **String Aggregation**: For concatenating strings:
    - Use `STRING_AGG(column, delimiter)` not `list_aggr()` or `group_concat()`
    - Example: `STRING_AGG(category, ', ')` to join categories with commas
    - For array aggregation use `LIST(column)`
12. Return ONLY the SQL query, nothing else
13. If you need to combine data from multiple tables, use UNION ALL or appropriate JOINs

**Remember**: Simple queries are better! Avoid CTEs unless essential. Most questions can be answered with straightforward SELECT + GROUP BY + ORDER BY.
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Generate SQL for: {state['user_query']}")
            ]
            
            response = self.llm.invoke(messages)
            sql_query = response.content.strip()
            
            # Clean up SQL query (remove markdown code blocks if present)
            if sql_query.startswith("```"):
                sql_query = sql_query.split("```")[1]
                if sql_query.startswith("sql"):
                    sql_query = sql_query[3:]
                sql_query = sql_query.strip()
            
            state['sql_query'] = sql_query
            logger.info(f"✓ Generated SQL: {sql_query[:100]}...")
            
            # Execute the query
            try:
                result_df = self.data_manager.execute_query(sql_query)
                state['extracted_data'] = result_df
                logger.info(f"✓ Extracted {len(result_df)} rows")
            except Exception as e:
                error_msg = str(e)
                logger.error(f"SQL execution error: {error_msg}")
                
                # Try to fix common SQL errors automatically
                # Check if this is a fixable error
                fixable_keywords = ["sum(varchar)", "type", "strftime", "date", "parser", 
                                   "syntax", "union", "table", "does not exist", "catalog error",
                                   "binder error", "conversion error", "list_aggr", "no function matches",
                                   "string_agg", "group_concat", "referenced column", "not found"]
                is_fixable = any(keyword in error_msg.lower() for keyword in fixable_keywords)
                
                if is_fixable:
                    logger.info("Attempting to fix SQL query...")
                    
                    fix_prompt = f"""The SQL query failed with an error:
{error_msg}

Original query:
{sql_query}

Available tables: {', '.join([f'`{t}`' for t in self.data_manager.get_all_tables()])}

Full schema with all columns:
{self.data_manager.get_schema_description()}

Please fix this query by:
1. **For "column not found" or "referenced column" errors**:
   - Check the schema above for the EXACT columns available in each table
   - DO NOT reference columns that don't exist in the table
   - If a column doesn't exist, either remove it or use NULL AS column_name
   - Example: If "category" doesn't exist in international_sale_report, use NULL AS category
2. Adding appropriate type casts (CAST or TRY_CAST) for VARCHAR/TEXT columns used in numeric functions
3. For date parsing errors like "Could not parse string 'SKU'":
   - The column contains non-date values that must be filtered out FIRST
   - **Add WHERE filter**: Use `WHERE date_column LIKE '[0-9]%'` to keep only rows starting with a digit
   - Or use: `WHERE REGEXP_MATCHES(date_column, '^[0-9]')`
   - Then parse safely: `STRPTIME(date_column, '%m-%d-%y')`
   - Example fix: Change `STRPTIME(date, '%m-%d-%y')` to use filtered data:
     ```sql
     SELECT ... FROM table WHERE date LIKE '[0-9]%' AND date IS NOT NULL
     ```
   - Common formats: MM-DD-YY ('%m-%d-%y'), DD-MM-YYYY ('%d-%m-%Y')
4. For "REGEXP" syntax errors:
   - DuckDB uses `REGEXP_MATCHES(column, pattern)` not `column REGEXP pattern`
   - Or use simpler LIKE: `column LIKE '[0-9]%'`
5. For "list_aggr" or "string_agg" function errors:
   - DuckDB uses `STRING_AGG(column, delimiter)` not `list_aggr(column, delimiter)`
   - Or use `LIST(column)` for array aggregation
   - Example: Change `list_aggr(category, ', ')` to `STRING_AGG(category, ', ')`
6. For UNION syntax errors, ensure:
   - Each SELECT in the UNION has the same number of columns
   - Column data types match between UNIONed queries
   - Each SELECT is properly terminated before UNION ALL
   - Wrap complex expressions in parentheses if needed
7. For "table does not exist" errors:
   - **CRITICAL**: If the error mentions a CTE name (like "amazon_top_categories"), this query is too complex
   - **SIMPLIFY THE QUERY**: Remove all CTEs and write a single, direct query instead
   - Use ONLY the actual base table names from the list above (like `amazon_sale_report`, not CTEs)
   - Example: Instead of complex CTEs, use a simple query like:
     ```sql
     SELECT category, SUM(CAST(amount AS DOUBLE)) AS total
     FROM amazon_sale_report
     WHERE amount IS NOT NULL
     GROUP BY category
     ORDER BY total DESC
     LIMIT 10
     ```
   - Avoid multi-CTE queries - they often fail. Keep it simple!
   - Ensure all CTE names are properly referenced
   - Consider simplifying to a single query without CTEs if there are issues
8. Check for missing commas, unmatched parentheses, or other syntax issues

Return ONLY the fixed SQL query, nothing else."""
                    
                    try:
                        fix_response = self.llm.invoke([HumanMessage(content=fix_prompt)])
                        fixed_sql = fix_response.content.strip()
                        
                        # Clean up
                        if fixed_sql.startswith("```"):
                            fixed_sql = fixed_sql.split("```")[1]
                            if fixed_sql.startswith("sql"):
                                fixed_sql = fixed_sql[3:]
                            fixed_sql = fixed_sql.strip()
                        
                        logger.info(f"Retrying with fixed SQL: {fixed_sql[:100]}...")
                        result_df = self.data_manager.execute_query(fixed_sql)
                        state['extracted_data'] = result_df
                        state['sql_query'] = fixed_sql  # Update with working query
                        logger.info(f"✓ Query fixed! Extracted {len(result_df)} rows")
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {str(retry_error)}")
                        state['error'] = f"Query execution failed even after fix attempt: {str(retry_error)}"
                        state['extracted_data'] = pd.DataFrame()
                else:
                    state['error'] = f"Query execution failed: {error_msg}"
                    state['extracted_data'] = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Data extraction error: {str(e)}")
            state['error'] = f"Data extraction failed: {str(e)}"
        
        return state
    
    def validation_agent(self, state: AgentState) -> AgentState:
        """
        Agent 3: Validation Agent
        Validates results and checks for data quality
        """
        logger.info("🤖 Validation Agent activated")
        
        extracted_data = state.get('extracted_data', pd.DataFrame())
        
        validation_result = {
            "is_valid": True,
            "data_quality": {},
            "warnings": [],

            "recommendations": []
        }
        
        # Check if data was extracted
        if extracted_data.empty:
            validation_result['is_valid'] = False
            validation_result['warnings'].append("No data returned from query")
            validation_result['recommendations'].append("Check if the query matches available data")
        else:
            # Data quality checks
            validation_result['data_quality'] = {
                "row_count": len(extracted_data),
                "column_count": len(extracted_data.columns),
                "null_percentages": (extracted_data.isnull().sum() / len(extracted_data) * 100).to_dict()
            }
            
            # Check for high null percentages
            for col, null_pct in validation_result['data_quality']['null_percentages'].items():
                if null_pct > 50:
                    validation_result['warnings'].append(f"Column '{col}' has {null_pct:.1f}% null values")
            
            # Check for reasonable result size
            if len(extracted_data) > 10000:
                validation_result['warnings'].append("Large result set - consider adding filters")
            
            logger.info(f"✓ Validation complete: {validation_result['data_quality']}")
        
        state['validation_result'] = validation_result
        
        return state
    
    def response_generation_agent(self, state: AgentState) -> AgentState:
        """
        Agent 4: Response Generation Agent
        Generates natural language response based on extracted data
        """
        logger.info("🤖 Response Generation Agent activated")
        
        extracted_data = state.get('extracted_data', pd.DataFrame())
        validation = state.get('validation_result', {})
        query_intent = state.get('query_intent', {})
        
        # Check for errors
        if state.get('error'):
            state['final_response'] = f"I encountered an issue: {state['error']}\n\nPlease rephrase your question or check if the data exists."
            return state
        
        if extracted_data.empty:
            state['final_response'] = "I couldn't find any data matching your query. Please try rephrasing your question."
            return state
        
        # Prepare data summary for LLM
        data_summary = f"""
Data Shape: {len(extracted_data)} rows × {len(extracted_data.columns)} columns

Columns: {', '.join(extracted_data.columns)}

Sample Data (first 10 rows):
{extracted_data.head(10).to_string(index=False)}

Statistics:
{extracted_data.describe().to_string() if not extracted_data.select_dtypes(include='number').empty else 'No numeric columns'}
"""
        
        system_prompt = f"""You are a Business Intelligence Assistant providing insights from retail data.

User's Original Query: {state['user_query']}

Query Intent: {json.dumps(query_intent, indent=2)}

Data Retrieved:
{data_summary}

Validation Results: {json.dumps(validation, indent=2)}

Your task:
1. Provide a clear, concise answer to the user's question
2. Highlight key insights and patterns
3. Use specific numbers and metrics from the data
4. If it's a summarization request, provide a comprehensive overview
5. If there are warnings, mention them diplomatically
6. Format your response in a business-friendly manner

Format with:
- Clear headers
- Bullet points for key insights
- Numbers formatted properly
- Professional tone
"""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Generate the response based on the data above.")
            ]
            
            response = self.llm_creative.invoke(messages)
            state['final_response'] = response.content
            
            logger.info("✓ Response generated successfully")
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            state['final_response'] = f"I have the data but encountered an error generating the response: {str(e)}"
        
        return state
    
    def process_query(self, user_query: str, mode: str = "qa") -> Dict[str, Any]:
        """
        Main entry point to process a user query through the multi-agent system
        
        Args:
            user_query: Natural language query from user
            mode: 'summarization' or 'qa'
        
        Returns:
            Dictionary with final response and intermediate results
        """
        initial_state = {
            "user_query": user_query,
            "mode": mode,
            "query_intent": {},
            "sql_query": "",
            "extracted_data": None,
            "validation_result": {},
            "final_response": "",
            "messages": [],
            "error": ""
        }
        
        # Run the agent workflow
        final_state = self.graph.invoke(initial_state)
        
        return {
            "response": final_state['final_response'],
            "sql_query": final_state.get('sql_query', ''),
            "data": final_state.get('extracted_data'),
            "intent": final_state.get('query_intent', {}),
            "validation": final_state.get('validation_result', {}),
            "error": final_state.get('error', '')
        }


if __name__ == "__main__":
    # Test the multi-agent system
    from dotenv import load_dotenv
    from pathlib import Path
    import os
    
    # Load environment from parent directory
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    # Get Azure OpenAI configuration
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Initialize data manager with correct path
    data_dir = Path(__file__).parent.parent / "Sales Dataset"
    dm = DataManager(str(data_dir))
    dm.load_all_datasets()
    
    print(f"\n✓ Loaded {len(dm.get_all_tables())} tables: {', '.join(dm.get_all_tables())}")
    
    # Initialize agent system with Azure OpenAI
    agent_system = MultiAgentSystem(
        dm, 
        azure_endpoint=azure_endpoint,
        deployment_name=deployment_name,
        api_version=api_version
    )
    
    # Test query
    test_query = "What are the top 5 customers by total sales amount?"
    print(f"\n🔍 Query: {test_query}")
    result = agent_system.process_query(test_query)
    
    print("\n=== Query Result ===")
    print(f"Response: {result['response']}")
    print(f"\nSQL: {result['sql_query']}")
    
    if result.get('data') is not None and not result['data'].empty:
        print(f"\n📊 Data Preview:")
        print(result['data'].head())
