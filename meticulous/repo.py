from git import Repo
REPO = Repo("", search_parent_directories=True)
COMMIT = REPO.commit()