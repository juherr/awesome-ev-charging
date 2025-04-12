import requests
import argparse
from time import sleep
from collections import defaultdict

BASE_URL = "https://api.github.com"
MAX_PAGES = 10
TOPICS = {"ocpp", "ocpi", "emobility"}
STARRED_USERS = {"juherr"}
EXCLUDED_REPOS = {"juherr/awesome-ev-charging"}

def get_repo_data(full_name, headers):
    url = f"{BASE_URL}/repos/{full_name}"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def get_starred_repos_for_user(user, headers):
    starred = set()
    page = 1
    while True:
        url = f"{BASE_URL}/users/{user}/starred"
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"⚠️  Could not fetch starred repos for {user}: {response.status_code}")
            break
        items = response.json()
        if not items:
            break
        for item in items:
            starred.add(item["full_name"])
        if len(items) < 100:
            break
        page += 1
        if not headers:
            sleep(1)
    return starred

def get_repos_by_topic(topic, headers):
    repos = {}
    for page in range(1, MAX_PAGES + 1):
        print(f"🔍 Fetching topic '{topic}', page {page}...")
        params = {
            "q": f"topic:{topic}",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }
        response = requests.get(f"{BASE_URL}/search/repositories", headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code} for topic '{topic}'")
            break

        for item in response.json().get("items", []):
            if item["full_name"] in EXCLUDED_REPOS:
                continue

            repo_info = get_repo_data(item["full_name"], headers)
            if not repo_info:
                continue

            parent_full_name = repo_info["parent"]["full_name"] if repo_info.get("fork") and "parent" in repo_info else None

            key = item["full_name"]
            if key not in repos:
                repos[key] = {
                    "full_name": item["full_name"],
                    "html_url": item["html_url"],
                    "description": item["description"],
                    "language": item["language"],
                    "license": item["license"]["name"] if item["license"] else "N/A",
                    "stars": item["stargazers_count"],
                    "topics": [topic],
                    "is_fork": item["fork"],
                    "parent_full_name": parent_full_name,
                    "starred_by_users": set()
                }
            else:
                repos[key]["topics"].append(topic)

        if not headers:
            sleep(2)
    return repos

def merge_all_sources(topics, headers):
    all_repos = {}
    user_starred = defaultdict(set)

    for user in STARRED_USERS:
        print(f"⭐ Fetching starred repos for {user}...")
        user_starred[user] = get_starred_repos_for_user(user, headers)

    for topic in topics:
        topic_repos = get_repos_by_topic(topic, headers)
        for name, data in topic_repos.items():
            if name in EXCLUDED_REPOS:
                continue
            if name not in all_repos:
                all_repos[name] = data
            else:
                all_repos[name]["topics"] = list(set(all_repos[name]["topics"] + data["topics"]))

    for name, repo in all_repos.items():
        for user, starred_set in user_starred.items():
            if name in starred_set:
                repo["starred_by_users"].add(user)

    return all_repos

def print_summary(repos):
    print(f"\n✅ Found {len(repos)} repositories (filtered, sorted):\n")

    def sort_key(repo):
        return (
            -len(repo["starred_by_users"]),       # Most user stars first
            -len(set(repo["topics"])),            # Most topic coverage
            -repo["stars"]                        # Then GitHub stars
        )

    for repo in sorted(repos.values(), key=sort_key):
        line = f"- [{repo['full_name']}]({repo['html_url']})"
        if repo["is_fork"] and repo["parent_full_name"]:
            line += f" _(fork of [{repo['parent_full_name']}](https://github.com/{repo['parent_full_name']}))_"
        if repo["starred_by_users"]:
            users = ', '.join(sorted(repo["starred_by_users"]))
            line += f" ⭐ x{len(repo['starred_by_users'])} (starred by: {users})"
        line += f" — {repo['description'] or 'No description'}"
        line += f" — Topics: {', '.join(sorted(repo['topics']))}"
        print(line)

def main():
    parser = argparse.ArgumentParser(description="Fetch and rank GitHub repositories by topic and user stars.")
    parser.add_argument('--token', type=str, help='GitHub personal access token (optional)')
    args = parser.parse_args()

    headers = {"Authorization": f"token {args.token}"} if args.token else {}
    repos = merge_all_sources(TOPICS, headers)
    print_summary(repos)

if __name__ == "__main__":
    main()
