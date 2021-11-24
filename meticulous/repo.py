from git import Repo
import os.path
REPO = Repo("", search_parent_directories=True)
COMMIT = REPO.commit()

DIFFS = []

TRACKED_EXTENSIONS = set()
for item in COMMIT.tree.traverse():
    if item.type == "blob":
        name, ext = os.path.splitext(item.name)
        TRACKED_EXTENSIONS.add(ext)

for diff in REPO.head.commit.diff(None, create_patch=True, unified=0):
    if diff.renamed_file:
        DIFFS.append({"file": diff.a_path, "renamed": True})
        continue
    if diff.a_path is not None:
        DIFFS.append({"file": diff.a_path, "patch": diff.diff.decode()})
for f in REPO.untracked_files:
    if os.path.splitext(f)[1] in TRACKED_EXTENSIONS:
        DIFFS.append({"file": f, "patch": open(f,"r").read()})
