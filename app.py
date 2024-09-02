from flask import Flask, jsonify, request
import git
import requests
import os

app = Flask(__name__)

# GitHub configuration
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/branches"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Ensure this is set in your environment
REPO_OWNER = "anirudhb2002"  # Replace with your actual GitHub username
REPO_NAME = "automerge"  # Replace with your actual repository name

# Local repository path
repo_path = '/Users/anirudhbhaskar/Documents/Project/automerge'
repo = git.Repo(repo_path)

main_branch = 'main'  # Define main branch

def get_github_branches():
    url = GITHUB_API_URL.format(owner=REPO_OWNER, repo=REPO_NAME)
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    branches = [branch['name'] for branch in response.json()]
    return branches

def get_github_commits(branch):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={branch}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    commits = response.json()
    return [commit['sha'] for commit in commits]

def propagate_fix(start_branch, commit_hash):
    branches = get_github_branches()
    main_branch = 'main'
    conflicts = []

    try:
        repo.git.checkout(start_branch)
        repo.git.cherry_pick(commit_hash)
    except git.exc.GitCommandError as e:
        return [f"Error cherry-picking commit: {str(e)}"]

    current_index = branches.index(start_branch)

    for i in range(current_index + 1, len(branches)):
        target_branch = branches[i]
        repo.git.checkout(target_branch)
        try:
            repo.git.merge(start_branch)
        except git.exc.GitCommandError as e:
            conflicts.append(f"Conflict in {target_branch}: {str(e)}")
            break

    repo.git.checkout(main_branch)
    try:
        repo.git.merge(branches[-1])
    except git.exc.GitCommandError as e:
        conflicts.append(f"Conflict in {main_branch}: {str(e)}")

    return conflicts


@app.route('/propagate-bug-fix', methods=['POST'])
def propagate_bug_fix():
    data = request.json
    branch = data.get('branch')
    commit_hash = data.get('commit')
    
    if not branch or not commit_hash:
        return jsonify({"success": False, "error": "Branch and commit are required"}), 400
    
    branches = get_github_branches()
    print(f"Branches available: {branches}")  # Debug line
    
    if branch not in branches:
        return jsonify({"success": False, "error": "Invalid branch specified"}), 400
    
    conflicts = propagate_fix(branch, commit_hash)
    
    if conflicts:
        return jsonify({"success": False, "conflicts": conflicts}), 400
    else:
        return jsonify({"success": True, "merged_into": branches + [main_branch]}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
