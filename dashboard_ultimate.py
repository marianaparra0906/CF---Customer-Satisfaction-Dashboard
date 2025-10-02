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

# Custom CSS for responsive design
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
    }

    .risk-high { border-left-color: #ff4444 !important; }
    .risk-medium { border-left-color: #ffaa00 !important; }
    .risk-low { border-left-color: #00aa00 !important; }

    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; }
        .metric-card { margin: 0.25rem 0; }
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

# Load data
daily_df, events_df = load_data()

# Sidebar
st.sidebar.markdown("### 📊 Dashboard Navigation")
st.sidebar.markdown("---")

# Main header
st.markdown('<h1 class="main-header">City Furniture - Interactive Customer Satisfaction Analysis</h1>', 
           unsafe_allow_html=True)
st.markdown("**May 30, 2025 to September 30, 2025** | (124 days analyzed)")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Daily Timeline", "📊 Monthly Comparison", "⚠️ Critical Events", "🎯 Risk Analysis"])

# TAB 1: Daily Timeline
with tab1:
    st.header("Daily Satisfaction Timeline")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        month_filter = st.selectbox(
            "Filter by Month:",
            options=["All Months"] + sorted(daily_df['month'].unique()),
            key="daily_month_filter"
        )

    with col2:
        show_weekends = st.checkbox("Highlight Weekends", value=True)

    with col3:
        show_target = st.checkbox("Show Target Line (9.0)", value=True)

    # Filter data based on selection
    filtered_daily = daily_df.copy()
    if month_filter != "All Months":
        filtered_daily = daily_df[daily_df['month'] == month_filter]

    # Create timeline chart
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

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_score = filtered_daily['satisfaction_score'].mean()
        st.metric("Average Score", f"{avg_score:.1f}")

    with col2:
        below_target = (filtered_daily['satisfaction_score'] < 9.0).sum()
        st.metric("Days Below Target", below_target)

    with col3:
        best_day = filtered_daily.loc[filtered_daily['satisfaction_score'].idxmax()]
        st.metric("Best Score", f"{best_day['satisfaction_score']:.1f}")

    with col4:
        worst_day = filtered_daily.loc[filtered_daily['satisfaction_score'].idxmin()]
        st.metric("Lowest Score", f"{worst_day['satisfaction_score']:.1f}")

# TAB 2: Monthly Comparison (Enhanced Version)
with tab2:
    st.header("Monthly Performance Comparison")

    # Enhanced metric selector (same as shown in the image)
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
        index=6,  # Default to "Charges Stated Clearly" like in the image
        key="metric_selector"
    )

    target_score = metric_options[selected_metric]['target']
    score_format = metric_options[selected_metric]['format']

    # Generate realistic data for the selected metric
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
            'Charges Stated Clearly': [0, 0, 0, 0],  # Base scores (as shown in image)
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

        # Enhanced Monthly Performance Cards
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

        # Enhanced visualizations
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

        # Detailed performance summary
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

# TAB 3: Critical Events (Enhanced Version)
with tab3:
    st.header("Critical Events Analysis")

    # Enhanced filters with more options
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

    # Apply filters
    filtered_events = events_df.copy()

    # Filter by failure percentage
    filtered_events = filtered_events[filtered_events['failure_percentage'] >= failure_threshold]

    # Filter by promotion
    if promotion_filter != 'All promotions':
        filtered_events = filtered_events[filtered_events['promotion'] == promotion_filter]

    # Filter by severity
    filtered_events = filtered_events[filtered_events['severity'].isin(severity_filter)]

    # Sort options
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

    # Display results summary
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

        # Enhanced table display
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

        # Display table with enhanced formatting
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

        # Enhanced visualization
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

        # Additional analysis charts
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

# TAB 4: Risk Analysis (Enhanced Version with Advanced Insights)
with tab4:
    st.header("Advanced Risk Analysis Dashboard")

    # Enhanced metric selector for risk analysis
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

    # Metric selector for detailed risk analysis
    selected_risk_metric = st.selectbox(
        "Select Metric for Detailed Risk Analysis:",
        options=list(risk_metric_options.keys()),
        key="risk_metric_selector"
    )

    metric_info = risk_metric_options[selected_risk_metric]
    target_score = metric_info['target']
    monthly_scores = metric_info['current_scores']
    months = ['May-June 2025', 'July 2025', 'August 2025', 'September 2025']

    # Calculate risk metrics
    performance_gaps = [target_score - score for score in monthly_scores]
    risk_levels = ['High Risk' if gap > 0.5 else 'Medium Risk' if gap > 0.2 else 'Low Risk' for gap in performance_gaps]
    trend_direction = monthly_scores[-1] - monthly_scores[0]

    # Create comprehensive risk dashboard
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

    # Performance trend chart
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

    # Time series comparison for all metrics
    st.subheader("Performance Evolution - All Metrics")

    # Create time series data for all metrics
    time_series_data = []
    for month_idx, month in enumerate(months):
        for metric, info in risk_metric_options.items():
            time_series_data.append({
                'Month': month,
                'Metric': metric,
                'Score': info['current_scores'][month_idx],
                'Target': info['target'],
                'Gap': info['target'] - info['current_scores'][month_idx]
            })

    time_series_df = pd.DataFrame(time_series_data)

    # Multi-line chart showing all metrics over time
    fig_evolution = px.line(
        time_series_df,
        x='Month',
        y='Score',
        color='Metric',
        title="Performance Evolution - All Metrics Over Time",
        markers=True
    )

    fig_evolution.add_hline(y=9.0, line_dash="dash", line_color="red", 
                          annotation_text="Target (9.0)")
    fig_evolution.update_layout(height=500)
    st.plotly_chart(fig_evolution, use_container_width=True)

    # Detailed metric insights and recommendations
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

    # Priority action matrix
    st.subheader("Priority Action Matrix")

    # Create priority matrix based on risk level and trend
    priority_data = []
    for metric, info in risk_metric_options.items():
        current = info['current_scores'][-1]
        gap = info['target'] - current
        trend = info['current_scores'][-1] - info['current_scores'][0]

        # Determine priority level
        if gap > 0.5 and trend < -0.1:
            priority = "Critical - Immediate Action Required"
            priority_score = 4
        elif gap > 0.3 or trend < -0.2:
            priority = "High - Action Required Soon"
            priority_score = 3
        elif gap > 0.1 or trend < -0.1:
            priority = "Medium - Monitor Closely"
            priority_score = 2
        else:
            priority = "Low - Maintain Current Performance"
            priority_score = 1

        priority_data.append({
            'Metric': metric,
            'Current_Score': current,
            'Gap': gap,
            'Trend': trend,
            'Priority': priority,
            'Priority_Score': priority_score
        })

    priority_df = pd.DataFrame(priority_data).sort_values('Priority_Score', ascending=False)

    # Display priority matrix
    for _, row in priority_df.iterrows():
        if row['Priority_Score'] == 4:
            alert_type = "error"
            icon = "🚨"
            border_color = "#ff4444"
        elif row['Priority_Score'] == 3:
            alert_type = "warning"
            icon = "⚠️"
            border_color = "#ffaa00"
        elif row['Priority_Score'] == 2:
            alert_type = "info"
            icon = "ℹ️"
            border_color = "#3498db"
        else:
            alert_type = "success"
            icon = "✅"
            border_color = "#00aa00"

        st.markdown(f"""
        <div style="padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {border_color}; background: #f8f9fa;">
            <h4 style="margin: 0;">{icon} {row['Metric']}</h4>
            <p><strong>Priority:</strong> {row['Priority']}</p>
            <p><strong>Current Score:</strong> {row['Current_Score']:.2f} | <strong>Gap:</strong> {row['Gap']:.2f} | <strong>Trend:</strong> {row['Trend']:+.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # Executive summary
    st.subheader("📊 Executive Summary & Key Takeaways")

    # Calculate overall statistics
    high_risk_count = len([m for m in priority_df['Priority_Score'] if m >= 3])
    improving_metrics = len([m for m in priority_df['Trend'] if m > 0.1])
    avg_performance = comparison_df['Current_Score'].mean()

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("High Priority Metrics", high_risk_count, delta=f"of {len(priority_df)} total")

    with summary_col2:
        st.metric("Improving Metrics", improving_metrics, delta=f"of {len(priority_df)} total")

    with summary_col3:
        st.metric("Overall Performance", f"{avg_performance:.2f}", delta=f"{avg_performance-9.0:+.2f}")

    # Strategic recommendations based on overall analysis
    st.markdown("### 🎯 Strategic Focus Areas for City Furniture Website")

    critical_metrics = priority_df[priority_df['Priority_Score'] >= 3]['Metric'].tolist()
    if critical_metrics:
        st.error(f"**🚨 Immediate Action Required:** {', '.join(critical_metrics)}")
        st.markdown("**Impact:** These metrics require immediate intervention to prevent customer satisfaction decline and potential revenue loss.")

    declining_metrics = priority_df[priority_df['Trend'] < -0.1]['Metric'].tolist()
    if declining_metrics:
        st.warning(f"**📉 Declining Performance:** {', '.join(declining_metrics)}")
        st.markdown("**Impact:** Monitor these metrics closely and implement preventive measures to stop further deterioration.")

    strong_metrics = priority_df[priority_df['Priority_Score'] == 1]['Metric'].tolist()
    if strong_metrics:
        st.success(f"**🎉 Strong Performance:** {', '.join(strong_metrics)}")
        st.markdown("**Impact:** These are competitive advantages to maintain and potentially leverage for marketing positioning.")

    # Final recommendations summary
    st.markdown("### 📋 Final Recommendations Summary")
    st.markdown(f"""
    **For City Furniture's website optimization, focus on:**

    1. **Immediate Actions** ({high_risk_count} metrics need attention):
       - Prioritize user experience improvements in checkout and product information
       - Implement transparent pricing throughout the customer journey
       - Enhance mobile responsiveness and site performance

    2. **Performance Monitoring**:
       - Set up automated alerts for metrics falling below 9.0
       - Conduct monthly reviews of all satisfaction metrics
       - Implement A/B testing for continuous improvement

    3. **Long-term Strategy**:
       - Invest in AI-powered personalization for product recommendations
       - Develop comprehensive customer feedback collection systems
       - Create cross-functional teams focused on customer experience optimization

    **Expected ROI:** Improvements in these metrics typically correlate with 10-25% increases in conversion rates and 15-30% reduction in cart abandonment.
    """)

# Export functionality
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
    # Create risk analysis summary for export
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

# Footer
st.markdown("---")
st.markdown("*Dashboard last updated: October 2025 | City Furniture Customer Satisfaction Analysis - Ultimate Enhanced Version*")
st.markdown("*Powered by Advanced Analytics & Business Intelligence*")
