from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import requests
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging

sn = Blueprint("sn", __name__)

NEWS_API_KEY = "4018749ef228496d8440096348ceee6a"
TRADING_ECONOMICS_API_KEY = "d51c6a256c024f7:auxd96wyn3ybiau"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@sn.route("/news", methods=["GET", "POST"])
@login_required
def news():
    """Fetch and display business news articles"""
    url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWS_API_KEY}"
    articles = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        
        # Check if the API returned an error
        if data.get("status") == "error":
            error_message = data.get("message", "Unknown error from News API")
            logger.error(f"News API error: {error_message}")
            flash(f"Unable to fetch news: {error_message}", "warning")
        else:
            articles = data.get("articles", [])
            if not articles:
                flash("No news articles available at the moment.", "info")
            
    except requests.exceptions.Timeout:
        logger.error("News API request timed out")
        flash("Request timed out. Please try again later.", "error")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to News API")
        flash("Unable to connect to news service. Please check your internet connection.", "error")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from News API: {e}")
        flash(f"Error fetching news: {e}", "error")
    except ValueError as e:
        logger.error(f"Error parsing News API response: {e}")
        flash("Error processing news data.", "error")
    except Exception as e:
        logger.error(f"Unexpected error in news route: {e}")
        flash("An unexpected error occurred while fetching news.", "error")

    return render_template(
        "news.html",
        user=current_user,
        global_articles=articles,
    )


@sn.route("/stats", methods=["GET", "POST"])
@login_required
def get_stats():
    """Fetch and display GDP statistics for a country"""
    # Get country from form (POST) or query string (GET), default to Sweden
    if request.method == "POST":
        country = request.form.get("country", "sweden").lower().strip()
    else:
        country = request.args.get("country", "sweden").lower().strip()

    # Validate country input
    if not country:
        country = "sweden"
        flash("No country specified, showing Sweden data.", "info")

    url = (
        f"https://api.tradingeconomics.com/historical/country/{country}/indicator/gdp"
        f"?c={TRADING_ECONOMICS_API_KEY}&f=json"
    )
    
    stats_data = []
    gdp_plot_filename = None
    gdp_plot_page_filename = None
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Parse JSON response
        try:
            stats_data = response.json()
        except ValueError as json_error:
            logger.error(f"Error parsing JSON from Trading Economics API: {json_error}")
            flash("Error processing economic data. The API returned invalid data.", "error")
            stats_data = []
        
        # Handle different response types
        if isinstance(stats_data, dict):
            # Check if it's an error response
            if "message" in stats_data or "error" in stats_data:
                error_msg = stats_data.get("message") or stats_data.get("error", "Unknown error")
                logger.error(f"Trading Economics API error: {error_msg}")
                flash(f"Error from Trading Economics API: {error_msg}", "error")
                stats_data = []
            else:
                # Not an error, but unexpected format
                logger.warning("Unexpected dictionary response from Trading Economics API")
                flash(f"No GDP data available for {country.capitalize()}.", "warning")
                stats_data = []
        
        # Check if we have valid data
        if not stats_data or len(stats_data) == 0:
            logger.warning(f"No data returned for country: {country}")
            flash(f"No GDP data available for {country.capitalize()}. Please try a different country.", "warning")
        else:
            try:
                # Remove the last item (as in original code)
                if len(stats_data) > 1:
                    stats_data = stats_data[:-1]
                
                # Create DataFrame and plots
                data_frame = create_dataframe(stats_data)
                
                if data_frame is not None and not data_frame.empty:
                    gdp_plot_filename = plot_gdp_trend(data_frame, country)
                    
                    # Pagination logic
                    page = int(request.args.get("page", 1))
                    per_page = 10
                    start = (page - 1) * per_page
                    end = start + per_page
                    paged_stats = stats_data[start:end]
                    
                    # Create DataFrame for the current page
                    data_frame_page = create_dataframe(paged_stats)
                    if data_frame_page is not None and not data_frame_page.empty:
                        gdp_plot_page_filename = plot_gdp_page(data_frame_page, country)
                    
                    total = len(stats_data)
                else:
                    flash("Unable to process the GDP data received.", "error")
                    stats_data = []
                    
            except Exception as processing_error:
                logger.error(f"Error processing GDP data: {processing_error}")
                flash("Error processing GDP data. Please try again.", "error")
                stats_data = []
                
    except requests.exceptions.Timeout:
        logger.error("Trading Economics API request timed out")
        flash("Request timed out. The economic data service is taking too long to respond.", "error")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Trading Economics API")
        flash("Unable to connect to economic data service. Please check your internet connection.", "error")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from Trading Economics API: {e}")
        if e.response.status_code == 401:
            flash("API authentication failed. Please contact the administrator.", "error")
        elif e.response.status_code == 403:
            flash("Access denied to economic data service.", "error")
        elif e.response.status_code == 404:
            flash(f"GDP data not found for {country.capitalize()}.", "warning")
        elif e.response.status_code == 429:
            flash("Too many requests. Please try again in a few minutes.", "warning")
        else:
            flash(f"Error fetching economic data: {e}", "error")
    except Exception as e:
        logger.error(f"Unexpected error in stats route: {e}")
        flash("An unexpected error occurred while fetching economic statistics.", "error")

    # Pagination logic (handle case when stats_data is empty)
    page = int(request.args.get("page", 1))
    per_page = 10
    total = len(stats_data)
    start = (page - 1) * per_page
    end = start + per_page
    paged_stats = stats_data[start:end] if stats_data else []

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


