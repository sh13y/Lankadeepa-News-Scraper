import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

NEWS_URL = "https://www.lankadeepa.lk/latest_news/1"
LOG_FILE = "news_log.json"
MARKDOWN_FILE = "README.md"

def fetch_full_content(news_url):
    response = requests.get(news_url)
    if response.status_code != 200:
        print(f"Failed to fetch content from {news_url}.")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Assuming content is inside a div with a specific class, you can update this selector
    content = soup.find("div", class_="article-body")  # Modify class name accordingly

    if content:
        paragraphs = content.find_all("p")
        full_content = "\n\n".join([para.get_text(strip=True) for para in paragraphs])
        return full_content
    else:
        return "Full content not found."

def fetch_news():
    response = requests.get(NEWS_URL)
    if response.status_code != 200:
        print("Failed to fetch news.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    news_items = []

    # Adjust the selector to match the structure of news articles in the page
    for news_div in soup.find_all("div", class_="col-md-10 col-lg-9 p-b-20 leftcol"):  # Modify the class as needed
        link = news_div.find("a", href=True)["href"]
        title = news_div.find("h5", class_="p-b-0").get_text(strip=True)  # Adjust title class
        date = news_div.find("span", class_="f1-s-4 cl8 hov-cl10 trans-03 timec").get_text(strip=True)  # Adjust date class
        short_desc = news_div.find("a", class_="f1-s-5 cl3 hov-cl10 trans-03").get_text(strip=True)

        image_url = news_div.find("img")["src"]  # Assuming the image URL is in the <img> tag

        # Fetch the full content for the news
        full_content = fetch_full_content(link)

        news_items.append({
            "link": link,
            "title": title,
            "date": date,
            "short_desc": short_desc,
            "image_url": image_url,
            "full_content": full_content
        })

    return news_items

def read_log():
    return json.load(open(LOG_FILE, "r", encoding="utf-8")) if os.path.exists(LOG_FILE) else []

def update_log(new_links):
    logged_links = read_log() + new_links
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logged_links, f, indent=4)

def format_news_to_markdown(news):
    markdown = ""
    for item in news:
        try:
            formatted_date = datetime.strptime(item["date"], "%d %m %Y").strftime("%B %d, %Y")
        except ValueError:
            formatted_date = item["date"]
        markdown += f"## {item['title']}\n\n"
        markdown += f"Published: {formatted_date}\n\n"
        markdown += f"{item['short_desc']}\n\n"
        markdown += f"![Image]({item['image_url']})\n\n"
    return markdown

def update_readme(news_items):
    markdown_content = format_news_to_markdown(news_items)
    with open(MARKDOWN_FILE, "a", encoding="utf-8") as f:
        f.write(markdown_content)

def main():
    all_news = fetch_news()
    logged_links = read_log()
    new_news = [news for news in all_news if news["link"] not in logged_links]

    if new_news:
        update_log([news["link"] for news in new_news])
        update_readme(new_news)
        print(f"{len(new_news)} new articles added.")
    else:
        print("No new articles to update.")

if __name__ == "__main__":
    main()
