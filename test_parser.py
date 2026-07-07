import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "gitflow_metro"))


from gitflow_metro.parser import parse_repository


REPOSITORY_PATH = r"D:\DESI GERMANS\UNIVERSITY APPLICATION\University of Stuttgart\Studies\Lab\GitFlowMetro\TestRepo"

repo = parse_repository(REPOSITORY_PATH)

print("=" * 60)
print("Repository Parsed Successfully")
print("=" * 60)

print(f"\nTotal commits: {len(repo.commits)}")

for i, commit in enumerate(repo.commits, start=1):

    print("\n" + "-" * 60)

    print(f"Commit {i}")

    print(f"Hash    : {commit.hash}")

    print(f"Parents : {commit.parents}")

    print(f"Author  : {commit.author}")

    print(f"Date    : {commit.date}")

    print(f"Message : {commit.message}")