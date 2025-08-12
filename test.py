import os
import asyncpraw,praw
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    # username=os.getenv("REDDIT_USERNAME"),
    # password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)
def search_reddit_posts(query, subreddit_name, limit=5):
    subreddit = reddit.subreddit(subreddit_name)
    results = []
    for submission in subreddit.search(query, limit=limit):
        results.append({
            "title": submission.title,
            "url": submission.url,
            "score": submission.score,
            "comments": submission.num_comments
        })
    return results

# Test
# if __name__ == "__main__":
posts = search_reddit_posts("Python programming", "learnpython", 5)
for p in posts:
    print(p)