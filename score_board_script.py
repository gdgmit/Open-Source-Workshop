import requests

GITHUB_TOKEN = "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" 
ORG_NAME = "gdgmit"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Label scores
LABEL_SCORES = {
    "l1": 10,
    "l2": 25,
    "l3": 45,
}

OUTPUT_FILE = "leaderboard.txt"  # File to save the leaderboard as plain text
MARKDOWN_FILE = "leaderboard.md"  # File to save the leaderboard as Markdown

def fetch_org_repos(org_name):
    """Fetch all repositories for the given organization."""
    url = f"https://api.github.com/orgs/{org_name}/repos"
    params = {"per_page": 100}
    repos = []

    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}, {response.text}")
            break
        
        repos.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Get the next page URL
    
    return repos

def fetch_prs_with_labels(repo_name):
    """Fetch pull requests for a specific repository."""
    url = f"https://api.github.com/repos/{ORG_NAME}/{repo_name}/pulls"
    params = {"state": "all", "per_page": 100}
    prs = []

    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"Error fetching PRs for {repo_name}: {response.status_code}, {response.text}")
            break
        
        prs.extend(response.json())
        url = response.links.get("next", {}).get("url")  # Get the next page URL
    
    return prs

def calculate_scores_for_org():
    """Calculate scores and list PRs for all repositories in the organization."""
    repos = fetch_org_repos(ORG_NAME)
    if not repos:
        print("No repositories found.")
        return

    user_data = {}

    for repo in repos:
        repo_name = repo["name"]
        print(f"Processing repository: {repo_name}...")
        prs = fetch_prs_with_labels(repo_name)

        for pr in prs:
            labels = [label["name"] for label in pr.get("labels", [])]
            if "gdg-mit-os" in labels:
                user = pr["user"]["login"]
                pr_url = pr["html_url"]
                score = sum(LABEL_SCORES.get(label, 0) for label in labels if label in LABEL_SCORES)

                # Initialize user data if not already present
                if user not in user_data:
                    user_data[user] = {"score": 0, "pr_links": []}

                # Update user score and add PR link
                user_data[user]["score"] += score
                user_data[user]["pr_links"].append(pr_url)

    return user_data

def generate_leaderboard(user_data):
    """Generate leaderboard with ranks."""
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["score"], reverse=True)
    leaderboard = []
    rank = 1
    previous_score = None
    skipped_ranks = 0

    for index, (user, data) in enumerate(sorted_users, start=1):
        if previous_score is None or data["score"] < previous_score:
            rank = index + skipped_ranks

        leaderboard.append({
            "rank": rank,
            "user": user,
            "score": data["score"],
            "pr_links": data["pr_links"],
        })

        # Adjust skipped ranks for ties
        if previous_score == data["score"]:
            skipped_ranks += 1
        else:
            skipped_ranks = 0

        previous_score = data["score"]

    return leaderboard

def save_leaderboard_to_file(leaderboard):
    """Save leaderboard to a text file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("Leaderboard:\n\n")
        for entry in leaderboard:
            file.write(f"Rank: {entry['rank']}\n")
            file.write(f"User: {entry['user']}\n")
            file.write(f"Total Score: {entry['score']} points\n")
            file.write(f"PR Links: {entry['pr_links']}\n\n")

def save_leaderboard_to_markdown(leaderboard):
    """Save leaderboard to a Markdown file in a tabular format."""
    with open(MARKDOWN_FILE, "w", encoding="utf-8") as file:
        file.write("# GDG-MIT-Open-Source-Connect-Workshop :octocat:\n\n")
        file.write("![GDG Community Banner](GDG-Community-Page.jpg)\n\n")
        file.write("---\n\n")
        file.write("Hello contributors! Welcome to the [Google Developer Group on Campus MIT’s](https://gdg.community.dev/gdg-on-campus-madras-institute-of-technology-chennai-india/) **\"Introduction to GitHub & Open Source Workshop**.\n\n")
        file.write("We hope you're all doing great! 🚀 \n\n")
        file.write("Before we dive in, make sure to review how Open Source Contribution works by checking our guidelines here: [GUIDELINES.md](GUIDELINES.md).\n\n")
        file.write("---\n\n")
        file.write("## **🏆 Leaderboard**\n\n")
        file.write("Here’s the leaderboard recognizing your efforts and contributions during the workshop. Keep up the amazing work and let’s build something great together!\n\n")
        file.write("| 🥇 Rank | 👤 User | 🌟 Total Score | 🔗 PR Links |\n")
        file.write("|--------|--------|----------------|-------------|\n")
        for entry in leaderboard:
            pr_links = "<br>".join([f"[PR Link]({link})" for link in entry["pr_links"]])
            file.write(f"| {entry['rank']} | {entry['user']} | {entry['score']} points | {pr_links} |\n")
        file.write("\n---\n")
        file.write("## How the Scoring Works\n\n")
        file.write("Each PR is assigned a label, and corresponding points are awarded:\n")
        file.write("- **`l1`**: 10 points\n")
        file.write("- **`l2`**: 25 points\n")
        file.write("- **`l3`**: 45 points\n")
        file.write("\nMake sure your PRs are meaningful and follow the workshop's contribution guidelines.\n\n")
        file.write("For more details, please refer to:\n")
        file.write("- [CONTRIBUTING.md](CONTRIBUTING.md) - Guidelines for meaningful contributions.\n")
        file.write("- [GUIDELINES.md](GUIDELINES.md) - Detailed instructions for open-source participation.\n\n")
        file.write("---\n\n")
        file.write("## **🌟 Keep Contributing!**\n\n")
        file.write("This leaderboard will be updated periodically as new contributions are reviewed and added. Continue making meaningful contributions, and let’s make this community shine!\n\n")
        file.write("⚡ Remember: Quality >>>>> Quantity. Avoid spammy PRs, and let your work stand out! 🚀\n\n")
        file.write("---\n\n")
        file.write("Happy Contributing! 🎉\n")

def main():
    user_data = calculate_scores_for_org()
    if not user_data:
        print("No scores calculated.")
        return

    leaderboard = generate_leaderboard(user_data)
    save_leaderboard_to_file(leaderboard)
    save_leaderboard_to_markdown(leaderboard)

    print("\nLeaderboard saved to leaderboard.txt and leaderboard.md")
    for entry in leaderboard:
        print(f"Rank: {entry['rank']}, User: {entry['user']}, Score: {entry['score']} points, PR Links: {entry['pr_links']}")

if __name__ == "__main__":
    main()
