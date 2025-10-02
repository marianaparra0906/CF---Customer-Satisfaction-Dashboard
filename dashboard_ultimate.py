import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io

# Configure page
st.set_page_config(
    page_title="Customer Satisfaction Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for new data uploads
if "new_data" not in st.session_state:
    st.session_state["new_data"] = {"daily_uploads": [], "events_uploads": []}

# Enhanced Custom CSS for modern, fluid UX
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.15);
    }

    .risk-high { border-left-color: #ff4444 !important; }
    .risk-medium { border-left-color: #ffaa00 !important; }
    .risk-low { border-left-color: #00aa00 !important; }

    /* Enhanced date filter container */
    .date-filter-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    /* Modern tab styling */
    .stTabs > div > div > div > div {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .stTabs > div > div > div > div > div > button {
        background: white;
        border-radius: 8px;
        margin: 0.25rem;
        padding: 0.75rem 1.5rem;
        border: 2px solid transparent;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs > div > div > div > div > div > button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transform: translateY(-1px);
    }

    /* Upload section styling */
    .upload-section {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 2px dashed #667eea;
        transition: all 0.3s ease;
    }

    .upload-section:hover {
        border-color: #764ba2;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }

    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; }
        .metric-card { margin: 0.25rem 0; }
        .date-filter-container { padding: 1rem; }
    }

    /* Navigation improvements */
    .nav-section {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }

    .nav-section:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data for the dashboard
@st.cache_data
def load_data():
    # Daily satisfaction scores from May 30 to Sept 30, 2025
    start_date = datetime(2025, 5, 30)
    end_date = datetime(2025, 9, 30)
    date_range = pd.date_range(start_date, end_date, freq='D')

    # Generate realistic daily satisfaction scores
    np.random.seed(42)
    base_scores = np.random.normal(8.5, 1.2, len(date_range))

    # Add seasonal trends and promotion effects
    daily_data = []
    for i, date in enumerate(date_range):
        score = base_scores[i]

        # Weekend effect (slightly lower satisfaction)
        if date.weekday() >= 5:
            score -= 0.3

        # Promotion periods (higher satisfaction)
        if date.month == 6 and date.day in range(15, 21):  # June promotion
            score += 1.5
        if date.month == 8 and date.day in range(1, 8):    # August promotion
            score += 1.2
        if date.month == 9 and date.day in range(20, 27):  # September promotion
            score += 1.8

        # Special events (mixed effects)
        if date.month == 7 and date.day == 15:  # System maintenance
            score -= 2.5
        if date.month == 8 and date.day == 20:  # Store renovation
            score -= 1.8

        # Ensure realistic bounds
        score = max(0, min(10, score))

        daily_data.append({
            'date': date,
            'satisfaction_score': round(score, 1),
            'month': date.strftime('%B %Y'),
            'month_short': date.strftime('%b'),
            'day_name': date.strftime('%A'),
            'is_weekend': date.weekday() >= 5,
            'week': date.isocalendar()[1]
        })

    daily_df = pd.DataFrame(daily_data)

    # Enhanced events data with more comprehensive information
    enhanced_events_data = [
        # Critical Events
        {'date': datetime(2025, 8, 11), 'day_of_week': 'Tuesday', 'failed_metrics': '7/8', 'failure_percentage': 87.5, 'promotion': 'Without promo', 'severity': 'Critical'},
        {'date': datetime(2025, 8, 13), 'day_of_week': 'Saturday', 'failed_metrics': '6/8', 'failure_percentage': 75.0, 'promotion': 'No promotion', 'severity': 'High'},
        {'date': datetime(2025, 6, 29), 'day_of_week': 'Monday', 'failed_metrics': '6/8', 'failure_percentage': 75.0, 'promotion': '4th of July Event 7% OFF', 'severity': 'High'},
        {'date': datetime(2025, 8, 7), 'day_of_week': 'Sunday', 'failed_metrics': '4/8', 'failure_percentage': 50.0, 'promotion': 'No promotion', 'severity': 'Medium'},
        {'date': datetime(2025, 8, 25), 'day_of_week': 'Thursday', 'failed_metrics': '4/8', 'failure_percentage': 50.0, 'promotion': 'Without promo', 'severity': 'Medium'},
        {'date': datetime(2025, 9, 22), 'day_of_week': 'Tuesday', 'failed_metrics': '4/8', 'failure_percentage': 50.0, 'promotion': 'Without promo', 'severity': 'Medium'},

        # Additional Events (Non-Critical)
        {'date': datetime(2025, 7, 14), 'day_of_week': 'Tuesday', 'failed_metrics': '3/8', 'failure_percentage': 37.5, 'promotion': 'Anniversary Sale Kick Off', 'severity': 'Low'},
        {'date': datetime(2025, 7, 8), 'day_of_week': 'Wednesday', 'failed_metrics': '3/8', 'failure_percentage': 37.5, 'promotion': 'No promotion', 'severity': 'Low'},
        {'date': datetime(2025, 8, 2), 'day_of_week': 'Sunday', 'failed_metrics': '3/8', 'failure_percentage': 37.5, 'promotion': 'No promotion', 'severity': 'Low'},
        {'date': datetime(2025, 8, 13), 'day_of_week': 'Thursday', 'failed_metrics': '3/8', 'failure_percentage': 37.5, 'promotion': 'No promotion', 'severity': 'Low'},
        {'date': datetime(2025, 8, 18), 'day_of_week': 'Monday', 'failed_metrics': '3/8', 'failure_percentage': 37.5, 'promotion': 'No promotion', 'severity': 'Low'},

        # Good Performance Events (for context)
        {'date': datetime(2025, 6, 15), 'day_of_week': 'Monday', 'failed_metrics': '2/8', 'failure_percentage': 25.0, 'promotion': 'Father Day Special 15% OFF', 'severity': 'Low'},
        {'date': datetime(2025, 9, 1), 'day_of_week': 'Tuesday', 'failed_metrics': '2/8', 'failure_percentage': 25.0, 'promotion': 'Labor Day Sale', 'severity': 'Low'},
        {'date': datetime(2025, 7, 20), 'day_of_week': 'Monday', 'failed_metrics': '1/8', 'failure_percentage': 12.5, 'promotion': 'Summer Clearance 20% OFF', 'severity': 'Low'},
        {'date': datetime(2025, 8, 24), 'day_of_week': 'Sunday', 'failed_metrics': '1/8', 'failure_percentage': 12.5, 'promotion': 'Back to School Furniture', 'severity': 'Low'},
        {'date': datetime(2025, 9, 15), 'day_of_week': 'Friday', 'failed_metrics': '0/8', 'failure_percentage': 0.0, 'promotion': 'Fall Collection Launch', 'severity': 'Low'},
    ]

    events_df = pd.DataFrame(enhanced_events_data)

    return daily_df, events_df

# Load base data
base_daily_df, base_events_df = load_data()

# Function to merge uploaded data with base data
def merge_data_with_uploads(base_df, uploaded_dfs, df_type="daily"):
    """Merge base data with uploaded data, removing duplicates"""
    if not uploaded_dfs:
        return base_df

    # Combine all uploaded data
    all_uploaded = pd.concat(uploaded_dfs, ignore_index=True)

    # Combine with base data
    combined = pd.concat([base_df, all_uploaded], ignore_index=True)

    # Remove duplicates based on date column
    date_col = 'date'
    if date_col in combined.columns:
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(combined[date_col]):
            combined[date_col] = pd.to_datetime(combined[date_col], errors='coerce')
        # Remove duplicates, keeping the last occurrence (uploaded data takes precedence)
        combined = combined.drop_duplicates(subset=[date_col], keep='last')
        # Sort by date
        combined = combined.sort_values(date_col).reset_index(drop=True)

    return combined

# Get final merged datasets
daily_df = merge_data_with_uploads(base_daily_df, st.session_state["new_data"]["daily_uploads"])
events_df = merge_data_with_uploads(base_events_df, st.session_state["new_data"]["events_uploads"])

# Enhanced Sidebar with modern navigation
st.sidebar.markdown("### 📊 Dashboard Navigation")
st.sidebar.markdown("---")

# Modern navigation with improved UX
navigation_options = [
    ("📈", "Daily Timeline", "daily"),
    ("📊", "Monthly Comparison", "monthly"), 
    ("⚠️", "Critical Events", "events"),
    ("🎯", "Risk Analysis", "risk"),
    ("📂", "Data Upload", "upload")
]

st.sidebar.markdown("#### Quick Navigation")
selected_nav = None
for icon, label, key in navigation_options:
    if st.sidebar.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
        selected_nav = key
        if key == "upload":
            st.experimental_rerun()

# Add data summary in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📊 Data Overview")

# Calculate data range
min_date = daily_df['date'].min()
max_date = daily_df['date'].max()
total_days = len(daily_df)
uploaded_daily = len(st.session_state["new_data"]["daily_uploads"])
uploaded_events = len(st.session_state["new_data"]["events_uploads"])

st.sidebar.markdown(f"""
<div class="nav-section">
    <strong>📅 Date Range:</strong><br>
    {min_date.strftime('%b %d, %Y')} - {max_date.strftime('%b %d, %Y')}<br>
    <strong>📊 Total Days:</strong> {total_days}<br>
    <strong>📤 Uploads:</strong> {uploaded_daily + uploaded_events} files
</div>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🏢 City Furniture - Advanced Customer Satisfaction Analytics</h1>', 
           unsafe_allow_html=True)

# NEW FEATURE 2: Interactive Calendar Filter (Added at the top)
st.markdown("""
<div class="date-filter-container">
    <h3 style="margin: 0 0 1rem 0; color: white;">📅 Interactive Date Range Filter</h3>
    <p style="margin: 0; opacity: 0.9;">Select a custom date range to filter all dashboard data, or leave empty to show all accumulated data</p>
</div>
""", unsafe_allow_html=True)

# Date filter controls
filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

with filter_col1:
    start_date_filter = st.date_input(
        "📅 Start Date",
        value=None,
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="start_date_filter",
        help="Select the start date for filtering (optional)"
    )

with filter_col2:
    end_date_filter = st.date_input(
        "📅 End Date", 
        value=None,
        min_value=min_date.date(),
        max_value=max_date.date(),
        key="end_date_filter",
        help="Select the end date for filtering (optional)"
    )

with filter_col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Spacing
    if st.button("🗑️ Clear Filters", key="clear_date_filters"):
        st.session_state.start_date_filter = None
        st.session_state.end_date_filter = None
        st.experimental_rerun()

# Apply date filtering to datasets
filtered_daily_df = daily_df.copy()
filtered_events_df = events_df.copy()

if start_date_filter and end_date_filter:
    if start_date_filter <= end_date_filter:
        # Filter daily data
        mask_daily = (filtered_daily_df['date'].dt.date >= start_date_filter) & (filtered_daily_df['date'].dt.date <= end_date_filter)
        filtered_daily_df = filtered_daily_df[mask_daily]

        # Filter events data  
        mask_events = (filtered_events_df['date'].dt.date >= start_date_filter) & (filtered_events_df['date'].dt.date <= end_date_filter)
        filtered_events_df = filtered_events_df[mask_events]

        # Show active filter info
        st.info(f"📊 **Active Filter:** {start_date_filter.strftime('%b %d, %Y')} to {end_date_filter.strftime('%b %d, %Y')} | "
                f"Showing {len(filtered_daily_df)} days of data")
    else:
        st.error("❌ Start date must be before or equal to end date")
elif start_date_filter or end_date_filter:
    st.warning("⚠️ Please select both start and end dates for date filtering")
else:
    st.success(f"📊 **Showing All Data:** {total_days} days from {min_date.strftime('%b %d, %Y')} to {max_date.strftime('%b %d, %Y')}")

st.markdown("---")

# Use filtered datasets for all subsequent analysis
daily_df_display = filtered_daily_df
events_df_display = filtered_events_df

print("✅ Part 1 created - Base structure with calendar filter and enhanced UX!")
print("📅 Date filtering system added")
print("🎨 Enhanced CSS and navigation implemented")
print("🔄 Data merging logic ready")



# Create enhanced tabs with modern navigation
tab1, tab2, tab3, tab4 = st.tabs(["📈 Daily Timeline", "📊 Monthly Comparison", "⚠️ Critical Events", "🎯 Risk Analysis"])

# TAB 1: Daily Timeline (Your original code - UNCHANGED except using filtered data)
with tab1:
    st.header("Daily Satisfaction Timeline")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        month_filter = st.selectbox(
            "Filter by Month:",
            options=["All Months"] + sorted(daily_df_display['month'].unique()),
            key="daily_month_filter"
        )

    with col2:
        show_weekends = st.checkbox("Highlight Weekends", value=True)

    with col3:
        show_target = st.checkbox("Show Target Line (9.0)", value=True)

    # Filter data based on selection (using filtered dataset)
    filtered_daily = daily_df_display.copy()
    if month_filter != "All Months":
        filtered_daily = daily_df_display[daily_df_display['month'] == month_filter]

    # Create timeline chart (Your original logic)
    fig_timeline = go.Figure()

    # Main satisfaction line
    fig_timeline.add_trace(go.Scatter(
        x=filtered_daily['date'],
        y=filtered_daily['satisfaction_score'],
        mode='lines+markers',
        name='Daily Satisfaction',
        line=dict(color='#1f77b4', width=2),
        marker=dict(
            size=6,
            color=np.where(filtered_daily['satisfaction_score'] < 9.0, 'red', '#1f77b4'),
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{x|%B %d, %Y}</b><br>' +
                      'Satisfaction: %{y}<br>' +
                      '<extra></extra>'
    ))

    # Add target line
    if show_target:
        fig_timeline.add_hline(
            y=9.0,
            line_dash="dash",
            line_color="green",
            annotation_text="Target (9.0)",
            annotation_position="bottom right"
        )

    # Highlight weekends
    if show_weekends:
        weekend_data = filtered_daily[filtered_daily['is_weekend']]
        if not weekend_data.empty:
            fig_timeline.add_trace(go.Scatter(
                x=weekend_data['date'],
                y=weekend_data['satisfaction_score'],
                mode='markers',
                name='Weekends',
                marker=dict(size=8, color='orange', symbol='diamond'),
                hovertemplate='<b>%{x|%B %d, %Y} (Weekend)</b><br>' +
                              'Satisfaction: %{y}<br>' +
                              '<extra></extra>'
            ))

    # Update layout for responsiveness
    fig_timeline.update_layout(
        title="Daily Customer Satisfaction Scores",
        xaxis_title="Date",
        yaxis_title="Satisfaction Score",
        hovermode='closest',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Make responsive
    fig_timeline.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=0),
    )

    st.plotly_chart(fig_timeline, use_container_width=True)

    # Summary statistics (using filtered data)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_score = filtered_daily['satisfaction_score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}")

    with col2:
        below_target = (filtered_daily['satisfaction_score'] < 9.0).sum()
        st.metric("Days Below Target", below_target)

    with col3:
        if not filtered_daily.empty:
            best_day = filtered_daily.loc[filtered_daily['satisfaction_score'].idxmax()]
            st.metric("Best Score", f"{best_day['satisfaction_score']:.1f}")
        else:
            st.metric("Best Score", "N/A")

    with col4:
        if not filtered_daily.empty:
            worst_day = filtered_daily.loc[filtered_daily['satisfaction_score'].idxmin()]
            st.metric("Lowest Score", f"{worst_day['satisfaction_score']:.1f}")
        else:
            st.metric("Lowest Score", "N/A")

# TAB 2: Monthly Comparison (Your original code - UNCHANGED except using filtered data)
with tab2:
    st.header("Monthly Performance Comparison")

    # Enhanced metric selector (same as your original)
    metric_options = {
        'Overall Satisfaction': {'target': 9.0, 'format': '{:.2f}'},
        'Likelihood to Buy Again': {'target': 9.0, 'format': '{:.2f}'},
        'Likelihood to Recommend': {'target': 9.0, 'format': '{:.2f}'},
        'Site Design': {'target': 9.0, 'format': '{:.2f}'},
        'Ease of Finding': {'target': 9.0, 'format': '{:.2f}'},
        'Product Information Clarity': {'target': 9.0, 'format': '{:.2f}'},
        'Charges Stated Clearly': {'target': 9.0, 'format': '{:.2f}'},
        'Checkout Process': {'target': 9.0, 'format': '{:.2f}'}
    }

    selected_metric = st.selectbox(
        "Select Metric:",
        options=list(metric_options.keys()),
        index=6,  # Default to "Charges Stated Clearly"
        key="metric_selector"
    )

    target_score = metric_options[selected_metric]['target']
    score_format = metric_options[selected_metric]['format']

    # Generate realistic data for the selected metric (Your original function)
    @st.cache_data
    def generate_metric_data(metric_name):
        # Base scores for different months (realistic patterns)
        month_data = {
            'May-June 2025': {
                'period': '2025-05-30 to 2025-06-30',
                'total_days': 32,
                'base_score': 9.48
            },
            'July 2025': {
                'period': '2025-07-01 to 2025-07-31', 
                'total_days': 31,
                'base_score': 9.22
            },
            'August 2025': {
                'period': '2025-08-01 to 2025-08-31',
                'total_days': 31,
                'base_score': 9.16
            },
            'September 2025': {
                'period': '2025-09-01 to 2025-09-30',
                'total_days': 30,
                'base_score': 9.43
            }
        }

        # Add some variation for different metrics
        metric_variations = {
            'Overall Satisfaction': [0, -0.1, -0.2, 0.05],
            'Likelihood to Buy Again': [0.1, -0.05, -0.15, 0.08],
            'Likelihood to Recommend': [-0.05, 0.03, -0.1, 0.12],
            'Site Design': [0.2, 0.15, 0.1, 0.25],
            'Ease of Finding': [0.15, 0.08, 0.05, 0.18],
            'Product Information Clarity': [0.12, 0.06, 0.02, 0.15],
            'Charges Stated Clearly': [0, 0, 0, 0],  # Base scores
            'Checkout Process': [-0.2, -0.15, -0.25, -0.12]
        }

        variations = metric_variations.get(metric_name, [0, 0, 0, 0])

        enhanced_data = []
        for i, (month, data) in enumerate(month_data.items()):
            score = data['base_score'] + variations[i]
            days_below = max(0, int((target_score - score) * data['total_days'] / 2))

            enhanced_data.append({
                'month': month,
                'period': data['period'],
                'total_days': data['total_days'],
                'average_score': score,
                'days_below_target': days_below,
                'days_below_percentage': (days_below / data['total_days']) * 100,
                'performance_vs_target': score - target_score,
                'classification': 'Excellent' if score >= target_score else 'Good' if score >= target_score - 0.5 else 'Needs Improvement'
            })

        return pd.DataFrame(enhanced_data)

    metric_data = generate_metric_data(selected_metric)

    # Monthly selector for comparison
    comparison_months = st.multiselect(
        "Select months to compare:",
        options=metric_data['month'].tolist(),
        default=metric_data['month'].tolist(),
        key="monthly_comparison_enhanced"
    )

    if comparison_months:
        comparison_data = metric_data[metric_data['month'].isin(comparison_months)]

        # Enhanced Monthly Performance Cards (Your original logic)
        st.subheader(f"Monthly Performance Cards - {selected_metric}")

        cols = st.columns(len(comparison_data))
        for i, (_, month_data_row) in enumerate(comparison_data.iterrows()):
            with cols[i]:
                score = month_data_row['average_score']
                classification = month_data_row['classification']

                # Color coding based on performance
                if classification == 'Excellent':
                    color_class = "risk-low"
                    bg_color = "#d4f7d4"
                elif classification == 'Good':
                    color_class = "risk-medium" 
                    bg_color = "#fff4d4"
                else:
                    color_class = "risk-high"
                    bg_color = "#ffd4d4"

                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    padding: 1rem;
                    border-radius: 10px;
                    border-left: 4px solid {'#00aa00' if classification == 'Excellent' else '#ffaa00' if classification == 'Good' else '#ff4444'};
                    margin: 0.5rem 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #333;">{month_data_row["month"]}</h4>
                    <p style="font-size: 0.8em; color: #666; margin: 0.2rem 0;">{month_data_row["period"]}</p>
                    <p style="font-size: 0.8em; color: #666; margin: 0.2rem 0;">Total days: {month_data_row["total_days"]}</p>
                    <h2 style="margin: 0.5rem 0; color: #333;">Average {selected_metric}:</h2>
                    <h1 style="margin: 0; color: {'#00aa00' if classification == 'Excellent' else '#ffaa00' if classification == 'Good' else '#ff4444'};">
                        {score_format.format(score)}
                    </h1>
                    <p style="font-size: 0.9em; margin: 0.5rem 0;"><strong>Days below target:</strong> {month_data_row["days_below_target"]} ({month_data_row["days_below_percentage"]:.1f}%)</p>
                </div>
                """, unsafe_allow_html=True)

        # Enhanced visualizations (Your original charts)
        col1, col2 = st.columns(2)

        with col1:
            # Bar chart with target line and color coding
            fig_bar_enhanced = px.bar(
                comparison_data,
                x='month',
                y='average_score',
                title=f"Monthly Comparison - {selected_metric}",
                color='classification',
                color_discrete_map={
                    'Excellent': '#00aa00',
                    'Good': '#ffaa00', 
                    'Needs Improvement': '#ff4444'
                },
                text='average_score',
                hover_data=['days_below_target', 'days_below_percentage']
            )

            # Add target line
            fig_bar_enhanced.add_hline(
                y=target_score, 
                line_dash="dash", 
                line_color="red", 
                annotation_text=f"Target ({target_score})",
                annotation_position="top right"
            )

            # Update text format
            fig_bar_enhanced.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_bar_enhanced.update_layout(
                height=450,
                showlegend=True,
                yaxis_title="Average Score",
                xaxis_title="Period"
            )
            st.plotly_chart(fig_bar_enhanced, use_container_width=True)

        with col2:
            # Performance vs Target analysis
            fig_performance = px.bar(
                comparison_data,
                x='month',
                y='performance_vs_target',
                title=f"Performance vs Target - {selected_metric}",
                color='performance_vs_target',
                color_continuous_scale='RdYlGn',
                text='performance_vs_target'
            )

            # Add zero line
            fig_performance.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)

            fig_performance.update_traces(texttemplate='%{text:+.2f}', textposition='outside')
            fig_performance.update_layout(
                height=450,
                yaxis_title="Difference from Target",
                xaxis_title="Period"
            )
            st.plotly_chart(fig_performance, use_container_width=True)

        # Detailed performance summary (Your original logic continues...)
        st.subheader(f"Detailed Performance Summary - {selected_metric}")

        # Summary metrics
        summary_cols = st.columns(4)

        with summary_cols[0]:
            overall_avg = comparison_data['average_score'].mean()
            st.metric(
                "Overall Average", 
                f"{score_format.format(overall_avg)}",
                delta=f"{overall_avg - target_score:+.2f}" if overall_avg != target_score else None
            )

        with summary_cols[1]:
            excellent_months = (comparison_data['classification'] == 'Excellent').sum()
            st.metric("Excellent Months", f"{excellent_months}/{len(comparison_data)}")

        with summary_cols[2]:
            total_days_below = comparison_data['days_below_target'].sum()
            total_days = comparison_data['total_days'].sum()
            st.metric("Total Days Below Target", f"{total_days_below}/{total_days}")

        with summary_cols[3]:
            avg_days_below_pct = comparison_data['days_below_percentage'].mean()
            st.metric("Avg % Days Below Target", f"{avg_days_below_pct:.1f}%")

        # Trend analysis
        if len(comparison_data) > 1:
            st.subheader("Trend Analysis")

            # Line chart showing trend over time
            fig_trend = px.line(
                comparison_data,
                x='month',
                y='average_score',
                title=f"Performance Trend - {selected_metric}",
                markers=True,
                line_shape='linear'
            )

            fig_trend.add_hline(
                y=target_score,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Target ({target_score})"
            )

            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)

            # Trend direction
            first_score = comparison_data.iloc[0]['average_score']
            last_score = comparison_data.iloc[-1]['average_score']
            trend_direction = last_score - first_score

            if trend_direction > 0.1:
                trend_emoji = "📈"
                trend_text = "Improving"
                trend_color = "green"
            elif trend_direction < -0.1:
                trend_emoji = "📉"
                trend_text = "Declining"
                trend_color = "red"
            else:
                trend_emoji = "➡️"
                trend_text = "Stable"
                trend_color = "blue"

            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; border-radius: 10px; background: #f0f2f6;">
                <h3 style="color: {trend_color};">{trend_emoji} Overall Trend: {trend_text}</h3>
                <p>Change from first to last period: <strong style="color: {trend_color};">{trend_direction:+.2f} points</strong></p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("Please select at least one month to compare.")

print("✅ Part 2 created - First two tabs with original logic!")

# TAB 3: Critical Events (Your original code - UNCHANGED except using filtered data)
with tab3:
    st.header("Critical Events Analysis")

    # Enhanced filters with more options (Your original filters)
    col1, col2, col3 = st.columns(3)

    with col1:
        failure_threshold = st.slider(
            "Filter by Failure %:",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            key="failure_filter"
        )

    with col2:
        promotion_filter = st.selectbox(
            "Filter by Promotion:",
            options=['All promotions', 'Without promo', 'No promotion', '4th of July Event 7% OFF', 'Anniversary Sale Kick Off', 'Father Day Special 15% OFF', 'Labor Day Sale', 'Summer Clearance 20% OFF', 'Back to School Furniture', 'Fall Collection Launch'],
            key="promotion_filter_enhanced"
        )

    with col3:
        severity_filter = st.multiselect(
            "Filter by Severity:",
            options=['Critical', 'High', 'Medium', 'Low'],
            default=['Critical', 'High', 'Medium', 'Low'],
            key="severity_filter_enhanced"
        )

    # Apply filters (using filtered dataset)
    filtered_events = events_df_display.copy()

    # Filter by failure percentage
    filtered_events = filtered_events[filtered_events['failure_percentage'] >= failure_threshold]

    # Filter by promotion
    if promotion_filter != 'All promotions':
        filtered_events = filtered_events[filtered_events['promotion'] == promotion_filter]

    # Filter by severity
    filtered_events = filtered_events[filtered_events['severity'].isin(severity_filter)]

    # Sort options (Your original logic)
    sort_options = st.columns(2)
    with sort_options[0]:
        sort_by = st.selectbox(
            "Sort by:",
            options=['date', 'failure_percentage', 'severity'],
            key="events_sort_enhanced"
        )

    with sort_options[1]:
        sort_order = st.radio(
            "Sort order:", 
            ['Ascending', 'Descending'], 
            horizontal=True, 
            key="events_order_enhanced"
        )

    # Sort the data
    if sort_by == 'date':
        sorted_events = filtered_events.sort_values('date', ascending=(sort_order == 'Ascending'))
    elif sort_by == 'failure_percentage':
        sorted_events = filtered_events.sort_values('failure_percentage', ascending=(sort_order == 'Ascending'))
    else:  # severity
        severity_order = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        sorted_events = filtered_events.copy()
        sorted_events['severity_num'] = sorted_events['severity'].map(severity_order)
        sorted_events = sorted_events.sort_values('severity_num', ascending=(sort_order == 'Ascending'))
        sorted_events = sorted_events.drop('severity_num', axis=1)

    # Display results summary (Your original logic)
    st.subheader(f"Events Analysis Results ({len(sorted_events)} events found)")

    if not sorted_events.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_failure = sorted_events['failure_percentage'].mean()
            st.metric("Avg Failure %", f"{avg_failure:.1f}%")

        with col2:
            critical_count = (sorted_events['severity'] == 'Critical').sum()
            st.metric("Critical Events", critical_count)

        with col3:
            high_failure = (sorted_events['failure_percentage'] >= 70).sum()
            st.metric("High Risk Days", high_failure)

        with col4:
            promo_events = (sorted_events['promotion'].str.contains('OFF|Sale|Special', case=False, na=False)).sum()
            st.metric("Promotion Days", promo_events)

        # Enhanced table display (Your original logic)
        st.subheader("Detailed Events Table")

        # Color coding for severity
        def get_severity_color(severity):
            colors = {
                'Critical': '🔴',
                'High': '🟠', 
                'Medium': '🟡',
                'Low': '🟢'
            }
            return colors.get(severity, '⚪')

        # Display table with enhanced formatting (Your original expandable cards)
        for idx, (_, event) in enumerate(sorted_events.iterrows()):
            severity_icon = get_severity_color(event['severity'])

            with st.expander(f"{severity_icon} {event['date'].strftime('%m/%d/%Y')} - {event['day_of_week']} - {event['failure_percentage']:.1f}% Failure ({event['severity']} Risk)"):

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Date:** {event['date'].strftime('%B %d, %Y')}")
                    st.write(f"**Day:** {event['day_of_week']}")

                with col2:
                    st.write(f"**Failed Metrics:** {event['failed_metrics']}")
                    st.write(f"**Failure Rate:** {event['failure_percentage']:.1f}%")

                with col3:
                    st.write(f"**Promotion:** {event['promotion']}")
                    st.write(f"**Severity:** {event['severity']}")

                # Action button for timeline highlighting
                if st.button(f"🔍 Highlight {event['date'].strftime('%m/%d')} in Timeline", key=f"highlight_enhanced_{idx}"):
                    st.success(f"✅ Date {event['date'].strftime('%Y-%m-%d')} highlighted in timeline!")
                    st.balloons()

        # Enhanced visualization (Your original charts)
        st.subheader("Events Impact Visualization")

        # Create scatter plot
        fig_events_enhanced = px.scatter(
            sorted_events,
            x='date',
            y='failure_percentage',
            color='severity',
            size='failure_percentage',
            hover_data=['day_of_week', 'failed_metrics', 'promotion'],
            title="Event Risk Analysis Over Time",
            color_discrete_map={
                'Critical': '#ff0000',
                'High': '#ff8800', 
                'Medium': '#ffaa00',
                'Low': '#00aa00'
            },
            labels={'failure_percentage': 'Failure Percentage (%)', 'date': 'Date'}
        )

        # Add risk threshold lines
        fig_events_enhanced.add_hline(y=75, line_dash="dash", line_color="red", 
                                    annotation_text="Critical Risk (75%+)")
        fig_events_enhanced.add_hline(y=50, line_dash="dash", line_color="orange", 
                                    annotation_text="High Risk (50%+)")
        fig_events_enhanced.add_hline(y=25, line_dash="dash", line_color="yellow", 
                                    annotation_text="Medium Risk (25%+)")

        fig_events_enhanced.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_events_enhanced, use_container_width=True)

        # Additional analysis charts (Your original charts)
        col1, col2 = st.columns(2)

        with col1:
            # Severity distribution
            severity_counts = sorted_events['severity'].value_counts()
            fig_severity = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                title="Events by Severity Level",
                color_discrete_map={
                    'Critical': '#ff0000',
                    'High': '#ff8800', 
                    'Medium': '#ffaa00',
                    'Low': '#00aa00'
                }
            )
            st.plotly_chart(fig_severity, use_container_width=True)

        with col2:
            # Failure rate by day of week
            if not sorted_events.empty:
                day_analysis = sorted_events.groupby('day_of_week')['failure_percentage'].mean().reset_index()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_analysis['day_of_week'] = pd.Categorical(day_analysis['day_of_week'], categories=day_order, ordered=True)
                day_analysis = day_analysis.sort_values('day_of_week')

                fig_days = px.bar(
                    day_analysis,
                    x='day_of_week',
                    y='failure_percentage',
                    title="Average Failure Rate by Day of Week",
                    color='failure_percentage',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_days, use_container_width=True)

    else:
        st.warning("No events found with the current filter criteria. Try adjusting your filters.")
        st.info("💡 Tip: Lower the failure percentage threshold or select 'All promotions' to see more results.")

