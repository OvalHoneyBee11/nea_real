from flask import Blueprint, render_template
from flask_login import login_required, current_user
import requests
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
def stats():
    url = (
        f"https://api.tradingeconomics.com/historical/country/sweden/indicator/gdp"
        f"?c={TRADING_ECONOMICS_API_KEY}&f=json"
    )
    stats_data = []
    response = requests.get(url)
    print("Trading Economics API response:", response.text)
    if response.status_code == 200:
        try:
            stats_data = response.json()
            if isinstance(stats_data, dict):
                stats_data = []
        except Exception as e:
            print("Error parsing JSON:", e)
            stats_data = []
    return render_template("stats.html", user=current_user, stats_data=stats_data)
