import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots

class Visualizer:
    def __init__(self, df):
        self.df = df
        # Try to identify sales amount column
        sales_amount_columns = [col for col in df.columns if 
                              any(term in col.lower() 
                                  for term in ['sale', 'amount', 'revenue', 'total'])]
        self.sales_col = sales_amount_columns[0] if sales_amount_columns else None
        
        # Premium color palette
        self.colors = {
            'primary': '#4A90E2',
            'secondary': '#50E3C2',
            'accent': '#F5A623',
            'background': '#1E1E1E',
            'gradient': ['#4A90E2', '#50E3C2', '#F5A623', '#FF6B6B', '#A463F2']
        }
        # Set default template
        self.template = self._create_custom_template()
        
    def _create_custom_template(self):
        """Create a premium dark template for plots"""
        template = go.layout.Template()
        template.layout = go.Layout(
            paper_bgcolor='rgba(30,30,30,0.8)',
            plot_bgcolor='rgba(30,30,30,0.8)',
            font_color='white',
            font_family='Arial',
            title_font_size=24,
            title_x=0.5,
            title_font_family='Arial',
            legend_bgcolor='rgba(30,30,30,0.8)',
            legend_bordercolor='rgba(255,255,255,0.1)',
            colorway=self.colors['gradient']
        )
        return template
        
    def plot_overview_dashboard(self):
        """Modified overview dashboard to include sales-specific visualizations"""
        if self.df.empty:
            st.warning("No data available for visualization")
            return
        
        # Add sales dashboard
        self.plot_sales_dashboard()
        
        # Keep existing overview visualizations
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) > 0:
            # Create subplot grid
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Distribution Overview", "Missing Values", 
                              "Data Type Distribution", "Value Ranges"),
                specs=[[{"type": "box"}, {"type": "bar"}],
                      [{"type": "pie"}, {"type": "heatmap"}]]
            )
            
            # Box plots
            for i, col in enumerate(numeric_cols[:5]):  # Limit to first 5 columns
                fig.add_trace(
                    go.Box(y=self.df[col], name=col, 
                          fillcolor=self.colors['gradient'][i % len(self.colors['gradient'])],
                          line=dict(color='white')),
                    row=1, col=1
                )
                
            # Missing values
            missing_data = self.df.isnull().sum()
            fig.add_trace(
                go.Bar(
                    x=missing_data.index,
                    y=missing_data.values,
                    marker_color=self.colors['primary'],
                    name="Missing Values"
                ),
                row=1, col=2
            )
            
            # Data type distribution
            dtypes = self.df.dtypes.value_counts()
            fig.add_trace(
                go.Pie(
                    labels=dtypes.index.astype(str),
                    values=dtypes.values,
                    hole=0.5,
                    marker_colors=self.colors['gradient']
                ),
                row=2, col=1
            )
            
            # Value ranges heatmap
            ranges = pd.DataFrame({
                'min': self.df[numeric_cols].min(),
                'max': self.df[numeric_cols].max(),
                'mean': self.df[numeric_cols].mean()
            }).T
            
            fig.add_trace(
                go.Heatmap(
                    z=ranges.values,
                    x=ranges.columns,
                    y=ranges.index,
                    colorscale='Viridis'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                height=800,
                showlegend=False,
                template=self.template,
                title={
                    'text': "Data Overview Dashboard",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            
            # Add gradient background
            fig.update_layout(
                paper_bgcolor='rgba(30,30,30,0.8)',
                plot_bgcolor='rgba(30,30,30,0.8)',
                font_color='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    def plot_correlation_matrix(self):
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns available for correlation analysis")
            return
            
        corr = self.df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            text=np.round(corr, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            template=self.template,
            height=600,
            title={
                'text': "Correlation Matrix",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def plot_statistical_analysis(self):
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns available for statistical analysis")
            return
            
        for col in numeric_cols:
            # Create subplot with shared x-axis
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              vertical_spacing=0.1,
                              subplot_titles=(f"Distribution of {col}", "Box Plot"))
                              
            # Add histogram without KDE
            fig.add_trace(
                go.Histogram(
                    x=self.df[col],
                    name="Distribution",
                    nbinsx=30,
                    marker_color=self.colors['primary'],
                    opacity=0.7
                ),
                row=1, col=1
            )
            
            # Add box plot
            fig.add_trace(
                go.Box(
                    x=self.df[col],
                    name="Box Plot",
                    marker_color=self.colors['secondary']
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                template=self.template,
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics in a modern card layout
            st.markdown("""
                <style>
                .stat-card {
                    background: linear-gradient(135deg, rgba(74,144,226,0.1), rgba(80,227,194,0.1));
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                </style>
            """, unsafe_allow_html=True)
            
            stats = self.df[col].describe()
            cols = st.columns(4)
            
            metrics = [
                ("Mean", f"{stats['mean']:.2f}"),
                ("Median", f"{stats['50%']:.2f}"),
                ("Std Dev", f"{stats['std']:.2f}"),
                ("IQR", f"{stats['75%'] - stats['25%']:.2f}")
            ]
            
            for i, (label, value) in enumerate(metrics):
                with cols[i]:
                    st.markdown(f"""
                        <div class="stat-card">
                            <h3 style="color: {self.colors['gradient'][i]}">{label}</h3>
                            <p style="font-size: 24px; margin: 0;">{value}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
    def plot_ai_recommended_charts(self):
        if self.df.empty:
            st.warning("No data available for visualization")
            return
            
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        # Simple scatter plot without trendline
        if len(numeric_cols) >= 2:
            fig = px.scatter(
                self.df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                template=self.template,
                color_discrete_sequence=self.colors['gradient']
            )
            
            fig.update_layout(
                title="Relationship Analysis",
                height=700
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        # Bubble chart without animation
        if len(numeric_cols) >= 3:
            fig = px.scatter(
                self.df,
                x=numeric_cols[0],
                y=numeric_cols[1],
                size=numeric_cols[2],
                color=categorical_cols[0] if len(categorical_cols) > 0 else None,
                template=self.template,
                size_max=60
            )
            
            fig.update_layout(
                title="Multi-dimensional Analysis",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def plot_sales_dashboard(self):
        """Custom dashboard for sales data"""
        if self.df.empty:
            st.warning("No data available for visualization")
            return
        
        if not self.sales_col:
            st.error("No sales amount column found in the dataset")
            return
        
        # Create tabs for different dashboard sections
        tab1, tab2, tab3 = st.tabs(["Time Analysis", "Performance Metrics", "Product Analysis"])
        
        with tab1:
            # 1. Sales Trends Over Time
            date_columns = [col for col in self.df.columns if 
                           any(date_term in col.lower() 
                               for date_term in ['date', 'time', 'day', 'month', 'year'])]
            
            if date_columns:
                date_col = date_columns[0]
                fig1 = go.Figure()
                
                df_time = self.df.sort_values(date_col).copy()
                df_time[date_col] = pd.to_datetime(df_time[date_col], errors='coerce')
                
                fig1.add_trace(go.Scatter(
                    x=df_time[date_col],
                    y=df_time[self.sales_col],
                    mode='lines+markers',
                    name='Sales Amount',
                    line=dict(color=self.colors['primary']),
                    fill='tonexty'
                ))
                
                fig1.update_layout(
                    title="Sales Trend Over Time",
                    template=self.template,
                    height=400
                )
                
                st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            # Only show region analysis if Region column exists
            with col1:
                if 'Region' in self.df.columns:
                    region_sales = (self.df.groupby('Region')[self.sales_col]
                                   .sum()
                                   .reset_index())
                    
                    fig_region = px.pie(
                        region_sales,
                        values=self.sales_col,
                        names='Region',
                        hole=0.5,
                        color_discrete_sequence=self.colors['gradient']
                    )
                    fig_region.update_layout(
                        title="Sales by Region",
                        template=self.template
                    )
                    st.plotly_chart(fig_region, use_container_width=True)
                
            # Only show manager analysis if Manager column exists
            with col2:
                if 'Manager' in self.df.columns:
                    fig_manager = px.bar(
                        self.df.groupby('Manager')[self.sales_col].sum().reset_index(),
                        x='Manager',
                        y=self.sales_col,
                        color=self.sales_col,
                        color_continuous_scale=self.colors['gradient']
                    )
                    fig_manager.update_layout(
                        title="Sales by Manager",
                        template=self.template
                    )
                    st.plotly_chart(fig_manager, use_container_width=True)
        
        with tab3:
            # Only show product analysis if relevant columns exist
            if 'Item' in self.df.columns:
                col3, col4 = st.columns(2)
                
                with col3:
                    # Product performance
                    product_sales = (self.df.groupby('Item')[self.sales_col]
                                   .sum()
                                   .sort_values(ascending=True)
                                   .reset_index())
                    
                    fig_products = px.bar(
                        product_sales,
                        x=self.sales_col,
                        y='Item',
                        orientation='h',
                        color=self.sales_col,
                        color_continuous_scale=self.colors['gradient']
                    )
                    fig_products.update_layout(
                        title="Sales by Product",
                        template=self.template
                    )
                    st.plotly_chart(fig_products, use_container_width=True)
                
                with col4:
                    if 'Units' in self.df.columns:
                        items_units = (
                            self.df.groupby('Item')['Units']
                            .sum()
                            .sort_values(ascending=True)
                            .reset_index()
                        )
                        
                        fig_items = px.bar(
                            items_units,
                            x='Units',
                            y='Item',
                            orientation='h',
                            title="Units Sold by Item",
                            color='Units',
                            color_continuous_scale=self.colors['gradient']
                        )
                        fig_items.update_layout(template=self.template)
                        st.plotly_chart(fig_items, use_container_width=True)
                    else:
                        st.warning("Missing Units column for product analysis")
            else:
                st.warning("No Item column found in the dataset")

    def plot_distribution_analysis(self):
        """Plot distribution analysis for numeric columns"""
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns available for distribution analysis")
            return
        
        selected_col = st.selectbox("Select column for distribution analysis", numeric_cols)
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=self.df[selected_col],
            name="Distribution",
            nbinsx=30,
            marker_color=self.colors['primary']
        ))
        
        fig.update_layout(
            title=f"Distribution of {selected_col}",
            template=self.template,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show statistics
        stats = self.df[selected_col].describe()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{stats['mean']:.2f}")
        with col2:
            st.metric("Median", f"{stats['50%']:.2f}")
        with col3:
            st.metric("Std Dev", f"{stats['std']:.2f}")
        with col4:
            st.metric("IQR", f"{stats['75%'] - stats['25%']:.2f}")

    def plot_trend_analysis(self):
        """Plot trend analysis for time-series data"""
        # Find date columns
        date_cols = [col for col in self.df.columns if 
                    any(term in col.lower() for term in ['date', 'time', 'day'])]
        
        if not date_cols:
            st.warning("No date columns found for trend analysis")
            return
        
        date_col = st.selectbox("Select date column", date_cols)
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        value_col = st.selectbox("Select value column", numeric_cols)
        
        # Create time series plot
        df_time = self.df.copy()
        df_time[date_col] = pd.to_datetime(df_time[date_col], errors='coerce')
        df_time = df_time.sort_values(date_col)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_time[date_col],
            y=df_time[value_col],
            mode='lines+markers',
            name=value_col,
            line=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title=f"Trend Analysis: {value_col} over Time",
            template=self.template,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)