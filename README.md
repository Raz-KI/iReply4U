AI-powered social media engagement assistant that finds relevant posts across platforms (Reddit, Twitter/X, LinkedIn, etc.) and generates empathetic, natural-sounding comments to join conversations and promote your product without sounding salesy.

🔹 Features:

Web scraping + keyword search to discover relevant posts

LLaMA-powered AI comment generation (empathetic, conversational, non-salesy)

Product-aware replies with natural integration of name + link

FastAPI backend with modular architecture

Database: Supabase (Postgres) via Supabase Python client
    - Set env vars: SUPABASE_URL, SUPABASE_ANON_KEY (or SUPABASE_SERVICE_ROLE_KEY)
    - Replace previous SQLAlchemy/Postgres local setup

Env vars required for external services:
    - GROQ_API_KEY
    - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

Secure key management via environment variables
