# import os
# import praw
# from dotenv import load_dotenv

# load_dotenv()

# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
#     # username=os.getenv("REDDIT_USERNAME"),
#     # password=os.getenv("REDDIT_PASSWORD"),
#     user_agent=os.getenv("REDDIT_USER_AGENT")
# )
# def search_reddit_posts(query, subreddit_name, limit=5):
#     subreddit = reddit.subreddit(subreddit_name)
#     results = []
#     for submission in subreddit.search(query, limit=limit):
#         results.append({
#             "title": submission.title,
#             "url": submission.url,
#             "score": submission.score,
#             "comments": submission.num_comments
#         })
#     return results

# # Test
# # if __name__ == "__main__":
# # posts = search_reddit_posts("Python programming", "learnpython", 5)
# # for p in posts:
# #     print(p)

# from groq import Groq
# client = Groq(
#     api_key="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"
# )
# chat_completion = client.chat.completions.create(
#         messages=[
#             {"role": "system", "content": "Answer in sarcastic tone"},
#             {"role": "user", "content": "how are you"}
#         ],
#         model="llama3-8b-8192",
#     )
# print(chat_completion.choices[0].message.content)

# reddit = praw.Reddit(
#     client_id=os.getenv("REDDIT_CLIENT_ID"),
#     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
#     # username=os.getenv("REDDIT_USERNAME"),
#     # password=os.getenv("REDDIT_PASSWORD"),
#     user_agent=os.getenv("REDDIT_USER_AGENT")
# )

# valid_subreddits = []
# list_of_subreddits = ["r/LongDistance", "r/relationships", "r/online relationships", "r/distance", "r/longdistancecouples"]
# for sub_name in list_of_subreddits:
#     sub_name = sub_name[2:]
#     subreddit = reddit.subreddit(sub_name).id
#     print(subreddit)

# list_of_subreddits = ['longdistance', 'relationships', 'distance']
# # for subreddit in list_of_subreddits:
# #     subreddit = reddit.subreddit(subreddit)
# #     posts=[]
# for submission in reddit.subreddit("longdistance").hot(limit=25):
#     print(submission.title)
from sentence_transformers import SentenceTransformer, util

# Load a small, free model (fast + good quality)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Product description
product_desc = "AI app that helps IELTS students practice writing and speaking."
product_embedding = model.encode(product_desc, convert_to_tensor=True)

# Example scraped Reddit posts
posts = [
    {"title": "Best apps for IELTS writing practice?", "body": "Looking for recommendations."},
    {"title": "Struggling with IELTS writing task 2", "body": "Need apps to practice daily."},
    {"title": "Best movies for learning English?", "body": "Looking for fun ways to improve vocabulary."},
    {"title": "What SHould i cook for dinner TOday?", "body": "Anyone available to help?"}
]

# Generate embeddings for posts
for post in posts:
    post_text = post["title"] + " " + post["body"]
    post["embedding"] = model.encode(post_text, convert_to_tensor=True)

# Compute similarity
for post in posts:
    similarity = util.cos_sim(product_embedding, post["embedding"]).item()
    post["similarity"] = similarity

# Rank posts
ranked = sorted(posts, key=lambda x: x["similarity"], reverse=True)

# Print results
for post in ranked:
    print(f"{post['title']} -> relevance: {post['similarity']:.4f}")
