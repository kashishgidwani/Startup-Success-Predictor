# Startup Success Predictor Dashboard

A Streamlit dashboard for analyzing startup success factors and metrics.

## Local Deployment

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
streamlit run dashboard.py
```

## Cloud Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Create a GitHub repository and push your code
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set the main file path to `dashboard.py`
7. Click "Deploy"

### Option 2: Heroku

1. Install the Heroku CLI
2. Create a `Procfile`:
```
web: streamlit run dashboard.py --server.port $PORT
```

3. Deploy to Heroku:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: AWS EC2

1. Launch an EC2 instance (Ubuntu recommended)
2. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv
```

3. Clone your repository and deploy:
```bash
git clone your-repo-url
cd your-repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Environment Variables

Create a `.env` file with:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## Troubleshooting

- If you see "All arrays must be of the same length" error, check your data in `unicorncompanies.csv`
- For deployment issues, ensure all dependencies are correctly specified in `requirements.txt`
- For Streamlit Cloud deployment, make sure your repository is public or you have a paid account

## Features

- Sector-wise analysis (Beauty, FinTech, Healthcare, EdTech, Quick Commerce)
- Comparative metrics visualization
- Financial performance tracking
- Growth metrics analysis
- Crisis response evaluation
- Startup viability predictor

## Data Structure

The dashboard analyzes companies based on five key sections:

1. Company Profile Data
   - Company Name
   - Sector
   - Founding Year
   - Founders
   - HQ Location
   - Initial Funding Details

2. Financial & Investment Data
   - Funding Rounds
   - Revenue History
   - Break-even Year
   - Profit Margins
   - CAC/LTV
   - Marketing Spend

3. Growth & Brand Metrics
   - Customer Growth
   - Social Engagement
   - NPS Score
   - Traffic Metrics
   - Repeat Purchase Rate

4. Strategy & Differentiation
   - Monetization Model
   - Product Innovations
   - Pivot History
   - Community Initiatives
   - Brand Storytelling

5. Crises & Response Data
   - Major Crises
   - Performance Impact
   - PR Strategy
   - Outcome Analysis

## Usage

1. Select your sector of interest from the sidebar
2. Explore key metrics and comparisons
3. Use the survival score predictor to assess your startup idea
4. Analyze successful vs. failed company patterns
5. Learn from crisis responses and strategic pivots

## Contributing

Feel free to submit issues and enhancement requests! 
