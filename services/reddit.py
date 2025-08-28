import datetime
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
            
            

def search_reddit_posts(query, list_of_subreddits, limit=1):
    # Show hot posts from combined subreddits
    combined = "+".join(list_of_subreddits)

    # Search individually across subreddits
    results = []
    for sub in list_of_subreddits:
        subreddit = reddit.subreddit(sub)
        for submission in subreddit.new(limit=limit):
            results.append({
                "subreddit": sub,
                "post_id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "comments": submission.num_comments,
                "content": submission.selftext
            })

    return results


def filter_relevant_posts_llm(posts, product_desc):
    relevant_posts = []
    # test=[]
    for post in posts:
        try:
            relevantOrNot = client.chat.completions.create(
                messages=[
                    
                    {"role": "system", "content": "You are a strict binary classifier. For each post, respond with only 'YES' if the post is relevant to the product description, or 'NO' if it is not. Do not include anything else.STRICTLY GENERATE ONLY YES OR NO, NO OTHER TEXT IS NEEDED. ALWAYS FOLLOW THE RULE"},
                    {"role": "user", "content": "Post Title: "+post['title']+"Post Content: "+post['content']+"Product Description: "+product_desc+".Is this post relevant to the product description? Answer strictly with YES or NO.STRICTLY GENERATE NO OTHER CONTENT NOT EVEN SALUTATIONS AND NO EXPLANATIONS JUST A YES IF RELEVANT AND NO IF NOT RELEVANT"}
                
                ],
                model="llama-3.3-70b-versatile",
            )
            reply = relevantOrNot.choices[0].message.content
            # Choki to check if llm gave only YES or NO or not and only send the  title content and id forward
            text = reply.strip().lower()
            if text in ["yes", "YES","Yes"]:
                relevant_posts.append({"post_title":post['title'],"post_content":post['content'],"post_id":post['post_id']})
            elif "yes" in text or "YES" in text or "Yes" in text:
                relevant_posts.append({"post_title":post['title'],"post_content":post['content'],"post_id":post['post_id']})
        
        except Exception as e:
            print(e)
    return relevant_posts
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


    return ranked
def generate_reply(relevant_posts,product_name,product_desc,product_link,db: Session,product_id,current_user: user_dependency):

    if not relevant_posts:
        return "No Relevant Post at this moment..."
    else:
        for post in relevant_posts:
            # try:
            reply = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are ReplyGuy, an empathetic Reddit user.  
                        Your job is to write natural, helpful, and conversational comments.  
                        You must:
                        - First, show empathy or understanding of the post.  
                        - Second, give genuine advice or share an experience.  
                        - Third, naturally mention the [product_name] and how it helps [PRODUCT_DESCRIPTION].  
                        - Never sound like marketing. Avoid salesy words.  
                        - Always write like a normal Reddit user (3–6 sentences).  
                        - Keep it short, casual, and relevant.  
                        - VERY IMPORTANT: ONLY GENERATE THE COMMENT, NOTHING ELSE, NO SALUTATION, NO GREETING, NO EXPLANATION ABOUT THE COMMENT, JUST THE COMMENT ITSELF.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Post Title: {post["post_title"]}
                        Post Content: {post["post_content"]}
                        Product Details: 
                            Product Name: {product_name}
                            Product Description: {product_desc}
                            Product Link: {product_link}
                        
                        Now write one natural Reddit comment following the system instructions. 
                        Casually m
                        STRICTLY FOLLOW THE RULES AND DON’T GENERATE ANY EXTRA CONTENT, JUST THE COMMENT.
                        """
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            reply_text = reply.choices[0].message.content.strip()

            # Save in DB
            print("This is the post\n",post)
            print("This is the reply\n",reply_text)
            new_comment = models.Comment(
                post_id=post["post_id"],
                reply_text=reply_text,
                posted_at = datetime.datetime.utcnow(),
                post_title = post["post_title"],
                post_content = post["post_content"],
                product_id = product_id,
                customer_id=current_user["id"],
                platform="reddit"
            )
            db.add(new_comment)
            db.commit()

            print(f" Comment saved for post '{post["post_title"]}'")


# Main function to create a comment
def create_comment(product_id: int, db: Session,current_user:user_dependency):
    # Example: Generate a comment for Reddit
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    
    product_name = product.product_name
    product_desc = product.product_desc
    product_link = product.product_link
    
    print(product_name,product_desc)

    list_of_subreddits = get_relevant_subreddits(product_desc)
    
    posts = search_reddit_posts(product_desc,list_of_subreddits)

    # Filter out the posts which have the same product id and same subreddit post id
    existing_ids = {
    c.post_id
    for c in db.query(models.Comment.post_id)
                .filter(models.Comment.product_id == product_id)
                .all()
    }
    print("These Exists",existing_ids)
    new_posts = [p for p in posts if p["post_id"] not in existing_ids]
    

    relevant_posts = filter_relevant_posts_llm(new_posts, product_desc)
    print("These are the new posts",relevant_posts)
    replies = generate_reply(relevant_posts, product_name, product_desc, product_link, product_id=product_id, db=db, current_user=current_user)