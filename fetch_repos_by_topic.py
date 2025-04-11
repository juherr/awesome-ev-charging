import requests
from time import sleep
import argparse

# GitHub API base
BASE_URL = "https://api.github.com/search/repositories"

# Topics to fetch
TOPICS = ["ocpp", "ocpi", "emobility"]

# Max pages per topic (100 repos per page max)
MAX_PAGES = 2

def get_repos_by_topic(topic, headers):
    """Fetch repositories associated with a specific topic from GitHub."""
    repos = {}
    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching topic '{topic}', page {page}...")
        params = {
            "q": f"topic:{topic}",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code} while fetching topic '{topic}'")
            break

        data = response.json()
        for item in data.get("items", []):
            repos[item["full_name"]] = {
                "full_name": item["full_name"],
                "html_url": item["html_url"],
                "description": item["description"],
                "language": item["language"],
                "license": item["license"]["name"] if item["license"] else "N/A",
                "stars": item["stargazers_count"],
                "topics": [topic]
            }

        if not headers:
            sleep(2)  # Wait to avoid rate limiting
    return repos

def merge_topics(topics, headers):
    """Merge repositories from multiple topics, avoiding duplicates."""
    all_repos = {}
    for topic in topics:
        topic_repos = get_repos_by_topic(topic, headers)
        for name, repo_data in topic_repos.items():
            if name in all_repos:
                all_repos[name]["topics"].append(topic)
            else:
                all_repos[name] = repo_data
    return all_repos

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub repositories by topic.")
    parser.add_argument('--token', type=str, help='GitHub personal access token (optional)')
    args = parser.parse_args()

    headers = {"Authorization": f"token {args.token}"} if args.token else {}

    repos = merge_topics(TOPICS, headers)
    print(f"\n✅ Found {len(repos)} unique repositories:\n")

    for repo in sorted(repos.values(), key=lambda r: -r["stars"]):
        print(f"- [{repo['full_name']}]({repo['html_url']}) | ⭐ {repo['stars']} | Topics: {', '.join(repo['topics'])}")

if __name__ == "__main__":
    main()
