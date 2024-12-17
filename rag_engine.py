from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv

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
        
    def answer_question(self, question):
        """Answer specific questions about the data"""
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever
            )
            
            enhanced_question = f"""Based on the dataset, please answer this question: {question}
            
            Provide specific details and numbers when relevant. If the answer requires assumptions, please state them."""
            
            return qa_chain.run(enhanced_question)
        except Exception as e:
            return f"Error answering question: {str(e)}"
            
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