from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    company_name = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_login = Column(TIMESTAMP)

    reddit_accounts = relationship("RedditAccount", back_populates="customer", cascade="all, delete")
    products = relationship("Product", back_populates="customer", cascade="all, delete")
    comments = relationship("Comment", back_populates="customer", cascade="all, delete")  


class RedditAccount(Base):
    __tablename__ = "reddit_accounts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    username = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expiry = Column(TIMESTAMP)
    connected_at = Column(TIMESTAMP, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="reddit_accounts")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String, nullable=False)
    product_desc = Column(Text, nullable=False)
    product_link = Column(Text, nullable=False)
    is_active = Column(String, default="active")  
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    platform = Column(String, nullable=False) 

    customer = relationship("Customer", back_populates="products")
    subreddits = relationship("Subreddit", back_populates="product", cascade="all, delete")
    comments = relationship("Comment", back_populates="product", cascade="all, delete")

class Subreddit(Base):
    __tablename__ = "subreddits"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    source = Column(String, default="AI")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    product = relationship("Product", back_populates="subreddits")
    reddit_posts = relationship("RedditPost", back_populates="subreddit", cascade="all, delete")


class RedditPost(Base):
    __tablename__ = "reddit_posts"

    id = Column(Integer, primary_key=True, index=True)
    subreddit_id = Column(Integer, ForeignKey("subreddits.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(String, nullable=False)
    title = Column(Text)
    body = Column(Text)
    url = Column(Text)
    upvotes = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    subreddit = relationship("Subreddit", back_populates="reddit_posts")
    replies = relationship("Reply", back_populates="reddit_post", cascade="all, delete")


class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("reddit_posts.id", ondelete="CASCADE"), nullable=False)
    reply_text = Column(Text, nullable=False)
    status = Column(String, default="draft")  
    posted_at = Column(TIMESTAMP)

    reddit_post = relationship("RedditPost", back_populates="replies")

class Comment(Base): 
    __tablename__ = "comments" 

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Text)
    reply_text = Column(Text, nullable=False)
    posted_at = Column(TIMESTAMP)
    post_title = Column(Text, nullable=False)
    post_content = Column(Text, nullable=False)
    platform = Column(String, default="reddit")

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False) 

    product = relationship("Product", back_populates="comments")
    customer = relationship("Customer", back_populates="comments")  
