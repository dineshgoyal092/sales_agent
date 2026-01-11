"""
Streamlit UI for Retail Insights Assistant
Provides interactive interface for data summarization and Q&A
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.append(str(Path(__file__).parent))

from data_manager import DataManager
from agents import MultiAgentSystem

# Page configuration
st.set_page_config(
    page_title="Retail Insights Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the data manager and agent system"""
    load_dotenv()
    
    # Get Azure OpenAI configuration from environment or use defaults
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Initialize data manager
    data_dir = Path(__file__).parent.parent / "Sales Dataset"
    dm = DataManager(str(data_dir))
    dm.load_all_datasets()
    
    # Initialize agent system with Azure OpenAI
    try:
        agent_system = MultiAgentSystem(
            dm, 
            azure_endpoint=azure_endpoint,
            deployment_name=deployment_name,
            api_version=api_version
        )
    except Exception as e:
        st.error(f"⚠️ Failed to initialize Azure OpenAI: {str(e)}")
        st.info("💡 Make sure you're authenticated with Azure CLI: `az login`")
        st.stop()
    
    return dm, agent_system


def display_header():
    """Display the app header"""
    st.markdown('<div class="main-header">📊 Retail Insights Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">GenAI-Powered Sales Analytics & Conversational Intelligence</div>', unsafe_allow_html=True)


def display_sidebar(dm: DataManager):
    """Display sidebar with system information"""
    with st.sidebar:
        st.header("📁 Data Overview")
        
        tables = dm.get_all_tables()
        st.metric("Loaded Tables", len(tables))
        
        with st.expander("View Tables"):
            for table in tables:
                info = dm.get_table_info(table)
                st.write(f"**{table}**")
                st.caption(f"📄 {info['original_name']}")
                st.caption(f"📊 {info['rows']:,} rows × {len(info['columns'])} columns")
                st.divider()
        
        st.header("ℹ️ About")
        st.info("""
        This assistant uses a multi-agent architecture:
        
        1. **Query Understanding Agent** - Interprets your question
        2. **Data Extraction Agent** - Retrieves relevant data
        3. **Validation Agent** - Ensures data quality
        4. **Response Generation Agent** - Creates insights
        """)
        
        st.header("💡 Example Queries")
        st.code("""
• Summarize overall sales performance
• Top 5 customers by revenue
• Which categories sell the most?
• Show sales trends by month
• What's the average order value?
        """, language=None)


def summarization_mode(dm: DataManager, agent_system: MultiAgentSystem):
    """Summarization Mode Interface"""
    st.header("📋 Summarization Mode")
    st.write("Generate comprehensive insights and summaries from your sales data.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        summary_type = st.selectbox(
            "Select Summary Type",
            ["Overall Performance", "By Category", "By Time Period", "Top Performers", "Custom Summary"]
        )
    
    with col2:
        generate_btn = st.button("🔍 Generate Summary", type="primary", use_container_width=True)
    
    if generate_btn:
        with st.spinner("🤖 Agents are analyzing your data..."):
            # Generate appropriate query based on summary type
            queries = {
                "Overall Performance": "Provide a comprehensive summary of overall sales performance including total revenue, number of transactions, top categories, and key trends.",
                "By Category": "Summarize sales performance broken down by product categories, showing which categories perform best.",
                "By Time Period": "Analyze sales trends over time, showing monthly or quarterly patterns and growth rates.",
                "Top Performers": "Identify top performing products, customers, and categories by sales volume and revenue.",
                "Custom Summary": "Provide a detailed analytical summary of all key metrics in the sales data."
            }
            
            query = queries.get(summary_type, queries["Custom Summary"])
            
            result = agent_system.process_query(query, mode="summarization")
            
            # Display results
            if result['error']:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success("✅ Summary generated successfully!")
                
                # Main response
                st.markdown("### 📊 Insights")
                st.markdown(result['response'])
                
                # Show data if available
                if result['data'] is not None and not result['data'].empty:
                    with st.expander("📈 View Underlying Data"):
                        st.dataframe(result['data'], use_container_width=True)
                        
                        # Offer download
                        csv = result['data'].to_csv(index=False)
                        st.download_button(
                            "⬇️ Download Data",
                            csv,
                            "summary_data.csv",
                            "text/csv",
                            key='download-csv'
                        )
                
                # Show SQL query
                with st.expander("🔍 View Generated SQL Query"):
                    st.code(result['sql_query'], language='sql')
                
                # Show validation info
                if result['validation']:
                    with st.expander("✅ Validation Report"):
                        st.json(result['validation'])


