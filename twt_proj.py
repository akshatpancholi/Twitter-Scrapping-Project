import streamlit as st
import pandas as pd
import sqlite3
import tweepy
from PIL import Image
from datetime import date
import json

# ==============================
# TWITTER API SETUP (Tweepy)
# ==============================
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOIz3QEAAAAAWHkgkdHkkmLq%2B7pEPd0C4uTeI54%3DBbafq95aIJYWXG3izDfd813WbScufmrjdmghnr0FdDYKHPqyjC"  # 🔁 Replace this with your real token
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# ==============================
# DATABASE SETUP (SQLite3)
# ==============================
conn = sqlite3.connect("tweets.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id TEXT PRIMARY KEY,
        date TEXT,
        username TEXT,
        content TEXT
    )
''')
conn.commit()

# ==============================
# STREAMLIT WEB APP
# ==============================
def main():
    st.title("Twitter Scraping App (SQLite + Streamlit)")

    menu = ["Home", "About", "Search", "Display", "Download"]
    choice = st.sidebar.selectbox("Menu", menu)

    # HOME TAB
    if choice == "Home":
        st.write('''
        This app scrapes recent tweets using the Twitter API and saves them into a local SQLite3 database.
        You can display the tweets and download them as CSV or JSON.
        ''')
        image = Image.open("D:\Desktop\Twitter scrapping\elonmusktwt.png")
        st.image(image, caption="Twitter Scraping", use_column_width=True)

    # ABOUT TAB
    elif choice == "About":
        with st.expander("About Tweepy"):
            st.write("Tweepy is the official Python library to access Twitter's API safely and reliably.")
        with st.expander("About SQLite"):
            st.write("SQLite is a lightweight, file-based database — perfect for small projects like this.")
        with st.expander("About Streamlit"):
            st.write("Streamlit turns Python scripts into beautiful web apps for data science and ML.")

    # SEARCH TAB
    elif choice == "Search":
        with st.form(key="search_form"):
            st.subheader("Search Tweets 🔍")
            query = st.text_input("Enter keyword or hashtag (no # needed)")
            limit = st.slider("Number of tweets to fetch", 10, 100, 20)
            start_date = st.date_input("Start date", value=date.today())
            end_date = st.date_input("End date", value=date.today())
            submit = st.form_submit_button("Fetch Tweets")

        if submit:
            if not query:
                st.warning("Please enter a keyword.")
            else:
                st.info(f"Fetching tweets for '{query}' ...")
                try:
                    tweets = client.search_recent_tweets(
                        query=query,
                        max_results=limit,
                        tweet_fields=["created_at"],
                        expansions="author_id"
                    )

                    if tweets.data:
                        usernames = {u.id: u.username for u in tweets.includes['users']}
                        inserted = 0
                        for tweet in tweets.data:
                            tid = tweet.id
                            content = tweet.text
                            user = usernames.get(tweet.author_id, "unknown")
                            tdate = str(tweet.created_at)

                            try:
                                c.execute("INSERT INTO tweets (id, date, username, content) VALUES (?, ?, ?, ?)",
                                          (tid, tdate, user, content))
                                conn.commit()
                                inserted += 1
                            except sqlite3.IntegrityError:
                                pass  # Duplicate tweet

                        st.success(f"{inserted} new tweets inserted into database.")
                    else:
                        st.warning("No tweets found.")

                except Exception as e:
                    st.error(f"Error occurred: {e}")

    # DISPLAY TAB
    elif choice == "Display":
        st.subheader("Stored Tweets 🗃️")
        df = pd.read_sql_query("SELECT * FROM tweets ORDER BY date DESC", conn)
        st.dataframe(df)

    # DOWNLOAD TAB
    elif choice == "Download":
        df = pd.read_sql_query("SELECT * FROM tweets ORDER BY date DESC", conn)

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name='tweets.csv',
                mime='text/csv'
            )

        with col2:
            json_data = df.to_json(orient="records", indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name='tweets.json',
                mime='application/json'
            )

        st.success("Download complete.")

# ==============================
# RUN APP
# ==============================
if __name__ == '__main__':
    main()
