import pandas as pd
import numpy as np
from io import BytesIO

class DataProcessor:
    def __init__(self, df):
        self.df = self._process_input(df)
        
    def _process_input(self, file_input):
        """Safely process input file with various encodings"""
        try:
            # If input is already a DataFrame
            if isinstance(file_input, pd.DataFrame):
                return file_input
                
            # Try reading with different encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    if hasattr(file_input, 'name'):  # If it's a file upload
                        if file_input.name.endswith(('.xlsx', '.xls')):
                            df = pd.read_excel(file_input)
                        elif file_input.name.endswith('.csv'):
                            df = pd.read_csv(file_input, encoding=encoding)
                        
                        # Verify DataFrame is not empty
                        if df.empty:
                            raise ValueError("The uploaded file contains no data")
                        if len(df.columns) == 0:
                            raise ValueError("The uploaded file contains no columns")
                        return df
                            
                    else:  # If it's a file path or buffer
                        if str(file_input).endswith(('.xlsx', '.xls')):
                            return pd.read_excel(file_input)
                        else:
                            return pd.read_csv(file_input, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error with encoding {encoding}: {str(e)}")
                    continue
                    
            # If all encodings fail, try binary read for Excel
            try:
                buffer = BytesIO(file_input.read())
                df = pd.read_excel(buffer)
                if df.empty or len(df.columns) == 0:
                    raise ValueError("The uploaded file contains no data")
                return df
            except:
                raise ValueError("Unable to process file with any supported encoding")
                
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
        
    def get_basic_stats(self):
        """Get basic statistics about the dataset"""
        if self.df.empty or len(self.df.columns) == 0:
            return {
                'error': 'No data available for analysis'
            }
            
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().sum(),
            'duplicates': self.df.duplicated().sum(),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_types': dict(self.df.dtypes.value_counts())
        }
        
    def get_data_quality_metrics(self):
        """Get detailed data quality metrics for each column"""
        if self.df.empty or len(self.df.columns) == 0:
            return {'error': 'No data available for analysis'}
            
        metrics = {}
        for column in self.df.columns:
            metrics[column] = {
                'missing': self.df[column].isnull().sum(),
                'missing_percentage': f"{(self.df[column].isnull().sum() / len(self.df)) * 100:.2f}%",
                'unique_values': self.df[column].nunique(),
                'data_type': str(self.df[column].dtype),
                'sample_values': self.df[column].dropna().head(3).tolist() if not self.df[column].empty else []
            }
            
            # Add numeric column specific metrics
            if np.issubdtype(self.df[column].dtype, np.number):
                metrics[column].update({
                    'mean': f"{self.df[column].mean():.2f}" if not self.df[column].empty else "N/A",
                    'std': f"{self.df[column].std():.2f}" if not self.df[column].empty else "N/A",
                    'min': self.df[column].min() if not self.df[column].empty else "N/A",
                    'max': self.df[column].max() if not self.df[column].empty else "N/A"
                })
                
        return metrics
        
    def get_detailed_stats(self):
        """Get detailed statistical analysis"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return pd.DataFrame({
                'message': ['No numeric columns found in the dataset'],
                'recommendation': ['Consider converting appropriate columns to numeric type']
            })
            
        stats = self.df[numeric_cols].describe()
        
        # Add additional statistics
        if not stats.empty:
            stats.loc['skew'] = self.df[numeric_cols].skew()
            stats.loc['kurtosis'] = self.df[numeric_cols].kurtosis()
        
        return stats
        
    def get_correlations(self):
        """Get correlation matrix for numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return pd.DataFrame({
                'message': ['No numeric columns found for correlation analysis']
            })
            
        return self.df[numeric_cols].corr()
        
    def clean_column_names(self):
        """Clean and standardize column names"""
        if self.df.empty or len(self.df.columns) == 0:
            return []
            
        self.df.columns = self.df.columns.str.strip()
        self.df.columns = self.df.columns.str.lower()
        self.df.columns = self.df.columns.str.replace(' ', '_')
        return self.df.columns.tolist()
        
    def handle_missing_values(self, strategy='mean'):
        """Handle missing values with specified strategy"""
        if self.df.empty or len(self.df.columns) == 0:
            return self.df
            
        if strategy == 'mean':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == 'median':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        elif strategy == 'mode':
            self.df = self.df.fillna(self.df.mode().iloc[0] if not self.df.empty else pd.Series())
        elif strategy == 'drop':
            self.df = self.df.dropna()
        
        return self.df