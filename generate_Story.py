import os
import random
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import nltk
import psycopg2
from nltk.tokenize import sent_tokenize

# Download required NLTK data
nltk.download('punkt')


# Set up the PostgreSQL database connection
def setup_database():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id SERIAL PRIMARY KEY,
            genre TEXT,
            story TEXT
        )
    ''')
    conn.commit()
    return conn


# Function to scrape Reddit for paranormal stories
def scrape_reddit(subreddit):
    url = f'https://www.reddit.com/r/{subreddit}/top/.rss'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')

    items = soup.find_all('entry')
    story_texts = []
    for item in items:
        title = item.title.get_text()
        summary = item.summary.get_text()
        story_texts.append(f"{title}: {summary}")

    return story_texts


# Function to scrape Google for paranormal-related stories
def scrape_google(query, num_results=5):
    google_results = []
    for result in search(query, num_results=num_results, stop=num_results, lang="en"):
        response = requests.get(result)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.string if soup.title else "No title"
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs[:3]])

        google_results.append(f"{title}: {content}")

    return google_results


# Function to scrape true crime subreddit for stories
def scrape_true_crime_reddit(subreddit):
    url = f'https://www.reddit.com/r/{subreddit}/top/.rss'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'xml')

    items = soup.find_all('entry')
    story_texts = []
    for item in items:
        title = item.title.get_text()
        summary = item.summary.get_text()
        story_texts.append(f"{title}: {summary}")

    return story_texts


# Function to scrape a true crime blog
def scrape_true_crime_blog():
    url = 'https://crimereads.com/category/true-crime/'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    story_texts = []
    articles = soup.find_all('article')

    for article in articles[:5]:
        title = article.find('h2').get_text()
        summary = article.find('p').get_text()
        story_texts.append(f"{title}: {summary}")

    return story_texts


# Expanded hooks, twists, and call-to-actions for variety
hooks = ["You won't believe this creepy story!", "Get ready for a wild ride...", "This case will give you goosebumps!",
         "Here's a spooky mystery no one can explain...", "Ever heard of this eerie urban legend?",
         "Something terrifying just happened...", "Buckle up for a story you can't miss...",
         "This one will keep you up at night..."]

twists = ["But here's the part that no one saw coming...", "And then something even stranger happened...",
          "Here's where it gets seriously spooky...", "But there’s an eerie twist to this story...",
          "What happens next is beyond belief...", "Things took a sinister turn after this..."]

call_to_actions = ["Do you think this was real? Comment below!",
                   "Have you ever seen something like this? Drop your story!",
                   "What do you think really happened? Let me know!",
                   "Do you believe in ghosts? Tag someone who needs to see this!",
                   "What would you do if this happened to you? Tell us in the comments!",
                   "Think this is just a myth, or is there something more to it? Share your thoughts!",
                   "Ever had a paranormal experience? I want to hear your story!"]


# Function to rewrite a story for TikTok/Reels
def rewrite_story_for_tiktok(story, genre):
    sentences = sent_tokenize(story)

    hook = random.choice(hooks)
    main_event = " ".join(sentences[:2]) if len(sentences) > 1 else story
    twist = random.choice(twists)
    call_to_action = random.choice(call_to_actions)

    rewritten_story = f"{hook} {main_event} {twist} {call_to_action}"
    return rewritten_story


# Function to save the story to the database
def save_story_to_db(conn, genre, story):
    cursor = conn.cursor()

    # Check if the story already exists in the database
    cursor.execute('SELECT COUNT(*) FROM stories WHERE story = %s', (story,))
    count = cursor.fetchone()[0]

    # Insert only if the story is not a duplicate
    if count == 0:
        cursor.execute('INSERT INTO stories (genre, story) VALUES (%s, %s)', (genre, story))
        conn.commit()
        print(f"Saved new story: {story[:30]}...")  # Print a snippet of the saved story
    else:
        print("Duplicate story found, not saving.")


# Function to randomly select a genre and generate stories
def generate_random_content(conn):
    genres = ['paranormal', 'true crime']
    selected_genre = random.choice(genres)

    all_stories = []

    if selected_genre == 'paranormal':
        paranormal_stories = scrape_reddit('Paranormal') + scrape_google("paranormal ghost stories", num_results=5)
        all_stories.extend(paranormal_stories)
    elif selected_genre == 'true crime':
        true_crime_stories = scrape_true_crime_reddit('TrueCrime') + scrape_true_crime_blog()
        all_stories.extend(true_crime_stories)

    for story in all_stories:
        rewritten_story = rewrite_story_for_tiktok(story, selected_genre)
        save_story_to_db(conn, selected_genre, rewritten_story)


# Main function to run everything
def main():
    conn = setup_database()
    generate_random_content(conn)
    conn.close()


# Run the script
if __name__ == '__main__':
    main()
