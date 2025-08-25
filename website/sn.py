from flask import Blueprint, render_template
from flask_login import login_required, current_user
import requests

sn = Blueprint("sn", __name__)

NEWS_API_KEY = "4018749ef228496d8440096348ceee6a"


@sn.route("/news", methods=["GET", "POST"])
@login_required
def news():
    # NewsAPI for business headlines
    url = f"https://newsapi.org/v2/top-headlines?country=eg&category=business&apiKey={NEWS_API_KEY}"

    articles = []

    # Fetch articles (NewsAPI)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])

    return render_template(
        "news.html",
        user=current_user,
        global_articles=articles,  # Use the same variable as before for compatibility
    )


@sn.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    return render_template("stats.html", user=current_user)
