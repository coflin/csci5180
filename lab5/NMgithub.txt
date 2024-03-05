import os
from git import Repo
import subprocess

def get_or_create_repo():
    # Get the current working directory
    cwd = os.getcwd()

    try:
        # Initialize the repository object
        repo = Repo(cwd)
        return repo
    except:
        # If initialization fails, create a new repository
        repo = Repo.init(cwd)
        return repo

def push_latest_modified_files(file_extensions):
    repo = get_or_create_repo()

    # Fetch the latest changes from the remote repository
    origin = repo.remote(name='origin')
    origin.fetch()

    # Get the current branch name
    branch_name = repo.active_branch.name

    # Compare local and remote branches to find modified files
    changed_files = [item.a_path for item in repo.index.diff(None) if item.a_path.endswith(file_extensions)]

    # Get untracked files in the working directory
    untracked_files = repo.untracked_files

    # Filter untracked files based on extensions
    new_files = [file for file in untracked_files if file.endswith(file_extensions)]

    # Get deleted files in the working directory
    deleted_files = [item.a_path for item in repo.index.diff(None) if item.deleted_file]

    # If there are modified or new files, stage and commit them
    if changed_files or new_files or deleted_files:

        # Remove deleted files from the index
        if deleted_files:
            print(F"Removing these deleted files: {deleted_files}")
            repo.index.remove(deleted_files)

        # Stage all modified files
        if changed_files:
            for file in changed_files:
                if file not in deleted_files:
                    print(F"Staging these modified files: {changed_files}")
                    repo.index.add(changed_files)

        # Stage all new files
        if new_files:
            print(F"Staging these new files: {new_files}")
            repo.index.add(new_files)

        print("Committing the changes..")
        # Commit the changes
        repo.index.commit("Committing modified and new files in the working directory")

        print("Pushing to the remote repository")
        # Push the changes to the remote repository
        origin.push(branch_name)
        print("Pushed to the repository.")

    else:
        print("Up to date with the remote repository. Nothing to add/commit.")

push_latest_modified_files(('.txt','.jpg'))