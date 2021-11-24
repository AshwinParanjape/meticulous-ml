from git import Repo
REPO = Repo("", search_parent_directories=True)
COMMIT = REPO.commit()

DIFFS = []

for diff in REPO.head.commit.diff(None, create_patch=True, unified=0):
    if diff.renamed_file:
        DIFFS.append({"file":diff.a_path, "renamed":True})
        continue
    if diff.a_path is not None:
        if diff.a_path.endswith(".py"):
            DIFFS.append({"file":diff.a_path, "patch":diff.diff.decode()})
for f in REPO.untracked_files:
    if f.endswith(".py"):
        DIFFS.append({"file": f, "patch": open(f,"r").read()})
