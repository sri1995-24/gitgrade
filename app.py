from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["GET"])
def analyze_repo():
    repo_url = request.args.get("url")
    if not repo_url:
        return jsonify({"error": "GitHub URL is required"}), 400

    parts = repo_url.strip("/").split("/")
    if len(parts) < 2:
        return jsonify({"error": "Invalid GitHub URL"}), 400

    owner = parts[-2]
    repo = parts[-1]

    # Fetch repo details
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    if response.status_code != 200:
        return jsonify({"error": "Repository not found"}), 404
    data = response.json()

    # README check
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    has_readme = requests.get(readme_url).status_code == 200

    # File & folder count
    contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    file_count = folder_count = 0
    contents = requests.get(contents_url).json()
    for item in contents:
        if item["type"] == "file":
            file_count += 1
        elif item["type"] == "dir":
            folder_count += 1

    # Commit count
    commits = requests.get(f"https://api.github.com/repos/{owner}/{repo}/commits").json()
    commit_count = len(commits) if isinstance(commits, list) else 0

    # Score logic
    score = 0
    roadmap = []
    if has_readme: score += 15
    else: roadmap.append("Add a README.md with project overview and instructions.")
    if file_count > 3: score += 20
    else: roadmap.append("Add more source files for a complete project.")
    if folder_count > 0: score += 15
    else: roadmap.append("Organize your code into folders.")
    if commit_count > 5: score += 20
    else: roadmap.append("Commit changes more frequently for better tracking.")
    if data.get("language"): score += 15
    else: roadmap.append("Specify main programming language in repo.")
    score += min(data.get("stargazers_count",0)//50, 15)
    score += min(data.get("forks_count",0)//100, 15)
    score = min(score, 100)

    summary = f"Documentation is {'present' if has_readme else 'missing'}. Project has {file_count} file(s) and {folder_count} folder(s). Total commits: {commit_count}. Main programming language: {data.get('language', 'Not detected')}."

    return jsonify({
        "repository": data.get("full_name"),
        "score": score,
        "summary": summary,
        "roadmap": roadmap,
        "commit_count": commit_count,
        "file_count": file_count,
        "folder_count": folder_count,
        "has_readme": has_readme,
        "main_language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count")
    })

if __name__ == "__main__":
    app.run(debug=True)






