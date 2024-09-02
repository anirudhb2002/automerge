# Automated Bug Fix Propagation

This project includes a tool for automatically propagating bug fixes across different branches. The goal is to ensure that bug fixes from one branch are merged into subsequent branches and eventually into the main branch.


## Running the Tool

1. **Set Up the Environment**:
   - Ensure you have a Python virtual environment set up.
   - Install the necessary Python packages using `pip`.

2. **Configure the GitHub Repository**:
   - Make sure to set up the correct GitHub repository and branches.
   - Update the `GITHUB_API_URL`, `GITHUB_TOKEN`, `REPO_OWNER`, and `REPO_NAME` in the `app.py` file.

3. **Start the Flask Application**:
   - Run the Flask application with the command:
     ```bash
     python app.py
     ```

4. **Trigger Bug Fix Propagation**:
   - Send a POST request to the endpoint `/propagate-bug-fix` with JSON data containing the branch name and commit hash:
     ```json
     {
       "branch": "dev/v1",
       "commit": "SHA_OF_THE_BUG_FIX_COMMIT"
     }
     ```

## Handling Cherry-Pick Conflicts

If you encounter conflicts during the cherry-pick operation, follow these steps:

1. **Check the Status**:
   ```bash
   git status
   ```

2. **Resolve Conflicts**:
   - **For Modified Files**: If a file has been modified and you want to keep the changes, use:
     ```bash
     git add path/to/file
     ```
     If you need to discard the changes, use:
     ```bash
     git restore path/to/file
     ```
   - **For Deleted Files**: If a file was deleted but should be restored, use:
     ```bash
     git restore --source=COMMIT_HASH -- path/to/deleted_file
     ```

3. **Stage Resolved Changes**:
   After resolving the conflicts, stage the changes:
   ```bash
   git add path/to/file
   ```

4. **Continue Cherry-Pick**:
   After resolving conflicts and staging the necessary changes, proceed with the cherry-pick operation:
   ```bash
   git cherry-pick --continue
   ```

   This command will apply the changes from the specified commit onto the current branch.

5. **Push Changes**:
   Once the cherry-pick operation is complete and conflicts are resolved, push the updated branch to the remote repository:
   ```bash
   git push origin branch_name
   ```

   Replace `branch_name` with the name of the branch you are working on.

   ## Additional Notes

- **Ignoring System Files**: System files like `.DS_Store` (macOS) should be excluded from version control. Add these files to your `.gitignore` to prevent them from being tracked.



## Contact

For issues or questions, please contact me via email (anirudhb2002@gmail.com). Thanks and enjoy!

