from github import Github
import requests
import re
import sys

# --- CONFIG ---
# You can create a personal GitHub token for higher rate limits
GITHUB_TOKEN = ""  # optional
g = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()

# --- FUNCTIONS ---
def get_repo_info(url):
    """
    Extract owner and repo name from GitHub URL
    """
    match = re.match(r"https?://github.com/([\w-]+)/([\w.-]+)", url)
    if not match:
        return None, None
    return match.group(1), match.group(2)

def analyze_repo(owner, repo_name):
    repo = g.get_repo(f"{owner}/{repo_name}")

    # Basic repo info
    commits = repo.get_commits().totalCount
    files = sum(1 for f in repo.get_contents("") if f.type == "file")
    folders = sum(1 for f in repo.get_contents("") if f.type == "dir")
    has_readme = any(f.name.lower() == "readme.md" for f in repo.get_contents(""))
    main_language = repo.language
    forks = repo.forks_count
    stars = repo.stargazers_count

    # Simple scoring logic
    score = 0
    roadmap = []

    # File count
    if files > 3:
        score += 20
    else:
        roadmap.append("Add more source files for a complete project.")

    # Folder structure
    if folders > 0:
        score += 15
    else:
        roadmap.append("Organize your code into folders.")

    # Commits
    if commits > 5:
        score += 20
    else:
        roadmap.append("Commit changes more frequently for better tracking.")

    # README
    if has_readme:
        score += 15
    else:
        roadmap.append("Add a README.md with project overview and instructions.")

    # Main language
    if main_language:
        score += 15
    else:
        roadmap.append("Specify main programming language in repo.")

    # Stars and forks bonus
    score += min(stars // 50, 15)
    score += min(forks // 100, 15)
    score = min(score, 100)

    # Summary generation
    summary = []
    summary.append(f"Documentation is {'present' if has_readme else 'missing'}.")
    summary.append(f"Project has {files} file(s) and {folders} folder(s).")
    summary.append(f"Total commits: {commits}.")
    summary.append(f"Main programming language: {main_language if main_language else 'Not detected'}.")

    summary_text = " ".join(summary)

    # Output JSON-like dict
    result = {
        "repository": f"{owner}/{repo_name}",
        "score": score,
        "summary": summary_text,
        "roadmap": roadmap,
        "commit_count": commits,
        "file_count": files,
        "folder_count": folders,
        "has_readme": has_readme,
        "main_language": main_language,
        "stars": stars,
        "forks": forks
    }

    return result

# --- MAIN ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gitgrade.py <GitHub Repo URL>")
        sys.exit(1)

    url = sys.argv[1]
    owner, repo_name = get_repo_info(url)
    if not owner or not repo_name:
        print("Invalid GitHub URL")
        sys.exit(1)

    analysis = analyze_repo(owner, repo_name)
    print(analysis)