def create_dataframe(stats_data):
    """
    Create a pandas DataFrame from stats data with error handling
    
    Args:
        stats_data: List of dictionaries containing GDP data
        
    Returns:
        DataFrame or None if creation fails
    """
    try:
        if not stats_data:
            logger.warning("Empty stats_data provided to create_dataframe")
            return None
            
        data_frame = pd.DataFrame(stats_data)
        
        # Validate required columns exist
        if "DateTime" not in data_frame.columns or "Value" not in data_frame.columns:
            logger.error("Required columns missing from data")
            return None
        
        # Convert DateTime column
        data_frame["DateTime"] = pd.to_datetime(
            data_frame["DateTime"], format="mixed", utc=True, errors="coerce"
        )
        
        # Drop rows with invalid dates
        data_frame = data_frame.dropna(subset=["DateTime"])
        
        if data_frame.empty:
            logger.warning("DataFrame empty after date parsing")
            return None
        
        data_frame.set_index("DateTime", inplace=True)
        data_frame.sort_index(inplace=True)
        
        return data_frame
        
    except KeyError as e:
        logger.error(f"Missing expected column in data: {e}")
        return None
    except Exception as e:
        logger.error(f"Error creating DataFrame: {e}")
        return None


def plot_gdp_trend(data_frame, country):
    """
    Plot GDP trend over time with error handling
    
    Args:
        data_frame: DataFrame containing GDP data
        country: Country name for the plot title
        
    Returns:
        Filename of the saved plot or None if plotting fails
    """
    try:
        if data_frame is None or data_frame.empty:
            logger.warning("Cannot plot empty DataFrame")
            return None
            
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
        
        # Ensure the static directory exists
        static_dir = os.path.join("website", "static")
        os.makedirs(static_dir, exist_ok=True)
        
        img_path = os.path.join(static_dir, "gdp_plot.png")
        plt.savefig(img_path)
        plt.close()
        
        return "gdp_plot.png"
        
    except Exception as e:
        logger.error(f"Error plotting GDP trend: {e}")
        plt.close()  # Make sure to close the figure even if there's an error
        return None


def plot_gdp_page(data_frame_page, country):
    """
    Plot GDP for paginated data with error handling
    
    Args:
        data_frame_page: DataFrame containing paginated GDP data
        country: Country name for the plot title
        
    Returns:
        Filename of the saved plot or None if plotting fails
    """
    try:
        if data_frame_page is None or data_frame_page.empty:
            logger.warning("Cannot plot empty DataFrame page")
            return None
            
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
        
        # Ensure the static directory exists
        static_dir = os.path.join("website", "static")
        os.makedirs(static_dir, exist_ok=True)
        
        img_path = os.path.join(static_dir, "gdp_plot_page.png")
        plt.savefig(img_path)
        plt.close()
        
        return "gdp_plot_page.png"
        
    except Exception as e:
        logger.error(f"Error plotting GDP page: {e}")
        plt.close()  # Make sure to close the figure even if there's an error
        return None
