import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "gitflow_metro"))


from gitflow_metro.parser import parse_repository
from gitflow_metro.graph import build_graph

repo = parse_repository(r"D:\DESI GERMANS\UNIVERSITY APPLICATION\University of Stuttgart\Studies\Lab\GitFlowMetro\TestRepo")

repo = build_graph(repo)

for commit in repo.commits:

    print("=" * 50)

    print("Hash:", commit.hash[:7])

    print("Parents:", [p[:7] for p in commit.parents])

    print("Children:", [c[:7] for c in commit.children])

    print("Merge:", commit.is_merge)