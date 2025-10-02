# City Furniture - Customer Satisfaction Dashboard

A comprehensive Streamlit dashboard for analyzing City Furniture customer satisfaction data from May 30 to September 30, 2025.

## 📊 Dashboard Features

### 🔹 Daily Timeline Tab
- **Interactive line chart** with satisfaction scores over time
- **Month filters** for focused analysis
- **Tooltips** with detailed information on hover
- **Target line at 9.0** with visual indicators
- **Red markers** for days below target
- Weekend highlighting and trend analysis

### 🔹 Monthly Comparison Tab
- **Bar charts** with monthly averages
- **Dropdown selector** for month comparison
- **Monthly performance cards** with color-coded status
- **Statistical summaries** including standard deviation
- Responsive layout for different screen sizes

### 🔹 Critical Events Tab
- **Sortable events table** with filtering options
- **Severity and promotion type filters**
- **Clickable dates** that highlight timeline positions
- **Impact analysis visualization**
- Detailed event descriptions and metrics

### 🔹 Risk Analysis Tab
- **Risk assessment matrix** with probability vs impact
- **Horizontal bar charts** for performance gaps
- **Severity level classification** (Low/Medium/High)
- **Detailed metric cards** with current vs target scores
- Interactive scatter plots and risk categorization

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git (for version control)
- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd city-furniture-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard locally:**
   ```bash
   streamlit run dashboard.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8501`

## 🌐 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **Create a new GitHub repository:**
   - Go to [github.com](https://github.com) and create a new repository
   - Name it something like `city-furniture-dashboard`
   - Make it public (required for free Streamlit Cloud)

2. **Upload your files:**
   ```bash
   git init
   git add .
   git commit -m "Initial dashboard setup"
   git branch -M main
   git remote add origin https://github.com/your-username/city-furniture-dashboard.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create a new app:**
   - Click "New app"
   - Select your GitHub repository
   - Choose the main branch
   - Set the main file path: `dashboard.py`
   - Click "Deploy!"

3. **Wait for deployment:**
   - Streamlit Cloud will automatically install dependencies from `requirements.txt`
   - The process usually takes 2-3 minutes

4. **Get your permanent link:**
   - Once deployed, you'll receive a permanent public URL like:
   - `https://your-username-city-furniture-dashboard-dashboard-xyz123.streamlit.app`

### Step 3: Share and Maintain

- **Share the link:** Your dashboard is now publicly accessible
- **Auto-updates:** Any changes pushed to your GitHub repository will automatically update the dashboard
- **Monitor usage:** Check the Streamlit Cloud dashboard for analytics

## 📱 Responsive Design

The dashboard is optimized for:
- **Desktop** (full feature set)
- **Tablet** (responsive layout)
- **Mobile** (mobile-friendly interface)

## 📥 Export Features

- **CSV Downloads:** Daily data and risk analysis
- **Interactive Filters:** Real-time data filtering
- **PNG Export:** Chart screenshots (via Plotly toolbar)

## 🔧 Customization

### Adding New Data
1. Modify the `load_data()` function in `dashboard.py`
2. Update data sources and date ranges
3. Adjust chart configurations as needed

### Styling Changes
- Modify the CSS in the `st.markdown()` section
- Update color schemes in Plotly charts
- Adjust responsive breakpoints

### New Features
- Add new tabs by extending the `st.tabs()` structure
- Include additional metrics and visualizations
- Integrate with external APIs or databases

## 🛠️ Troubleshooting

### Common Issues

**1. Deployment fails:**
- Check that all files are in the repository root
- Verify `requirements.txt` is properly formatted
- Ensure Python version compatibility

**2. Charts not displaying:**
- Check Plotly version compatibility
- Verify data format and column names
- Test locally first

**3. Performance issues:**
- Use `@st.cache_data` for data loading functions
- Optimize large datasets
- Consider data sampling for better performance

**4. Mobile display problems:**
- Test responsive CSS
- Check column layouts on smaller screens
- Verify touch interactions

### Getting Help

- **Streamlit Community:** [discuss.streamlit.io](https://discuss.streamlit.io)
- **Documentation:** [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Issues:** Create issues in your repository

## 📊 Data Structure

The dashboard uses the following data structure:

```python
# Daily satisfaction data
daily_df = pd.DataFrame({
    'date': datetime objects,
    'satisfaction_score': float (0-10),
    'month': string,
    'is_weekend': boolean,
    # ... additional columns
})

# Events data
events_df = pd.DataFrame({
    'date': datetime,
    'event': string,
    'severity': string ['High', 'Medium', 'Low'],
    'impact': string ['Positive', 'Negative'],
    'satisfaction_impact': string (e.g., '+1.5', '-2.0'),
    'promotion_type': string,
    'description': string
})

# Risk analysis data
risk_df = pd.DataFrame({
    'category': string,
    'probability': float (0-1),
    'impact': float (0-1),
    'current_score': float (0-10),
    'target_score': float (0-10),
    'risk_score': float (calculated),
    'performance_gap': float (calculated)
})
```

## 🎯 Performance Metrics

- **Page Load Time:** < 3 seconds
- **Chart Rendering:** < 1 second
- **Data Updates:** Real-time filtering
- **Mobile Compatibility:** Full feature parity

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Dashboard created with ❤️ using Streamlit**

*For support or questions, please create an issue in the GitHub repository.*
