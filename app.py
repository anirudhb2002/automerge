from flask import Flask, jsonify, request
import git
import requests
import os

app = Flask(__name__)

# GitHub configuration
# Please change as required
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/branches"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Environment variable, use a .env file to store this
REPO_OWNER = "anirudhb2002"  # Replace with your Github username
REPO_NAME = "automerge"  # Replace with the repo

# Local repository path - a clone of the test repo stored in your local file
repo_path = '/Users/anirudhbhaskar/Documents/Project/automerge'
repo = git.Repo(repo_path)

# Define main branch - get from environment variable or default to 'main'
main_branch = os.getenv("MAIN_BRANCH", "main")

# Retrieves the list of branch names from the GitHub repository
def get_github_branches():
    url = GITHUB_API_URL.format(owner=REPO_OWNER, repo=REPO_NAME)
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    branches = [branch['name'] for branch in response.json()]
    return branches


# Retrieves the list of commit SHAs for a specified branch from the GitHub repository
def get_github_commits(branch):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits?sha={branch}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    commits = response.json()
    return [commit['sha'] for commit in commits]


# Merges changes from the start branch into the subsequent versions
def propagate_fix(start_branch, commit_hash):
    # Get a list of branches in the repository
    branches = get_github_branches()
    main_branch = 'main'
    conflicts = []

    try:
        # Checkout the starting branch and cherry-pick the specified commit
        repo.git.checkout(start_branch)
        repo.git.cherry_pick(commit_hash)
    except git.exc.GitCommandError as e:
        return [f"Error cherry-picking commit: {str(e)}"]

    # Determine the index of the current branch
    current_index = branches.index(start_branch)

    # Extract the feature prefix of the start branch (basically without version number)
    feature_prefix = '/'.join(start_branch.split('/')[:-1])

    for i in range(current_index + 1, len(branches)):
        target_branch = branches[i]
        
        # Ensure only branches with different version numbers are considered
        if target_branch.startswith(feature_prefix):
            repo.git.checkout(target_branch)
            try:
                repo.git.merge(start_branch)
            except git.exc.GitCommandError as e:
                conflicts.append(f"Conflict in {target_branch}: {str(e)}")
                break

    # Merge the last branch and also with Main
    repo.git.checkout(main_branch)
    try:
        repo.git.merge(branches[-1])
    except git.exc.GitCommandError as e:
        conflicts.append(f"Conflict in {main_branch}: {str(e)}")

    return conflicts


@app.route('/propagate-bug-fix', methods=['POST'])
def propagate_bug_fix():
    # Extract branch and commit hash from the request payload
    data = request.json
    branch = data.get('branch')
    commit_hash = data.get('commit')
    
    # Validate the presence of branch and commit hash
    if not branch or not commit_hash:
        return jsonify({"success": False, "error": "Branch and commit are required"}), 400
    
    # Retrieve the list of branches from GitHub
    branches = get_github_branches()
    # Line for debugging
    print(f"Branches available: {branches}")  
    
    # Check if the provided branch exists in the repository
    if branch not in branches:
        return jsonify({"success": False, "error": "Invalid branch specified"}), 400
    
    # Initialize conflicts list to collect any issues
    conflicts = []

    # Propagate the bug fix commit to subsequent branches
    for b in branches:
        if b.startswith(branch.split('/')[0]):
            # Propagate fix if the branch prefix matches
            print(f"Attempting to propagate fix to branch: {b}")
            branch_conflicts = propagate_fix(branch, commit_hash)
            conflicts.extend(branch_conflicts)
    
    # Respond with the outcome of the propagation
    if conflicts:
        return jsonify({"success": False, "conflicts": conflicts}), 400
    else:
        # Collect all branches that received the fix
        affected_branches = [branch] + [b for b in branches if b.startswith(branch.split('/')[0])]
        return jsonify({"success": True, "merged_into": affected_branches + [main_branch]}), 200



if __name__ == '__main__':
    # Initialise flask on port 5001
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

