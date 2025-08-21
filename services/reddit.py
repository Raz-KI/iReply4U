from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from auth import get_current_user
import models,json
import os
import asyncpraw,prawcore,praw
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer,util

model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    # username=os.getenv("REDDIT_USERNAME"),
    # password=os.getenv("REDDIT_PASSWORD"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db    
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[models.Customer, Depends(get_current_user)]

from groq import Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Business logic functions
def get_relevant_subreddits(product_desc):
    is_error = True
    while is_error:
        try:
            subreddits = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Your job is to return a list of 5 relevant subreddits for a given idea."},
                    {"role": "user", "content": "idea description: " + product_desc + ". Please provide a python list of 5 subreddits that are relevant to this idea."
                    "Return only the list of 5 subreddits, nothing else. Not even salutation or explanation just a python list of all the relevant subreddits."
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            list_of_subreddits = json.loads(subreddits.choices[0].message.content)
            is_error = False    
            valid_subreddits = []
            for sub_name in list_of_subreddits:
                try:
                    sub_name = sub_name[2:] #remove r/
                    _ = reddit.subreddit(sub_name).id  # triggers a request
                    valid_subreddits.append(sub_name)
                except prawcore.exceptions.Redirect:
                    print(f"Invalid subreddit skipped: {sub_name}")
                    continue
                except Exception as e:
                    print("Some error",e)
                    continue

            is_error = False
            return valid_subreddits

        except Exception as e:
            print("Error in get_relevant_subreddits:", e)
            print(subreddits.choices[0].message.content)
            

def search_reddit_posts(query, list_of_subreddits, limit=5):
    # Show hot posts from combined subreddits
    combined = "+".join(list_of_subreddits)
    # print("\n🔥 Hot posts from combined subreddits:\n")
    # for submission in reddit.subreddit(combined).hot(limit=10):
    #     print(submission.title,"This is the title")

    # Search individually across subreddits
    results = []
    for sub in list_of_subreddits:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.new(limit=limit):
            results.append({
                "subreddit": sub,
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "comments": submission.num_comments,
                "content": submission.selftext
            })

    return results


def filter_relevant_posts_llm(posts, product_desc):
    relevant_posts = []
    for post in posts:
        try:
            subreddits = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Your job is to tell wether the post is relevant to the product or not"},
                    {"role": "user", "content": "Post Title: " + post +" Product description: " + product_desc + ". If the post is relevant to the products description"
                    "return YES otherwise return NO"
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            print(subreddits.choices[0].message.content)
            # list_of_subreddits = json.loads(subreddits.choices[0].message.content)
        except Exception as e:
            print(e)
def filter_relevant_posts_embeddings(posts, product_desc):
    product_embedding = model.encode(product_desc, convert_to_tensor=True)

    # Generate embeddings for posts
    for post in posts:
        
        post_text = post["title"] + " " + post["content"]
        post["embedding"] = model.encode(post_text, convert_to_tensor=True)

    # Compute similarity
    for post in posts:
        similarity = util.cos_sim(product_embedding, post["embedding"]).item()
        post["similarity"] = similarity
        print(f"Post: {post['title']} - Similarity: {similarity:.4f}")

    # Rank posts
    ranked = sorted([post for post in posts if post["similarity"] > 0.4],key=lambda x: x["similarity"],reverse=True)


    # Print results
    # for post in ranked:
    #     print(f"{post['title']} -> relevance: {post['similarity']:.4f}")
    return ranked

# Main function to create a comment
def create_comment(product_id: int, db: Session):
    # Example: Generate a comment for Reddit
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    product_name = product.product_name
    product_desc = product.product_desc
    product_link = product.product_link
    
    

    list_of_subreddits = get_relevant_subreddits(product_desc)
    
    posts = search_reddit_posts(product_desc,list_of_subreddits)

    relevant_posts = filter_relevant_posts_embeddings(posts, product_desc)
    if not relevant_posts:
        print("No relevant posts found at the moment.")
    else:
        for post in relevant_posts:
            print("Post",post['title'],post['content'])
            try:
                reply = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": """You are ReplyGuy, an empathetic Reddit user.  
                            Your job is to write natural, helpful, and conversational comments.  
                            You must:
                            - First, show empathy or understanding of the post.  
                            - Second, give genuine advice or share an experience.  
                            - Third, if it makes sense, naturally mention the product [PRODUCT_DESCRIPTION].  
                            - Never sound like marketing. Avoid salesy words.  
                            - Always write like a normal Reddit user (3–6 sentences).  
                            - Keep it short, casual, and relevant.  
                            - VERY IMPORTANT: ONLY GENERATE THE COMMENT, NOTHING ELSE, NO SALUTATION, NO GREETING, NO EXPLANATION ABOUT THE COMMENT, JUST THE COMMENT ITSELF.
                            """
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Post Title: {post['title']}
                            Post Content: {post['content']}
                            Product Details: 
                                Product Name: {product_name}
                                Product Description: {product_desc}
                                Product Link: {product_link}
                            
                            Now write one natural Reddit comment following the system instructions. 
                            STRICTLY FOLLOW THE RULES AND DON’T GENERATE ANY EXTRA CONTENT, JUST THE COMMENT.
                            """
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )

                print("Reply Generated:", reply.choices[0].message.content.strip())

                # list_of_subreddits = json.loads(subreddits.choices[0].message.content)
            except Exception as e:
                print(e)