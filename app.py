import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os

# Set up local MongoDB connection
def get_mongo_client():
    # Create data directory if it doesn't exist
    if not os.path.exists('mongodb_data'):
        os.makedirs('mongodb_data')
    
    # Connect to local MongoDB with data in project folder
    client = MongoClient('mongodb://localhost:27017/')
    
    # Create or get database and collection
    db = client['blog_db']
    posts_collection = db['posts']
    
    return client, posts_collection

# Initialize MongoDB
client, posts_collection = get_mongo_client()

# Streamlit App
st.title("MongoDB Blogging Platform")
st.write("A basic blog with local MongoDB storage")

# Sidebar for new posts
with st.sidebar:
    st.header("Create New Post")
    title = st.text_input("Title")
    content = st.text_area("Content")
    if st.button("Publish"):
        if title and content:
            new_post = {
                "title": title,
                "content": content,
                "author": "User",
                "likes": 0,
                "comments": [],
                "date": datetime.now()
            }
            posts_collection.insert_one(new_post)
            st.success("Post published!")

# Display all posts
st.header("Recent Posts")
for post in posts_collection.find().sort("date", -1):
    with st.expander(f"**{post['title']}** (👍 {post['likes']})"):
        st.write(post["content"])
        st.caption(f"Posted by {post['author']} on {post['date'].strftime('%B %d, %Y')}")

        # Like button
        if st.button(f"Like ({post['likes']})", key=f"like_{post['_id']}"):
            posts_collection.update_one(
                {"_id": post["_id"]},
                {"$inc": {"likes": 1}}
            )
            st.rerun()

        # Comments section
        st.subheader("💬 Comments")
        for comment in post.get("comments", []):
            st.text(f"{comment['user']}: {comment['text']}")

        # Add comment
        new_comment = st.text_input("Add a comment", key=f"comment_{post['_id']}")
        if st.button("Post Comment", key=f"post_comment_{post['_id']}"):
            if new_comment:
                posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$push": {"comments": {"user": "Guest", "text": new_comment}}}
                )
                st.rerun()

# Close connection when done
client.close()
