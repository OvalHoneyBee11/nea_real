from flask import Blueprint, render_template
from flask_login import login_required, current_user
import requests  # <-- Add this import

sn = Blueprint("sn", __name__)

NEWS_API_KEY = "2f83f7ade2d94f589ddd761ba4a3a42b"  # Replace with your NewsAPI.org key


@sn.route("/news", methods=["GET", "POST"])
@login_required
def news():
    # Fetch global business (economics) headlines from NewsAPI
    url = (
        f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url)
    articles = []
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])
    else:
        articles = []

    return render_template("news.html", user=current_user, articles=articles)


@sn.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    return render_template("stats.html", user=current_user)
