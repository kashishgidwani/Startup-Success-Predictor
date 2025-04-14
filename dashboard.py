import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re

def create_exploded_dataframe(df, split_column, value_columns):
    # Create a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()
    
    # Split the text column and explode it
    exploded = df_copy[split_column].str.split(',').explode()
    
    # Create a new DataFrame with the exploded values
    result_df = pd.DataFrame({
        split_column: exploded.str.strip()
    })
    
    # Add each value column with proper repetition
    for col in value_columns:
        # Get the lengths of each split
        lengths = df_copy[split_column].str.split(',').str.len()
        # Repeat the values according to the lengths
        repeated_values = df_copy[col].repeat(lengths).reset_index(drop=True)
        result_df[col] = repeated_values
    
    return result_df

# Set page configuration
st.set_page_config(
    page_title="Startup Success Blueprint Dashboard",
    layout="wide"
)

# Custom CSS for better spacing and layout
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-factor {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🚀 Startup Success Blueprint Dashboard")
st.markdown("""
    Analyze successful unicorns and learn from failed startups across 5 major sectors in India.
    Compare metrics, understand key differentiators, and get insights for your startup journey.
    """)

# Load and preprocess data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('unicorncompanies.csv')
        
        # Remove % signs from percentage columns and convert to float
        percentage_columns = [
            'Profit Margin %', 'Marketing Spend %', 'Customer Growth %',
            'Social Engagement %', 'Repeat Purchase %'
        ]
        
        for col in percentage_columns:
            # Convert to string first to handle any non-string values
            df[col] = df[col].astype(str)
            # Remove % sign and convert to float
            df[col] = df[col].str.rstrip('%').astype(float)
        
        # Convert numeric columns and handle NaN values
        numeric_columns = [
            'Initial Funding (M$)', 'Total Funding (M$)', 'Annual Revenue (M$)',
            'CAC (M$)', 'LTV (M$)', 'NPS Score', 'Web Traffic (M)'
        ]
        
        for col in numeric_columns:
            # Convert to string first to handle any non-string values
            df[col] = df[col].astype(str)
            # Remove $ and M signs and convert to float
            df[col] = df[col].str.replace('$', '').str.replace('M', '').astype(float)
            # Replace NaN with median of the column
            df[col] = df[col].fillna(df[col].median())
            # Ensure all values are non-negative
            df[col] = df[col].clip(lower=0)
        
        # Create normalized columns for visualization
        df['Normalized Growth'] = (df['Customer Growth %'] - df['Customer Growth %'].min()) / (df['Customer Growth %'].max() - df['Customer Growth %'].min()) * 100
        df['Normalized Revenue'] = (df['Annual Revenue (M$)'] - df['Annual Revenue (M$)'].min()) / (df['Annual Revenue (M$)'].max() - df['Annual Revenue (M$)'].min()) * 100
        
        # Ensure normalized values are not NaN
        df['Normalized Growth'] = df['Normalized Growth'].fillna(50)
        df['Normalized Revenue'] = df['Normalized Revenue'].fillna(50)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Sidebar filters
st.sidebar.title("Filters")
sector = st.sidebar.selectbox(
    "Select Sector",
    ["All", "Investment", "Food", "Financial", "Fashion", "Medicine"]
)

# Filter data based on sector
if sector != "All":
    filtered_data = st.session_state.data[st.session_state.data['Unique name'] == sector].copy()
else:
    filtered_data = st.session_state.data.copy()

# Main content
if st.session_state.data is not None:
    # Overview Metrics
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(filtered_data))
    
    with col2:
        avg_funding = filtered_data['Total Funding (M$)'].mean()
        st.metric("Average Funding", f"${avg_funding:.2f}M")
    
    with col3:
        success_rate = (filtered_data['Break-even Status'] == 'Achieved').mean() * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        avg_revenue = filtered_data['Annual Revenue (M$)'].mean()
        st.metric("Average Revenue", f"${avg_revenue:.2f}M")

    # Tab-based layout
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance Analysis", "🎯 Success Factors", "🔍 Company Comparison", "🔮 Strategy Predictor"])

    with tab1:
        st.header("Performance Analysis")
        
        # Financial Growth Analysis
        st.subheader("Financial Growth Analysis")
        
        # Revenue Trends
        col1, col2 = st.columns(2)
        with col1:
            # Group by sector and calculate average revenue
            sector_revenue = filtered_data.groupby(['Unique name', 'Founding Year'])['Annual Revenue (M$)'].mean().reset_index()
            fig = px.line(sector_revenue,
                        x='Founding Year',
                        y='Annual Revenue (M$)',
                        color='Unique name',
                        title='Revenue Growth Trends by Sector',
                        markers=True,
                        line_shape='spline')
            fig.update_layout(
                showlegend=True,
                hovermode='x unified',
                xaxis_title='Year',
                yaxis_title='Average Revenue (M$)',
                legend_title='Sector'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Create a melted dataframe for funding comparison
            funding_data = filtered_data.melt(
                id_vars=['Unique name'],
                value_vars=['Initial Funding (M$)', 'Total Funding (M$)'],
                var_name='Funding Type',
                value_name='Amount'
            )
            # Calculate average funding by sector
            sector_funding = funding_data.groupby(['Unique name', 'Funding Type'])['Amount'].mean().reset_index()
            fig = px.bar(sector_funding,
                        x='Unique name',
                        y='Amount',
                        color='Funding Type',
                        title='Average Funding by Sector',
                        barmode='group')
            fig.update_layout(
                showlegend=True,
                xaxis_title='Sector',
                yaxis_title='Average Amount (M$)',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Burn Rate Analysis
        st.subheader("Burn Rate Analysis by Sector")
        
        # Calculate burn rate: (Total Funding - Annual Revenue) / Total Funding
        filtered_data['Burn Rate %'] = ((filtered_data['Total Funding (M$)'] - filtered_data['Annual Revenue (M$)']) / 
                                      filtered_data['Total Funding (M$)'] * 100).round(1)
        
        # Replace infinite values with 100 (for companies with zero funding)
        filtered_data['Burn Rate %'] = filtered_data['Burn Rate %'].replace([np.inf, -np.inf], 100)
        
        # Create a box plot for burn rates by sector
        fig = px.box(filtered_data,
                    x='Unique name',
                    y='Burn Rate %',
                    color='Break-even Status',
                    title='Burn Rate Distribution by Sector',
                    points="all",
                    hover_data=['Company Name', 'Total Funding (M$)', 'Annual Revenue (M$)'])
        
        fig.update_layout(
            showlegend=True,
            xaxis_title='Sector',
            yaxis_title='Burn Rate (%)',
            hovermode='closest',
            yaxis=dict(range=[0, 100])  # Set y-axis range from 0 to 100%
        )
        
        # Add annotations for key insights
        fig.add_annotation(
            text="Lower burn rate indicates better financial health",
            xref="paper", yref="paper",
            x=0.5, y=1.1,
            showarrow=False,
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a table showing detailed burn rate analysis
        st.markdown("### Detailed Burn Rate Analysis")
        burn_rate_table = filtered_data[['Company Name', 'Unique name', 'Total Funding (M$)', 
                                       'Annual Revenue (M$)', 'Burn Rate %', 'Break-even Status']]
        burn_rate_table = burn_rate_table.sort_values('Burn Rate %', ascending=False)
        st.dataframe(burn_rate_table, use_container_width=True)
        
        # Revenue vs Funding Analysis
        st.subheader("Revenue vs Funding Analysis")
        col1, col2 = st.columns(2)
        with col1:
            size_data = filtered_data['Normalized Growth'].fillna(50)
            fig = px.scatter(filtered_data,
                           x='Total Funding (M$)',
                           y='Annual Revenue (M$)',
                           color='Break-even Status',
                           size=size_data,
                           hover_name='Company Name',
                           title='Revenue vs Funding Analysis',
                           color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(
                showlegend=True,
                xaxis_title='Total Funding (M$)',
                yaxis_title='Annual Revenue (M$)',
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            size_data = filtered_data['Normalized Revenue'].fillna(50)
            fig = px.scatter(filtered_data,
                           x='CAC (M$)',
                           y='LTV (M$)',
                           color='Break-even Status',
                           size=size_data,
                           hover_name='Company Name',
                           title='CAC vs LTV Analysis',
                           color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                showlegend=True,
                xaxis_title='CAC (M$)',
                yaxis_title='LTV (M$)',
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Growth Metrics Distribution
        st.subheader("Growth Metrics Distribution")
        growth_metrics = pd.DataFrame({
            'Customer Growth': filtered_data['Customer Growth %'],
            'Social Engagement': filtered_data['Social Engagement %'],
            'Repeat Purchase': filtered_data['Repeat Purchase %'],
            'Web Traffic': filtered_data['Web Traffic (M)'],
            'NPS Score': filtered_data['NPS Score']
        })
        
        fig = go.Figure()
        for col in growth_metrics.columns:
            fig.add_trace(go.Box(
                y=growth_metrics[col],
                name=col,
                boxpoints='outliers',
                marker_color='rgb(31,119,180)',
                line_color='rgb(31,119,180)'
            ))
        
        fig.update_layout(
            title='Distribution of Growth Metrics',
            yaxis_title='Values',
            boxmode='group',
            showlegend=True,
            height=600,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Social & Brand Engagement Analysis
        st.subheader("Social & Brand Engagement Analysis")
        
        # Engagement Metrics
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(filtered_data,
                           x='Social Engagement %',
                           y='NPS Score',
                           color='Break-even Status',
                           size='Web Traffic (M)',
                           hover_name='Company Name',
                           title='Social Engagement vs NPS',
                           color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(
                showlegend=True,
                xaxis_title='Social Engagement (%)',
                yaxis_title='NPS Score',
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(filtered_data,
                           x='Repeat Purchase %',
                           y='Customer Growth %',
                           color='Break-even Status',
                           size='Web Traffic (M)',
                           hover_name='Company Name',
                           title='Repeat Purchase vs Growth',
                           color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                showlegend=True,
                xaxis_title='Repeat Purchase (%)',
                yaxis_title='Customer Growth (%)',
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Engagement Heatmap
        st.subheader("Engagement Metrics Heatmap")
        engagement_metrics = filtered_data[['Social Engagement %', 'NPS Score', 'Repeat Purchase %', 'Customer Growth %']]
        fig = px.imshow(engagement_metrics.corr(),
                       title='Engagement Metrics Correlation',
                       color_continuous_scale='RdBu',
                       text_auto=True)
        fig.update_layout(
            xaxis_title='Metrics',
            yaxis_title='Metrics',
            hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Share of Voice Analysis
        st.subheader("Share of Voice Analysis")
        fig = px.scatter(filtered_data,
                        x='Web Traffic (M)',
                        y='Social Engagement %',
                        color='Break-even Status',
                        size='Customer Growth %',
                        hover_name='Company Name',
                        title='Web Traffic vs Social Engagement',
                        color_discrete_sequence=px.colors.qualitative.Set1)
        fig.update_layout(
            showlegend=True,
            xaxis_title='Web Traffic (M)',
            yaxis_title='Social Engagement (%)',
            hovermode='closest'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Success Factors Analysis")
        st.markdown("""
        Analyze key factors that contribute to startup success across different dimensions:
        1. Revenue Generation Strategies
        2. Innovation & Growth
        3. Customer Engagement & Brand Building
        """)
        
        # 1. Revenue Generation Strategies
        st.subheader("1. Revenue Generation Strategies")
        st.markdown("Understand which monetization approaches lead to better financial outcomes.")
        
        # Create word cloud and metrics table in a single column for better focus
        # Word Cloud for Monetization Strategies
        strategies = filtered_data['Monetization Strategy'].str.split(',').explode().str.strip()
        strategy_counts = strategies.value_counts()
        
        # Create word cloud with frequency-based sizing
        wordcloud = WordCloud(width=1000, height=400, background_color='white').generate_from_frequencies(strategy_counts)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        
        # Add strategy effectiveness metrics
        value_columns = ['Company Name', 'Unique name', 'Annual Revenue (M$)', 'Profit Margin %', 
                        'Customer Growth %', 'Repeat Purchase %']
        strategy_data = create_exploded_dataframe(filtered_data, 'Monetization Strategy', value_columns)
        
        strategy_data = strategy_data.rename(columns={
            'Monetization Strategy': 'Strategy',
            'Company Name': 'Company',
            'Unique name': 'Sector'
        })
        
        strategy_metrics = strategy_data.groupby('Strategy').agg({
            'Annual Revenue (M$)': 'mean',
            'Profit Margin %': 'mean',
            'Customer Growth %': 'mean',
            'Repeat Purchase %': 'mean'
        }).round(2)
        
        st.markdown("#### Strategy Performance Metrics")
        st.markdown("*Higher values (green) indicate better performance*")
        st.dataframe(strategy_metrics.style.background_gradient(cmap='RdYlGn'), use_container_width=True)

        # 2. Innovation & Growth
        st.subheader("2. Innovation & Growth")
        st.markdown("Explore how different innovations impact business growth and revenue.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Key Innovations Treemap
            st.subheader("Key Innovations Impact")
            innovation_exploded = create_exploded_dataframe(filtered_data, 'Key Innovations', ['Annual Revenue (M$)', 'Customer Growth %'])
            innovation_exploded['Annual Revenue (M$)'] = pd.to_numeric(innovation_exploded['Annual Revenue (M$)'], errors='coerce')
            innovation_exploded['Customer Growth %'] = pd.to_numeric(innovation_exploded['Customer Growth %'], errors='coerce')

            # Filter out rows with zero or negative revenue
            innovation_exploded = innovation_exploded[innovation_exploded['Annual Revenue (M$)'] > 0]

            if not innovation_exploded.empty:
                # Calculate average metrics for each innovation
                innovation_metrics = innovation_exploded.groupby('Key Innovations').agg({
                    'Annual Revenue (M$)': 'mean',
                    'Customer Growth %': 'mean'
                }).reset_index()
                
                # Ensure we have valid data for the treemap
                if innovation_metrics['Annual Revenue (M$)'].sum() > 0:
                    fig = px.treemap(
                        innovation_metrics,
                        path=['Key Innovations'],
                        values='Annual Revenue (M$)',
                        color='Customer Growth %',
                        color_continuous_scale='RdYlGn',
                        title='Innovation Impact on Revenue and Growth'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No valid revenue data available for treemap visualization.")
            else:
                st.warning("No valid innovation data available for visualization.")
        
        with col2:
            # Pivot Moments Analysis
            value_columns = ['Company Name', 'Annual Revenue (M$)', 'Customer Growth %', 'Profit Margin %']
            pivot_data = create_exploded_dataframe(filtered_data, 'Pivot Moments', value_columns)
            
            pivot_data = pivot_data.rename(columns={
                'Pivot Moments': 'Pivot',
                'Company Name': 'Company'
            })
            
            pivot_metrics = pivot_data.groupby('Pivot').agg({
                'Annual Revenue (M$)': 'mean',
                'Customer Growth %': 'mean',
                'Profit Margin %': 'mean'
            }).round(2)
            
            fig = px.bar(
                pivot_metrics.reset_index(),
                x='Pivot',
                y=['Annual Revenue (M$)', 'Customer Growth %', 'Profit Margin %'],
                title='Impact of Strategic Pivots',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

        # 3. Customer Engagement & Brand Building
        st.subheader("3. Customer Engagement & Brand Building")
        st.markdown("Analyze community engagement and brand storytelling effectiveness.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Community Initiatives
            value_columns = ['Company Name', 'Repeat Purchase %', 'NPS Score', 'Social Engagement %']
            community_data = create_exploded_dataframe(filtered_data, 'Community Initiatives', value_columns)
            
            community_data = community_data.rename(columns={
                'Community Initiatives': 'Initiative',
                'Company Name': 'Company'
            })
            
            initiative_metrics = community_data.groupby('Initiative').agg({
                'Repeat Purchase %': 'mean',
                'NPS Score': 'mean',
                'Social Engagement %': 'mean'
            }).round(2)
            
            st.markdown("#### Community Engagement Impact")
            st.dataframe(initiative_metrics.style.background_gradient(cmap='RdYlGn'), use_container_width=True)
        
        with col2:
            # Brand Storytelling
            value_columns = ['Company Name', 'Web Traffic (M)', 'Social Engagement %', 'Customer Growth %']
            storytelling_data = create_exploded_dataframe(filtered_data, 'Brand Storytelling', value_columns)
            
            storytelling_data = storytelling_data.rename(columns={
                'Brand Storytelling': 'Storytelling',
                'Company Name': 'Company'
            })
            
            storytelling_metrics = storytelling_data.groupby('Storytelling').agg({
                'Web Traffic (M)': 'mean',
                'Social Engagement %': 'mean',
                'Customer Growth %': 'mean'
            }).round(2)
            
            st.markdown("#### Brand Storytelling Impact")
            st.dataframe(storytelling_metrics.style.background_gradient(cmap='RdYlGn'), use_container_width=True)

        # Key Insights Summary
        st.subheader("Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Top Performing Strategies:**
            - Most successful monetization approaches
            - Highest impact innovations
            - Most effective community initiatives
            """)
            
            # Get top performers
            top_revenue = strategy_metrics.nlargest(3, 'Annual Revenue (M$)').index.tolist()
            top_innovations = innovation_metrics.nlargest(3, 'Customer Growth %').index.tolist()
            top_initiatives = initiative_metrics.nlargest(3, 'NPS Score').index.tolist()
            
            st.markdown("##### Top Revenue Strategies")
            for i, strategy in enumerate(top_revenue, 1):
                st.markdown(f"{i}. {strategy}")
            
            st.markdown("##### Most Impactful Innovations")
            for i, innovation in enumerate(top_innovations, 1):
                st.markdown(f"{i}. {innovation}")
            
            st.markdown("##### Best Community Initiatives")
            for i, initiative in enumerate(top_initiatives, 1):
                st.markdown(f"{i}. {initiative}")
        
        with col2:
            st.markdown("""
            **Growth Indicators:**
            - Customer engagement correlation
            - Revenue growth patterns
            - Brand impact metrics
            """)
            
            # Calculate correlations
            engagement_metrics = pd.DataFrame({
                'Social Engagement': storytelling_metrics['Social Engagement %'],
                'Customer Growth': storytelling_metrics['Customer Growth %'],
                'Web Traffic': storytelling_metrics['Web Traffic (M)']
            })
            
            correlation_matrix = engagement_metrics.corr()
            
            fig = px.imshow(
                correlation_matrix,
                color_continuous_scale='RdBu',
                title='Growth Metrics Correlation'
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("Company Comparison")
        
        # Company selector
        companies = filtered_data['Company Name'].unique()
        selected_companies = st.multiselect(
            "Select Companies to Compare",
            companies,
            default=companies[:2] if len(companies) >= 2 else companies
        )
        
        if selected_companies:
            comparison_data = filtered_data[filtered_data['Company Name'].isin(selected_companies)]
            
            # Metrics comparison
            metrics = ['Total Funding (M$)', 'Annual Revenue (M$)', 'Profit Margin %',
                      'Customer Growth %', 'NPS Score', 'Repeat Purchase %']
            
            fig = go.Figure()
            for company in selected_companies:
                company_data = comparison_data[comparison_data['Company Name'] == company]
                fig.add_trace(go.Bar(
                    name=company,
                    x=metrics,
                    y=[company_data[metric].values[0] for metric in metrics],
                    text=[f"{company_data[metric].values[0]:.1f}" for metric in metrics],
                    textposition='auto',
                ))
            
            fig.update_layout(
                barmode='group',
                title='Company Metrics Comparison',
                xaxis_title='Metrics',
                yaxis_title='Values',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed comparison table
            st.subheader("Detailed Comparison")
            comparison_table = comparison_data[['Company Name', 'Founding Year', 'Total Funding (M$)',
                                             'Annual Revenue (M$)', 'Profit Margin %', 'Customer Growth %',
                                             'NPS Score', 'Repeat Purchase %', 'Break-even Status']]
            st.dataframe(comparison_table, use_container_width=True)

    with tab4:
        st.header("Startup Strategy Predictor")
        st.markdown("""
        Enter your startup's metrics to get personalized recommendations:
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            initial_funding = st.number_input("Initial Funding (M$)", min_value=0.0)
            marketing_spend = st.number_input("Marketing Spend %", min_value=0.0, max_value=100.0)
            cac = st.number_input("Customer Acquisition Cost (M$)", min_value=0.0)
            ltv = st.number_input("Lifetime Value (M$)", min_value=0.0)
        
        with col2:
            growth_rate = st.number_input("Customer Growth Rate (%)", min_value=0.0, max_value=100.0)
            nps = st.number_input("NPS Score", min_value=0.0, max_value=100.0)
            repeat_purchase = st.number_input("Repeat Purchase Rate (%)", min_value=0.0, max_value=100.0)
            profit_margin = st.number_input("Profit Margin (%)", min_value=0.0, max_value=100.0)
        
            
        if st.button("Analyze Strategy"):
            # Calculate scores
            funding_score = 2 if initial_funding > 1 else 1
            marketing_score = 2 if marketing_spend < 30 else 1
            cac_ltv_score = 2 if (ltv/cac) > 3 else (1 if (ltv/cac) > 1.5 else 0) if cac > 0 else 0
            growth_score = 2 if growth_rate > 40 else (1 if growth_rate > 20 else 0)
            nps_score = 2 if nps > 70 else (1 if nps > 50 else 0)
            repeat_score = 2 if repeat_purchase > 60 else (1 if repeat_purchase > 30 else 0)
            margin_score = 2 if profit_margin > 20 else (1 if profit_margin > 10 else 0)
            
            total_score = (funding_score + marketing_score + cac_ltv_score + 
                          growth_score + nps_score + repeat_score + margin_score)
            viability_score = (total_score / 14) * 100
            
            # Visualize score breakdown
            scores = {
                'Funding': funding_score,
                'Marketing': marketing_score,
                'CAC/LTV': cac_ltv_score,
                'Growth': growth_score,
                'NPS': nps_score,
                'Repeat Purchase': repeat_score,
                'Profit Margin': margin_score
            }
            
            fig = go.Figure(go.Bar(
                x=list(scores.keys()),
                y=list(scores.values()),
                text=[f"{score}/2" for score in scores.values()],
                textposition='auto',
            ))
            fig.update_layout(
                title='Strategy Score Breakdown',
                xaxis_title='Metrics',
                yaxis_title='Score (out of 2)',
                yaxis=dict(range=[0, 2])
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Strategy Viability Score", f"{viability_score:.1f}%")
            
            # Recommendations
            st.subheader("Recommendations")
            
            if viability_score >= 70:
                st.success("Strong Strategy: Your startup shows excellent potential!")
                st.markdown("""
                **Key Strengths:**
                - Strong unit economics
                - Efficient marketing spend
                - High customer satisfaction
                - Good growth potential
                
                **Next Steps:**
                - Focus on scaling operations
                - Consider geographic expansion
                - Build strategic partnerships
                """)
            elif viability_score >= 40:
                st.warning("Moderate Strategy: Some areas need improvement")
                st.markdown("""
                **Areas for Improvement:**
                - Optimize marketing spend
                - Focus on customer retention
                - Improve unit economics
                - Consider strategic pivots
                
                **Action Items:**
                - Review CAC/LTV ratio
                - Enhance customer experience
                - Explore new revenue streams
                """)
            else:
                st.error("Weak Strategy: Significant improvements needed")
                st.markdown("""
                **Critical Issues:**
                - Poor unit economics
                - High customer acquisition costs
                - Low customer satisfaction
                - Weak growth metrics
                
                **Urgent Actions:**
                - Reassess business model
                - Reduce customer acquisition costs
                - Improve product-market fit
                - Consider strategic partnerships
                """)
            
            # Sector-specific insights
            if sector != "All":
                sector_data = filtered_data[filtered_data['Unique name'] == sector]
                st.subheader(f"Sector-Specific Insights for {sector}")
                
                # Calculate sector benchmarks
                sector_benchmarks = {
                    'Marketing Spend': sector_data['Marketing Spend %'].mean(),
                    'Profit Margin': sector_data['Profit Margin %'].mean(),
                    'Growth Rate': sector_data['Customer Growth %'].mean(),
                    'NPS': sector_data['NPS Score'].mean()
                }
                
                # Compare with user inputs
                st.markdown("""
                **How you compare with sector averages:**
                """)
                for metric, benchmark in sector_benchmarks.items():
                    user_value = locals().get(metric.lower().replace(' ', '_'))
                    if user_value is not None:
                        diff = user_value - benchmark
                        if diff > 0:
                            st.success(f"{metric}: {diff:.1f}% above sector average")
                        elif diff < 0:
                            st.error(f"{metric}: {abs(diff):.1f}% below sector average")
                        else:
                            st.info(f"{metric}: Matches sector average")
    
else:
    st.error("Please ensure the CSV file is properly formatted and accessible.") 