def qa_mode(dm: DataManager, agent_system: MultiAgentSystem):
    """Q&A Mode Interface"""
    st.header("💬 Conversational Q&A Mode")
    st.write("Ask questions about your sales data in natural language.")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for i, chat in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat['question'])
        with st.chat_message("assistant"):
            st.markdown(chat['answer'])
            if chat.get('data') is not None and not chat['data'].empty:
                with st.expander("📊 View Data"):
                    st.dataframe(chat['data'], use_container_width=True)
    
    # Chat input
    user_question = st.chat_input("Ask a question about your sales data...")
    
    if user_question:
        # Add user message to chat
        st.session_state.chat_history.append({
            'question': user_question,
            'answer': '',
            'data': None
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_question)
        
        # Get response from agent system
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                result = agent_system.process_query(user_question, mode="qa")
                
                if result['error']:
                    answer = f"❌ I encountered an issue: {result['error']}"
                else:
                    answer = result['response']
                
                st.markdown(answer)
                
                # Update chat history
                st.session_state.chat_history[-1]['answer'] = answer
                st.session_state.chat_history[-1]['data'] = result.get('data')
                
                # Show data if available
                if result.get('data') is not None and not result['data'].empty:
                    with st.expander("📊 View Data"):
                        st.dataframe(result['data'], use_container_width=True)
                        
                        # Create simple visualization if numeric data
                        numeric_cols = result['data'].select_dtypes(include='number').columns
                        if len(numeric_cols) > 0 and len(result['data']) <= 50:
                            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"], 
                                                     key=f"chart_{len(st.session_state.chat_history)}")
                            
                            if chart_type == "Bar" and len(result['data'].columns) >= 2:
                                fig = px.bar(result['data'], x=result['data'].columns[0], 
                                            y=numeric_cols[0], title="Data Visualization")
                                st.plotly_chart(fig, use_container_width=True)
                            elif chart_type == "Line" and len(result['data'].columns) >= 2:
                                fig = px.line(result['data'], x=result['data'].columns[0], 
                                             y=numeric_cols[0], title="Data Visualization")
                                st.plotly_chart(fig, use_container_width=True)
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


def data_explorer(dm: DataManager):
    """Data Explorer Interface"""
    st.header("🔍 Data Explorer")
    st.write("Browse and explore your loaded datasets.")
    
    # Select table
    tables = dm.get_all_tables()
    selected_table = st.selectbox("Select a table to explore", tables)
    
    if selected_table:
        # Get table info
        info = dm.get_table_info(selected_table)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{info['rows']:,}")
        with col2:
            st.metric("Total Columns", len(info['columns']))
        with col3:
            st.metric("Original File", info['original_name'])
        
        # Display data
        st.subheader("📊 Data Preview")
        data = dm.tables[selected_table]
        
        # Filter options
        show_rows = st.slider("Number of rows to display", 5, min(100, len(data)), 10)
        st.dataframe(data.head(show_rows), use_container_width=True)
        
        # Statistics
        with st.expander("📈 Statistical Summary"):
            st.write(data.describe())
        
        # Column info
        with st.expander("📋 Column Information"):
            col_info = pd.DataFrame({
                'Column': data.columns,
                'Type': data.dtypes.values,
                'Non-Null Count': data.count().values,
                'Null Count': data.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)


def main():
    """Main application"""
    # Initialize system
    dm, agent_system = initialize_system()
    
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar(dm)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📋 Summarization", "💬 Q&A Chat", "🔍 Data Explorer"])
    
    with tab1:
        summarization_mode(dm, agent_system)
    
    with tab2:
        qa_mode(dm, agent_system)
    
    with tab3:
        data_explorer(dm)
    
    # Footer
    st.divider()
    st.caption("🤖 Powered by Multi-Agent AI System | Built with LangGraph, OpenAI, and Streamlit")


if __name__ == "__main__":
    main()
