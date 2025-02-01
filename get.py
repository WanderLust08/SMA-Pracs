import praw
import json
import time

# Set up Reddit API credentials
reddit = praw.Reddit(
    client_id="4wMHyfMxZUJZdX_xQwPU0Q",
    client_secret="76dH47Tja8nDn5PmFCYcdNN75KxmaQ",
    user_agent="MalnutritionResearchBot"
)

# Define relevant subreddits and keywords (removed India-related searches)
subreddits = ["nutrition", "publichealth", "poverty", "globalhealth", "health"]
keywords = ["malnutrition", "undernutrition", "stunting", "nutritionaldeficiency", "globalmalnutrition", "hunger"]

# Function to fetch top comments from a post
def fetch_comments(submission, comment_limit=5):
    submission.comments.replace_more(limit=0)  # Load all top-level comments
    sorted_comments = sorted(submission.comments, key=lambda c: c.score, reverse=True)  # Sort by score

    comments = []
    for top_comment in sorted_comments[:comment_limit]:  # Get highest-scoring comments
        if len(top_comment.body) < 10 or (top_comment.author and top_comment.author.name == "AutoModerator"):  # Ignore short comments and AutoModerator
            continue
        
        comments.append({
            "comment_text": top_comment.body,
            "comment_author": top_comment.author.name if top_comment.author else "Deleted",
            "score": top_comment.score
        })

    return comments

# Function to fetch posts from Reddit
def fetch_reddit_posts(subreddit_name, keyword, limit=500):
    posts = []
    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.search(keyword, limit=limit):
        if not submission.selftext.strip():  # Ignore posts with no text
            continue
        
        posts.append({
            "title": submission.title,
            "text": submission.selftext,
            "url": submission.url,
            "author": submission.author.name if submission.author else "Deleted",  # Get post author
            "score": submission.score,
            "comments_count": submission.num_comments,
            "created_utc": submission.created_utc,
            "subreddit": submission.subreddit.display_name,
            "comments": fetch_comments(submission)  # Include top comments with authors
        })
        
    return posts

# Fetch posts for each subreddit and keyword
all_posts = {}

for subreddit in subreddits:
    for keyword in keywords:
        key = f"{subreddit}_{keyword}"  # Unique key for each search
        print(f"Fetching posts for r/{subreddit} with keyword '{keyword}'...")
        all_posts[key] = fetch_reddit_posts(subreddit, keyword)

# Save data to JSON
json_filename = "reddit_malnutrition_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, indent=4)

print(f"Reddit data saved to {json_filename}")
