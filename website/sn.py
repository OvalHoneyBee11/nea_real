from flask import Blueprint, render_template
from flask_login import login_required, current_user
import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import os


sn = Blueprint("sn", __name__)

NEWS_API_KEY = "4018749ef228496d8440096348ceee6a"
TRADING_ECONOMICS_API_KEY = "d51c6a256c024f7:auxd96wyn3ybiau"


@sn.route("/news", methods=["GET", "POST"])
@login_required
def news():
    # NewsAPI for business headlines
    url = (
        f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
    )

    articles = []

    # Fetch articles (NewsAPI)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])

    return render_template(
        "news.html",
        user=current_user,
        global_articles=articles,
    )


@sn.route("/stats", methods=["GET", "POST"])
@login_required
def get_stats():
    url = (
        f"https://api.tradingeconomics.com/historical/country/sweden/indicator/gdp"
        f"?c={TRADING_ECONOMICS_API_KEY}&f=json"
    )
    stats_data = []
    response = requests.get(url)
    if response.status_code == 200:
        try:
            stats_data = response.json()
            if isinstance(stats_data, dict):
                stats_data = []
        except Exception as e:
            print("Error parsing JSON:", e)
            stats_data = []
    return render_template("stats.html", user=current_user, stats_data=stats_data)

def create_dataframe(stats_data):
    df = pd.DataFrame(stats_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def plot_gdp_trend(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Value'], marker='o', linestyle='-')
    plt.title('Sweden GDP Over Time')
    plt.xlabel('Date')
    plt.ylabel('GDP Value')
    plt.grid(True)
    img_path = os.path.join('website', 'static', 'gdp_trend.png')
    plt.savefig(img_path)
    plt.close()
    return img_path