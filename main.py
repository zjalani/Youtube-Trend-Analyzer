import requests
import pandas as pd
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")

# -------------------------------
# Get Category Mapping (ID -> Name)
# -------------------------------
def get_category_mapping(api_key):
    url = "https://www.googleapis.com/youtube/v3/videoCategories"
    
    params = {
        "part": "snippet",
        "regionCode": "US",
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    category_map = {}
    
    for item in data["items"]:
        category_map[item["id"]] = item["snippet"]["title"]
    
    return category_map


# -------------------------------
# Fetch Trending Videos
# -------------------------------
def get_trending_videos(api_key, category_map):
    url = "https://www.googleapis.com/youtube/v3/videos"
    
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "US",
        "maxResults": 50,
        "key": api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    videos = []
    
    for item in data["items"]:
        video = {
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "category": category_map.get(item["snippet"]["categoryId"], "Unknown")
        }
        videos.append(video)
    
    return pd.DataFrame(videos)


# -------------------------------
# Main Execution
# -------------------------------
def main():
    if not API_KEY:
        print("Error: API_KEY not found. Check your .env file.")
        return
    
    # Get category names
    category_map = get_category_mapping(API_KEY)
    
    # Get trending videos
    df = get_trending_videos(API_KEY, category_map)
    
    # -------------------------------
    # Analysis
    # -------------------------------
    print("\n=== Sample Data ===")
    print(df.head())
    
    print("\n=== Top 5 Most Viewed Videos ===")
    print(df.sort_values(by="views", ascending=False)[["title", "views"]].head())
    
    print("\n=== Average Views ===")
    print(df["views"].mean())
    
    print("\n=== Top Categories ===")
    print(df["category"].value_counts().head())
    
    # Engagement Rate
    df["engagement_rate"] = df["likes"] / df["views"]
    
    print("\n=== Top Engagement Videos ===")
    print(df.sort_values(by="engagement_rate", ascending=False)[["title", "engagement_rate"]].head())
    
    # -------------------------------
    # Visualization
    # -------------------------------
    top_videos = df.sort_values(by="views", ascending=False).head(10)
    
    plt.figure()
    plt.barh(top_videos["title"], top_videos["views"])
    plt.xlabel("Views")
    plt.title("Top 10 Trending Videos by Views")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()