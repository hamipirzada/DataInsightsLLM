import streamlit as st
import pandas as pd
from data_processor import DataProcessor
from visualization import Visualizer
from rag_engine import RAGEngine
import plotly.express as px
from io import BytesIO
import traceback

# Configure Streamlit page
st.set_page_config(
    page_title="Excel Insights AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def read_file_safely(uploaded_file):
    """Safely read uploaded file with proper error handling"""
    try:
        # Get the file content as bytes
        file_content = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            # For Excel files, use BytesIO
            buffer = BytesIO(file_content)
            return pd.read_excel(buffer)
        else:
            # For CSV files, try multiple encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    return pd.read_csv(uploaded_file, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try reading with error handling
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding='utf-8', errors='replace')
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def main():
    # Custom CSS with darker gradient background
    st.markdown("""
        <style>
        /* Modern dark gradient animated background */
        .stApp {
            background: linear-gradient(-45deg, 
                #1a1a2e,  /* Dark navy */
                #16213e,  /* Deep blue */
                #1f1f1f,  /* Almost black */
                #0f3460   /* Dark royal blue */
            );
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Enhanced tab styling with darker theme */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 10px;
            color: #fff;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255,255,255,0.1);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(255,255,255,0.15) !important;
            border-radius: 10px;
        }
        
        /* Enhanced card styling for dark theme */
        .stDataFrame, div[data-testid="stMetricValue"] {
            background-color: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 1rem;
            backdrop-filter: blur(10px);
        }
        
        /* Improved metric styling */
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            color: #FFFFFF !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            font-weight: 600 !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.1rem !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Better chart visibility in dark theme */
        .js-plotly-plot {
            background-color: rgba(255,255,255,0.03);
            border-radius: 15px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }
        
        /* File uploader styling for dark theme */
        .stFileUploader {
            background-color: rgba(255,255,255,0.03);
            border-radius: 15px;
            padding: 2rem;
            border: 2px dashed rgba(255,255,255,0.15);
            margin: 2rem 0;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: rgba(0,0,0,0.2);
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Better spacing */
        .main {
            scroll-behavior: smooth;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Add sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <p style="color: white; font-size: 1.2rem; font-weight: 500;">Excel Insights AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx', 'xls', 'csv'])
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            
            # Add navigation in sidebar
            st.markdown("### Navigation")
            page = st.radio(
                "Go to",
                ["Quick Overview", "Detailed Analysis", "Custom Insights"],
                label_visibility="collapsed"
            )
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Process the file
            processor = DataProcessor(uploaded_file)
            visualizer = Visualizer(processor.df)
            rag_engine = RAGEngine(processor.df)
            
            # Display sections based on navigation
            if page == "Quick Overview":
                display_quick_overview(processor, visualizer, rag_engine)
            elif page == "Detailed Analysis":
                display_detailed_analysis(processor, visualizer, rag_engine)
            elif page == "Custom Insights":
                display_custom_insights(processor, visualizer, rag_engine)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    else:
        # Stylish placeholder content
        st.markdown("""
            <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.8);">
                <p style="font-size: 1.1rem;">Upload an Excel file to begin your analysis journey</p>
                <p style="font-size: 1.1rem;">Discover insights, visualize patterns, and make data-driven decisions</p>
            </div>
        """, unsafe_allow_html=True)

def display_quick_overview(processor, visualizer, rag_engine):
    st.header("Quick Overview")
    
    # Display dataset summary in a more organized way
    st.subheader("Dataset Summary")
    summary = processor.get_basic_stats()
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", summary.get("rows", "N/A"))
    with col2:
        st.metric("Total Columns", summary.get("columns", "N/A"))
    with col3:
        st.metric("Missing Values", summary.get("missing_values", "N/A"))
    with col4:
        st.metric("Memory Usage", summary.get("memory_usage", "N/A"))
        
    # Display column types in a table
    if "column_types" in summary:
        st.subheader("Column Types")
        col_types_df = pd.DataFrame.from_dict(
            summary["column_types"], 
            orient='index', 
            columns=['Count']
        ).reset_index()
        col_types_df.columns = ['Data Type', 'Count']
        st.table(col_types_df)
    
    # Display data quality metrics in an organized table
    st.subheader("Data Quality")
    quality_metrics = processor.get_data_quality_metrics()
    
    # Convert the nested dictionary to a DataFrame for better display
    quality_data = []
    for col, metrics in quality_metrics.items():
        # Convert percentage string to float
        if 'missing_percentage' in metrics:
            metrics['missing_percentage'] = float(metrics['missing_percentage'].strip('%'))
        quality_data.append({
            'Column': col,
            'Data Type': metrics.get('data_type', ''),
            'Missing Values': metrics.get('missing', 0),
            'Missing %': metrics.get('missing_percentage', 0),
            'Unique Values': metrics.get('unique_values', 0)
        })
    
    if quality_data:
        quality_df = pd.DataFrame(quality_data)
        # Style the DataFrame
        styled_df = quality_df.style.background_gradient(
            subset=['Missing %'],
            cmap='RdYlGn_r',
            vmin=0,
            vmax=100
        ).format({
            'Missing %': '{:.2f}%',
            'Missing Values': '{:,.0f}',
            'Unique Values': '{:,.0f}'
        })
        
        st.dataframe(styled_df, use_container_width=True)
    
    # Display visualizations
    st.subheader("Sales Dashboard")
    visualizer.plot_sales_dashboard()

def display_detailed_analysis(processor, visualizer, rag_engine):
    st.header("Detailed Analysis")

    # Tabs for different analysis aspects
    tab1, tab2, tab3 = st.tabs(["Statistical Analysis", "Correlations", "AI Insights"])
    
    with tab1:
        st.write(processor.get_detailed_stats())
        visualizer.plot_statistical_analysis()

    with tab2:
        st.write(processor.get_correlations())
        visualizer.plot_correlation_matrix()

    with tab3:
        insights = rag_engine.generate_insights()
        st.write(insights)
        visualizer.plot_ai_recommended_charts()

def display_custom_insights(processor, visualizer, rag_engine):
    st.header("Custom Insights")
    
    # Add visualization type selector
    viz_type = st.selectbox(
        "Select Visualization Type",
        ["Distribution Analysis", "Correlation Analysis", "Trend Analysis", "Custom Question"]
    )
    
    if viz_type == "Distribution Analysis":
        visualizer.plot_distribution_analysis()
    elif viz_type == "Correlation Analysis":
        visualizer.plot_correlation_matrix()
    elif viz_type == "Trend Analysis":
        visualizer.plot_trend_analysis()
    elif viz_type == "Custom Question":
        user_question = st.text_input("Ask a question about your data:")
        if user_question:
            answer = rag_engine.answer_question(user_question)
            st.write(answer)

if __name__ == "__main__":
    main() 
