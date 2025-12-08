from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
import requests
import matplotlib.pyplot as plt
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
    # Get country from form (POST) or query string (GET), default to Sweden
    if request.method == "POST":
        country = request.form.get("country", "sweden").lower()
    else:
        country = request.args.get("country", "sweden").lower()

    url = (
        f"https://api.tradingeconomics.com/historical/country/{country}/indicator/gdp"
        f"?c={TRADING_ECONOMICS_API_KEY}&f=json"
    )
    stats_data = []
    gdp_plot_filename = None
    response = requests.get(url)
    if response.status_code == 200:
        try:
            stats_data = response.json()
            if isinstance(stats_data, dict):
                stats_data = []
            stats_data = stats_data[:-1]
            if stats_data and len(stats_data) > 0:
                data_frame = create_dataframe(stats_data)
                gdp_plot_filename = plot_gdp_trend(data_frame, country)
        except Exception as e:
            print("Error parsing JSON:", e)
            stats_data = []

    # Pagination logic
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paged_stats = stats_data[start:end]
    total = len(stats_data)

    # Create DataFrame for all data and for the current page
    data_frame = create_dataframe(stats_data)
    data_frame_page = create_dataframe(paged_stats)

    # Plot the full graph and the page graph
    gdp_plot_filename = plot_gdp_trend(data_frame, country)
    gdp_plot_page_filename = plot_gdp_page(data_frame_page, country)

    return render_template(
        "stats.html",
        user=current_user,
        stats_data=paged_stats,
        gdp_plot_filename=gdp_plot_filename,
        gdp_plot_page_filename=gdp_plot_page_filename,
        page=page,
        per_page=per_page,
        total=total,
        country=country.capitalize(),
    )


@sn.route("/portal/stats")
@login_required
def stats_portal():
    """Minimal preview for home page iframe"""
    return render_template("portals/stats_portal.html")


def create_dataframe(stats_data):
    data_frame = pd.DataFrame(stats_data)
    data_frame["DateTime"] = pd.to_datetime(
        data_frame["DateTime"], format="mixed", utc=True
    )
    data_frame.set_index("DateTime", inplace=True)
    data_frame.sort_index(inplace=True)
    return data_frame


def plot_gdp_trend(data_frame, country):
    plt.figure(figsize=(10, 6))
    plt.plot(
        data_frame.index,
        data_frame["Value"],
        marker="o",
        linestyle="-",
        linewidth=2,
        markersize=4,
    )
    plt.title(f"{country.capitalize()} GDP Over Time", fontsize=16, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel(f"{country.capitalize()} GDP Value", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_path = os.path.join("website", "static", "gdp_plot.png")
    plt.savefig(img_path)
    plt.close()
    return "gdp_plot.png"


def plot_gdp_page(data_frame_page, country):
    plt.figure(figsize=(8, 4))
    plt.plot(
        data_frame_page.index,
        data_frame_page["Value"],
        marker="o",
        linestyle="-",
        color="orange",
    )
    plt.title(f"{country.capitalize()} GDP (Selected Period)", fontsize=14)
    plt.xlabel("Date", fontsize=10)
    plt.ylabel(f"{country.capitalize()} GDP Value", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    img_path = os.path.join("website", "static", "gdp_plot_page.png")
    plt.savefig(img_path)
    plt.close()
    return "gdp_plot_page.png"