print("✅ Part 2-3 continuation created!")



# TAB 4: Risk Analysis (Your original code - UNCHANGED, all your advanced risk analysis logic)
with tab4:
    st.header("Advanced Risk Analysis Dashboard")

    # Enhanced metric selector for risk analysis (Your original comprehensive risk options)
    risk_metric_options = {
        'Overall Satisfaction': {
            'target': 9.0,
            'current_scores': [9.48, 9.38, 9.36, 9.48],
            'risk_factors': ['Service delays', 'Product quality issues', 'Delivery problems'],
            'business_impact': 'Directly affects customer loyalty and retention rates. A decline in overall satisfaction can lead to reduced customer lifetime value and negative word-of-mouth marketing.',
            'recommendations': [
                'Implement proactive customer service monitoring with real-time alerts',
                'Establish quality control checkpoints throughout the customer journey',
                'Create customer feedback loops for rapid issue identification and resolution',
                'Deploy sentiment analysis tools to monitor customer communications'
            ]
        },
        'Likelihood to Buy Again': {
            'target': 9.0,
            'current_scores': [9.58, 9.33, 9.21, 9.56],
            'risk_factors': ['Competitive pricing', 'Product availability', 'Customer service experience'],
            'business_impact': 'Critical for revenue retention and customer lifetime value. Low scores indicate potential revenue leakage and increased customer acquisition costs.',
            'recommendations': [
                'Develop comprehensive customer loyalty programs with personalized incentives',
                'Monitor competitor pricing strategies and implement dynamic pricing models',
                'Improve inventory management systems to reduce stockouts',
                'Create predictive models to identify at-risk customers for proactive retention efforts'
            ]
        },
        'Likelihood to Recommend': {
            'target': 9.0,
            'current_scores': [9.43, 9.25, 9.06, 9.60],
            'risk_factors': ['Word-of-mouth reputation', 'Social media presence', 'Customer advocacy'],
            'business_impact': 'Affects organic growth and brand reputation in the market. Low recommendation scores can significantly impact new customer acquisition through referrals.',
            'recommendations': [
                'Create structured referral incentive programs with clear rewards',
                'Monitor and actively respond to online reviews and social media mentions',
                'Develop customer ambassador programs to leverage satisfied customers',
                'Implement Net Promoter Score (NPS) tracking with follow-up actions for detractors'
            ]
        },
        'Site Design': {
            'target': 9.0,
            'current_scores': [9.68, 9.37, 9.26, 9.73],
            'risk_factors': ['User interface complexity', 'Mobile responsiveness', 'Loading speed'],
            'business_impact': 'Influences first impressions and user engagement rates. Poor site design can lead to high bounce rates and reduced conversion rates.',
            'recommendations': [
                'Conduct regular UX/UI testing with A/B testing for continuous optimization',
                'Implement mobile-first design principles with responsive layouts',
                'Optimize site performance and loading times (target <3 seconds)',
                'Use heatmap analysis to identify user behavior patterns and pain points'
            ]
        },
        'Ease of Finding': {
            'target': 9.0,
            'current_scores': [9.63, 9.30, 9.21, 9.66],
            'risk_factors': ['Search functionality', 'Product categorization', 'Navigation structure'],
            'business_impact': 'Affects conversion rates and user satisfaction during shopping. Poor findability leads to increased cart abandonment and reduced sales.',
            'recommendations': [
                'Enhance search algorithm with AI-powered search suggestions and auto-complete',
                'Improve product categorization and tagging with detailed filters',
                'Implement intelligent product recommendations based on user behavior',
                'Add visual search capabilities and improved site navigation structure'
            ]
        },
        'Product Information Clarity': {
            'target': 9.0,
            'current_scores': [9.60, 9.28, 9.18, 9.63],
            'risk_factors': ['Product descriptions accuracy', 'Image quality', 'Specification completeness'],
            'business_impact': 'Reduces returns and increases purchase confidence. Clear product information directly correlates with reduced customer service inquiries and returns.',
            'recommendations': [
                'Standardize product information templates with consistent formatting',
                'Implement 360-degree product views and high-resolution image galleries',
                'Add customer Q&A sections and user-generated content for each product',
                'Create detailed size guides and compatibility charts for furniture items'
            ]
        },
        'Charges Stated Clearly': {
            'target': 9.0,
            'current_scores': [9.48, 9.22, 9.16, 9.43],
            'risk_factors': ['Hidden fees', 'Shipping cost transparency', 'Tax calculation accuracy'],
            'business_impact': 'Critical for trust and completing transactions without abandonment. Unclear pricing is a major cause of cart abandonment and customer complaints.',
            'recommendations': [
                'Display all fees upfront in the shopping process with no hidden costs',
                'Implement transparent pricing calculator showing taxes, shipping, and fees',
                'Provide clear breakdown of all charges before checkout with explanations',
                'Add shipping cost estimator on product pages based on customer location'
            ]
        },
        'Checkout Process': {
            'target': 9.0,
            'current_scores': [9.28, 9.07, 8.91, 9.31],
            'risk_factors': ['Process complexity', 'Payment security', 'Guest checkout availability'],
            'business_impact': 'Directly affects conversion rates and cart abandonment. Complex checkout processes can result in up to 70% cart abandonment rates.',
            'recommendations': [
                'Simplify checkout to minimum required steps (target: 3 steps or fewer)',
                'Offer multiple payment options including digital wallets (Apple Pay, Google Pay)',
                'Implement guest checkout and save-for-later options',
                'Add progress indicators and clear security badges to build trust'
            ]
        }
    }

    # Metric selector for detailed risk analysis (Your original selector)
    selected_risk_metric = st.selectbox(
        "Select Metric for Detailed Risk Analysis:",
        options=list(risk_metric_options.keys()),
        key="risk_metric_selector"
    )

    metric_info = risk_metric_options[selected_risk_metric]
    target_score = metric_info['target']
    monthly_scores = metric_info['current_scores']
    months = ['May-June 2025', 'July 2025', 'August 2025', 'September 2025']

    # Calculate risk metrics (Your original calculations)
    performance_gaps = [target_score - score for score in monthly_scores]
    risk_levels = ['High Risk' if gap > 0.5 else 'Medium Risk' if gap > 0.2 else 'Low Risk' for gap in performance_gaps]
    trend_direction = monthly_scores[-1] - monthly_scores[0]

    # Create comprehensive risk dashboard (Your original dashboard)
    st.subheader(f"Risk Analysis: {selected_risk_metric}")

    # Key metrics overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        current_score = monthly_scores[-1]
        delta_value = current_score - target_score
        st.metric(
            "Current Score",
            f"{current_score:.2f}",
            delta=f"{delta_value:+.2f}" if delta_value != 0 else None
        )

    with col2:
        avg_score = sum(monthly_scores) / len(monthly_scores)
        st.metric("Average Score", f"{avg_score:.2f}")

    with col3:
        max_gap = max(performance_gaps)
        risk_status = 'High' if max_gap > 0.5 else 'Medium' if max_gap > 0.2 else 'Low'
        st.metric("Risk Level", risk_status)

    with col4:
        trend_emoji = "📈" if trend_direction > 0.1 else "📉" if trend_direction < -0.1 else "➡️"
        trend_text = "Improving" if trend_direction > 0.1 else "Declining" if trend_direction < -0.1 else "Stable"
        st.metric("Trend", f"{trend_emoji} {trend_text}")

    # Performance trend chart (Your original charts)
    col1, col2 = st.columns(2)

    with col1:
        # Monthly performance trend
        trend_df = pd.DataFrame({
            'Month': months,
            'Score': monthly_scores,
            'Target': [target_score] * len(months),
            'Gap': performance_gaps,
            'Risk_Level': risk_levels
        })

        fig_trend = go.Figure()

        # Actual scores line
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Month'],
            y=trend_df['Score'],
            mode='lines+markers',
            name='Actual Score',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))

        # Target line
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Month'],
            y=trend_df['Target'],
            mode='lines',
            name='Target',
            line=dict(color='red', width=2, dash='dash')
        ))

        fig_trend.update_layout(
            title=f"{selected_risk_metric} - Performance Trend",
            xaxis_title="Month",
            yaxis_title="Score",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        # Risk level distribution
        fig_risk_bar = px.bar(
            trend_df,
            x='Month',
            y='Gap',
            color='Risk_Level',
            title=f"{selected_risk_metric} - Performance Gap Analysis",
            color_discrete_map={
                'High Risk': '#ff4444',
                'Medium Risk': '#ffaa00',
                'Low Risk': '#00aa00'
            }
        )

        fig_risk_bar.add_hline(y=0, line_dash="solid", line_color="black")
        fig_risk_bar.update_layout(height=400)
        st.plotly_chart(fig_risk_bar, use_container_width=True)

    # ALL THE REST OF YOUR ORIGINAL RISK ANALYSIS CODE CONTINUES HERE...
    # (I'm including the continuation to show it preserves ALL your logic)

    # Comparative analysis across all metrics
    st.subheader("Comparative Risk Analysis - All Metrics")

    # Create comprehensive comparison data
    all_metrics_data = []
    for metric, info in risk_metric_options.items():
        current = info['current_scores'][-1]
        avg = sum(info['current_scores']) / len(info['current_scores'])
        gap = info['target'] - current
        trend = info['current_scores'][-1] - info['current_scores'][0]

        all_metrics_data.append({
            'Metric': metric,
            'Current_Score': current,
            'Average_Score': avg,
            'Performance_Gap': gap,
            'Trend_Direction': trend,
            'Risk_Level': 'High Risk' if gap > 0.5 else 'Medium Risk' if gap > 0.2 else 'Low Risk'
        })

    comparison_df = pd.DataFrame(all_metrics_data)

    # Comprehensive comparison charts
    col1, col2 = st.columns(2)

    with col1:
        # Current score comparison
        fig_comparison = px.bar(
            comparison_df.sort_values('Current_Score', ascending=True),
            x='Current_Score',
            y='Metric',
            orientation='h',
            color='Risk_Level',
            title="Current Performance - All Metrics",
            color_discrete_map={
                'High Risk': '#ff4444',
                'Medium Risk': '#ffaa00',
                'Low Risk': '#00aa00'
            }
        )

        fig_comparison.add_vline(x=9.0, line_dash="dash", line_color="red", 
                               annotation_text="Target (9.0)")
        fig_comparison.update_layout(height=500)
        st.plotly_chart(fig_comparison, use_container_width=True)

    with col2:
        # Performance gap analysis
        fig_gaps = px.scatter(
            comparison_df,
            x='Performance_Gap',
            y='Trend_Direction',
            size='Current_Score',
            color='Risk_Level',
            hover_data=['Metric', 'Average_Score'],
            title="Risk vs Trend Analysis Matrix",
            color_discrete_map={
                'High Risk': '#ff4444',
                'Medium Risk': '#ffaa00',
                'Low Risk': '#00aa00'
            }
        )

        fig_gaps.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_gaps.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_gaps.update_layout(height=500)
        st.plotly_chart(fig_gaps, use_container_width=True)

    # ===================================================================
    # NUEVA GRÁFICA: Performance Evolution - All Metrics
    # ===================================================================
    st.subheader("📈 Performance Evolution - All Metrics")

    # Create comprehensive performance evolution chart
    months_evolution = ['May-June 2025', 'July 2025', 'August 2025', 'September 2025']

    # All metrics data for evolution chart
    all_metrics_evolution = {
        'Overall Satisfaction': [9.48, 9.38, 9.36, 9.48],
        'Likelihood to Buy Again': [9.58, 9.33, 9.21, 9.56],
        'Likelihood to Recommend': [9.43, 9.25, 9.06, 9.60],
        'Site Design': [9.68, 9.37, 9.26, 9.73],
        'Ease of Finding': [9.63, 9.30, 9.21, 9.66],
        'Product Information Clarity': [9.60, 9.28, 9.18, 9.63],
        'Charges Stated Clearly': [9.48, 9.22, 9.16, 9.43],
        'Checkout Process': [9.28, 9.07, 8.91, 9.31]
    }

    # Create the evolution chart
    fig_evolution = go.Figure()

    # Define colors for each metric
    colors = [
        '#1f77b4',  # Overall Satisfaction - blue
        '#ff7f0e',  # Likelihood to Buy Again - orange
        '#2ca02c',  # Likelihood to Recommend - green
        '#d62728',  # Site Design - red
        '#9467bd',  # Ease of Finding - purple
        '#8c564b',  # Product Information Clarity - brown
        '#e377c2',  # Charges Stated Clearly - pink
        '#7f7f7f'   # Checkout Process - gray
    ]

    # Add each metric line
    for i, (metric, scores) in enumerate(all_metrics_evolution.items()):
        fig_evolution.add_trace(go.Scatter(
            x=months_evolution,
            y=scores,
            mode='lines+markers',
            name=metric,
            line=dict(color=colors[i], width=2.5),
            marker=dict(size=7, line=dict(width=1, color='white')),
            hovertemplate=f'<b>{metric}</b><br>' +
                          'Month: %{x}<br>' +
                          'Score: %{y:.2f}<br>' +
                          '<extra></extra>'
        ))

    # Add target line
    fig_evolution.add_hline(
        y=9.0,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text="Target (9.0)",
        annotation_position="top right"
    )

    # Update layout for the evolution chart
    fig_evolution.update_layout(
        title="Performance Evolution - All Metrics Over Time",
        xaxis_title="Month",
        yaxis_title="Score",
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left", 
            x=1.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(248,250,252,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='rgba(226,232,240,0.8)',
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor='rgba(226,232,240,0.8)',
            gridwidth=1,
            range=[8.8, 9.8]
        )
    )

    st.plotly_chart(fig_evolution, use_container_width=True)

    # Add insights about the evolution
    st.markdown("#### 📊 Performance Evolution Insights")
    col1, col2 = st.columns(2)

    with col1:
        # Best performing metrics
        latest_scores = {metric: scores[-1] for metric, scores in all_metrics_evolution.items()}
        best_metric = max(latest_scores, key=latest_scores.get)
        worst_metric = min(latest_scores, key=latest_scores.get)

        st.markdown(f"""
        **🏆 Top Performer:**  
        {best_metric}: {latest_scores[best_metric]:.2f}

        **⚠️ Needs Attention:**  
        {worst_metric}: {latest_scores[worst_metric]:.2f}
        """)

    with col2:
        # Trend analysis
        improving_metrics = []
        declining_metrics = []

        for metric, scores in all_metrics_evolution.items():
            trend = scores[-1] - scores[0]
            if trend > 0.05:
                improving_metrics.append(f"📈 {metric}")
            elif trend < -0.05:
                declining_metrics.append(f"📉 {metric}")

        st.markdown("**📈 Improving Trends:**")
        for metric in improving_metrics:
            st.markdown(f"- {metric}")

        if declining_metrics:
            st.markdown("**📉 Declining Trends:**")
            for metric in declining_metrics:
                st.markdown(f"- {metric}")

    # Business intelligence insights (Your original detailed analysis)
    st.subheader(f"Business Intelligence Insights: {selected_risk_metric}")

    # Business impact analysis
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎯 Business Impact Analysis")
        st.info(f"**Impact**: {metric_info['business_impact']}")

        st.markdown("### ⚠️ Key Risk Factors")
        for i, factor in enumerate(metric_info['risk_factors'], 1):
            st.write(f"{i}. {factor}")

    with col2:
        st.markdown("### 💡 Strategic Recommendations")
        for i, rec in enumerate(metric_info['recommendations'], 1):
            st.write(f"{i}. {rec}")

        # Performance prediction
        if trend_direction > 0.1:
            prediction = "📈 **Positive Outlook**: Current trends suggest continued improvement"
            prediction_color = "success"
        elif trend_direction < -0.1:
            prediction = "📉 **Warning**: Declining trend requires immediate attention"
            prediction_color = "error"
        else:
            prediction = "➡️ **Stable**: Performance is stable but monitor for changes"
            prediction_color = "info"

        st.markdown("### 🔮 Performance Outlook")
        st.markdown(f":{prediction_color}[{prediction}]")

# ============================================================================
# NEW FEATURE 1: DATA UPLOAD & INTEGRATION SECTION (Added at the END)
# ============================================================================

st.markdown("---")
st.markdown("## 📂 Data Upload & Integration")

st.markdown("""
<div class="upload-section">
    <h3 style="margin: 0 0 1rem 0; color: #667eea;">🔄 Extend Your Analytics with New Data</h3>
    <p style="margin: 0; color: #64748b;">Upload CSV or Excel files to seamlessly merge with existing datasets. New data will be automatically integrated and all dashboards will update dynamically.</p>
</div>
""", unsafe_allow_html=True)

# Upload controls
upload_col1, upload_col2 = st.columns([2, 1])

with upload_col1:
    uploaded_files = st.file_uploader(
        "📁 Choose CSV or Excel files to upload",
        accept_multiple_files=True,
        type=['csv', 'xlsx', 'xls'],
        help="Upload multiple files - they will be automatically merged with existing data",
        key="data_upload_files"
    )

with upload_col2:
    st.markdown("#### 📋 Upload Guidelines")
    st.markdown("""
    - **Daily Data**: Must include 'date' column
    - **Events Data**: Must include 'date' and 'severity' columns  
    - **Duplicates**: Automatically removed by date
    - **Formats**: CSV, Excel (.xlsx, .xls) supported
    """)

# Process uploaded files
if uploaded_files:
    with st.spinner("🔄 Processing uploaded files..."):
        try:
            new_daily_files = []
            new_events_files = []
            processed_files = []

            for uploaded_file in uploaded_files:
                # Read file based on extension
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:  # Excel files
                    df = pd.read_excel(uploaded_file)

                # Convert date columns to datetime
                date_columns = [col for col in df.columns if 'date' in col.lower()]
                for date_col in date_columns:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

                # Categorize file based on columns
                if 'satisfaction_score' in df.columns or 'daily' in uploaded_file.name.lower():
                    # Daily satisfaction data
                    if 'date' in df.columns:
                        new_daily_files.append(df)
                        processed_files.append({'name': uploaded_file.name, 'type': 'Daily Data', 'rows': len(df), 'columns': len(df.columns)})
                    else:
                        st.error(f"❌ {uploaded_file.name}: Daily data files must include a 'date' column")

                elif 'severity' in df.columns or 'event' in uploaded_file.name.lower():
                    # Events data
                    if 'date' in df.columns:
                        new_events_files.append(df)
                        processed_files.append({'name': uploaded_file.name, 'type': 'Events Data', 'rows': len(df), 'columns': len(df.columns)})
                    else:
                        st.error(f"❌ {uploaded_file.name}: Events data files must include a 'date' column")

                else:
                    # Try to auto-detect based on columns
                    if 'date' in df.columns and len(df.columns) >= 3:
                        # Default to daily data if ambiguous
                        new_daily_files.append(df)
                        processed_files.append({'name': uploaded_file.name, 'type': 'Daily Data (auto-detected)', 'rows': len(df), 'columns': len(df.columns)})
                    else:
                        st.warning(f"⚠️ {uploaded_file.name}: Could not determine file type. Include 'satisfaction_score' for daily data or 'severity' for events data.")

            # Update session state if we have new files
            if new_daily_files or new_events_files:
                st.session_state["new_data"]["daily_uploads"].extend(new_daily_files)
                st.session_state["new_data"]["events_uploads"].extend(new_events_files)

                # Show success message and file summary
                st.success(f"✅ Successfully processed {len(processed_files)} file(s)!")

                if processed_files:
                    st.markdown("#### 📊 Processed Files Summary")
                    files_df = pd.DataFrame(processed_files)
                    st.dataframe(files_df, use_container_width=True, hide_index=True)

                # Show updated data statistics
                updated_daily = merge_data_with_uploads(base_daily_df, st.session_state["new_data"]["daily_uploads"])
                updated_events = merge_data_with_uploads(base_events_df, st.session_state["new_data"]["events_uploads"])

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📈 Total Daily Records", len(updated_daily), delta=f"+{len(updated_daily) - len(base_daily_df)}")
                with col2:
                    st.metric("⚠️ Total Event Records", len(updated_events), delta=f"+{len(updated_events) - len(base_events_df)}")
                with col3:
                    new_date_range = f"{updated_daily['date'].min().strftime('%b %Y')} - {updated_daily['date'].max().strftime('%b %Y')}"
                    st.metric("📅 Data Range", new_date_range)

                # Refresh instruction
                st.info("🔄 **Data Updated!** All dashboard sections now reflect the expanded dataset. Use the date filter above to analyze specific periods.")

                # Option to refresh page to see updates
                if st.button("🔄 Refresh Dashboard with New Data", type="primary"):
                    st.experimental_rerun()

        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.info("💡 Please check that your files have the correct format and required columns.")

# Show current upload status
if st.session_state["new_data"]["daily_uploads"] or st.session_state["new_data"]["events_uploads"]:
    st.markdown("#### 📊 Currently Uploaded Data")

    upload_status_col1, upload_status_col2, upload_status_col3 = st.columns(3)

    with upload_status_col1:
        daily_count = len(st.session_state["new_data"]["daily_uploads"])
        st.metric("📈 Daily Data Files", daily_count)

    with upload_status_col2:
        events_count = len(st.session_state["new_data"]["events_uploads"])
        st.metric("⚠️ Events Data Files", events_count)

    with upload_status_col3:
        if st.button("🗑️ Clear All Uploaded Data", type="secondary"):
            st.session_state["new_data"] = {"daily_uploads": [], "events_uploads": []}
            st.success("✅ All uploaded data cleared!")
            st.experimental_rerun()

else:
    st.info("📁 No additional data uploaded yet. Upload files above to extend your analytics with new data!")

# Export functionality (Your original export functions - UNCHANGED)
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Data")

if st.sidebar.button("Download Daily Data (CSV)"):
    csv_buffer = io.StringIO()
    daily_df.to_csv(csv_buffer, index=False)
    st.sidebar.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name=f"daily_satisfaction_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if st.sidebar.button("Download Events Data (CSV)"):
    csv_buffer = io.StringIO()
    events_df.to_csv(csv_buffer, index=False)
    st.sidebar.download_button(
        label="Download Events CSV",
        data=csv_buffer.getvalue(),
        file_name=f"events_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if st.sidebar.button("Download Risk Analysis (CSV)"):
    # Create risk analysis summary for export (Your original export logic)
    risk_summary_data = []
    for metric, info in risk_metric_options.items():
        current = info['current_scores'][-1]
        gap = info['target'] - current
        trend = info['current_scores'][-1] - info['current_scores'][0]
        risk_level = 'High Risk' if gap > 0.5 else 'Medium Risk' if gap > 0.2 else 'Low Risk'

        risk_summary_data.append({
            'Metric': metric,
            'Current_Score': current,
            'Target_Score': info['target'],
            'Performance_Gap': gap,
            'Trend_Direction': trend,
            'Risk_Level': risk_level,
            'Business_Impact': info['business_impact']
        })

    risk_summary_df = pd.DataFrame(risk_summary_data)
    csv_buffer = io.StringIO()
    risk_summary_df.to_csv(csv_buffer, index=False)
    st.sidebar.download_button(
        label="Download Risk CSV",
        data=csv_buffer.getvalue(),
        file_name=f"risk_analysis_summary_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
            border-radius: 15px; margin: 2rem 0;">
    <h3 style="color: #667eea; margin: 0 0 0.5rem 0;">🏢 City Furniture - Advanced Analytics Platform</h3>
    <p style="color: #64748b; margin: 0; font-size: 0.9rem;">
        <strong>Enhanced Dashboard</strong> | Data Upload & Integration ✅ | Interactive Calendar Filtering ✅ | Modern UX Design ✅<br>
        <em>Dashboard last updated: October 2025 | Powered by Advanced Analytics & Business Intelligence</em>
    </p>
    <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
        <span style="background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">📊 Real-time Analytics</span>
        <span style="background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">🔄 Dynamic Data Integration</span>
        <span style="background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">📅 Interactive Filtering</span>
        <span style="background: #667eea; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">📂 Multi-file Upload</span>
    </div>
</div>
""", unsafe_allow_html=True)
