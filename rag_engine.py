from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
import pandas as pd
from langchain_community.vectorstores.chroma import Chroma

class RAGEngine:
    def __init__(self, df):
        self.df = df
        # Set Groq API key
        os.environ["GROQ_API_KEY"] = "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"
        self.setup_rag()
        
    def setup_rag(self):
        # Convert DataFrame to text for RAG
        self.data_text = self.df.to_string()
        
        # Create text splitter
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Split text into chunks
        texts = text_splitter.split_text(self.data_text)
        
        # Initialize Groq Chat model
        self.llm = ChatGroq(
            temperature=0,
            model_name="mixtral-8x7b-32768",
            max_tokens=1024
        )
        
        # Use HuggingFace embeddings instead of OpenAI
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create vector store
        self.vectorstore = Chroma.from_texts(texts, embeddings)
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever()
        
    def generate_insights(self):
        """Generate AI insights about the data"""
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever
            )
            
            prompt = """Analyze this dataset and provide key insights including:
            1. Main patterns and trends
            2. Notable correlations
            3. Unusual observations or outliers
            4. Potential business implications
            
            Keep the response concise and actionable."""
            
            return qa_chain.run(prompt)
        except Exception as e:
            return f"Error generating insights: {str(e)}"
        
    def answer_question(self, question: str) -> str:
        try:
            # Simple data analysis based on the question
            if 'total' in question.lower():
                numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    total = self.df[numeric_cols[0]].sum()
                    return f"The total for {numeric_cols[0]} is {total:,.2f}"
                
            elif 'average' in question.lower() or 'mean' in question.lower():
                numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    mean = self.df[numeric_cols[0]].mean()
                    return f"The average for {numeric_cols[0]} is {mean:,.2f}"
                
            elif 'count' in question.lower():
                return f"The total number of records is {len(self.df)}"
                
            elif 'columns' in question.lower():
                return f"The columns in the dataset are: {', '.join(self.df.columns)}"
                
            else:
                return "I can help you analyze your data. Try asking about totals, averages, counts, or columns."
                
        except Exception as e:
            return f"Error analyzing data: {str(e)}"
            
    def get_column_analysis(self, column_name):
        """Generate specific analysis for a given column"""
        try:
            if column_name not in self.df.columns:
                return f"Column '{column_name}' not found in the dataset."
                
            column_data = self.df[column_name].describe().to_string()
            
            prompt = f"""Analyze this column '{column_name}' with the following statistics:
            {column_data}
            
            Provide insights about:
            1. The distribution of values
            2. Any potential issues or anomalies
            3. Recommendations for handling this data
            """
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever
            )
            
            return qa_chain.run(prompt)
        except Exception as e:
            return f"Error analyzing column: {str(e)}" 
