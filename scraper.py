import json
import requests
from bs4 import BeautifulSoup
import re
import os

BLOG_URL = "https://zfont-db.blogspot.com/"
OUT_DIR = os.getcwd()


def parse_slider(slider_text):
    print("[INFO] Parsing slider content.")
    try:
        return json.loads(slider_text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse slider JSON: {e}")
        return {}


def parse_labels(labels_soup):
    print("[INFO] Parsing labels.")
    labels = {}
    try:
        labels = {
            label.find("a").text: re.sub(r"\D", "", label.find("span").text)
            for label in labels_soup.find_all("li")
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse labels: {e}")
    return labels


def get_posts(url):
    print(f"[INFO] Fetching posts from URL: {url}")
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    next_url = None
    older_link = soup.find(class_="blog-pager-older-link")
    if older_link:
        next_url = older_link['href']
    return next_url


def collect_by_label(label):
    url = f"{BLOG_URL}/search/label/{label}"
    print(f"[INFO] Collecting posts for label: {label}")
    posts = []
    while url:
        print(f"[INFO] Fetching URL: {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        for item in soup.find_all(class_="post-outer-container"):
            thumb_element = item.find("img", id="z_thumb")
            info_element = item.find("div", id="z_info")
            title_element = item.find(class_="post-title entry-title")

            if thumb_element and info_element and title_element:
                try:
                    thumb = thumb_element.get("src")
                    info = json.loads(info_element.text)
                    title = title_element.text.strip()

                    info.update({"n": title, "t": thumb, "c": label})
                    posts.append(info)
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to parse JSON for post: {title_element.text.strip()}")
                except Exception as e:
                    print(f"[ERROR] An error occurred while processing a post: {e}")

        older_link = soup.find(class_="blog-pager-older-link")
        url = older_link['href'] if older_link else None
    print(f"[INFO] Found {len(posts)} posts for label: {label}")
    return posts


def save_json(data, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[INFO] Successfully saved data to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save data to {filename}: {e}")


def main():
    print("[INFO] Starting scraping process.")
    res = requests.get(BLOG_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    print("[INFO] Collecting slider items.")
    slider = parse_slider(soup.find(id="z_slider").text)

    print("[INFO] Collecting categories.")
    labels = parse_labels(soup.find(id="z_labels"))

    print("[INFO] Collecting all posts.")
    for label in labels:
        items = collect_by_label(label)
        filename = os.path.join(OUT_DIR, f"{label}.json")

        if label == "Featured":
            # Remove this lable from labels, we dont need to save in json
            tmp_labels = dict(labels)
            del tmp_labels[label]
            main_json = {"featured": items, "categories": tmp_labels, "slider": slider}
            save_json(main_json, os.path.join(OUT_DIR, "main.json"))
        else:
            save_json(items, filename)

    print("[INFO] Scraping process completed.")


if __name__ == '__main__':
    main()

