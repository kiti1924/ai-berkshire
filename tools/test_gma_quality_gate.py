#!/usr/bin/env python3
"""
Quality Gate script for Global Market Adaptation (GMA) specifications and task tracking.
"""

import json
import os
import sys
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(REPO_ROOT, "docs", "global-market-adaptation")
TASKS_DIR = os.path.join(REPO_ROOT, "tasks", "global_market_adaptation")

def test_json_parse():
    queue_json_path = os.path.join(TASKS_DIR, "queue.json")
    audit_json_path = os.path.join(TASKS_DIR, "audit.json")
    
    with open(queue_json_path, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
        
    with open(audit_json_path, "r", encoding="utf-8") as f:
        audit_data = json.load(f)
        
    return queue_data, audit_data

def test_queue_dag(queue_data):
    goals = {g["id"]: g for g in queue_data["goals"]}
    assert len(goals) == 14, f"Expected 14 goals (0-13), got {len(goals)}"
    
    # Check cycle using DFS
    visited = {}
    def dfs(gid, path):
        if visited.get(gid) == 1:
            raise ValueError(f"Cycle detected in dependencies: {path} -> {gid}")
        if visited.get(gid) == 2:
            return
        visited[gid] = 1
        for dep in goals[gid]["dependencies"]:
            dfs(dep, path + [gid])
        visited[gid] = 2

    for gid in goals:
        dfs(gid, [])
    print("DAG dependency check passed cleanly.")

def test_queue_md_consistency(queue_data):
    queue_md_path = os.path.join(TASKS_DIR, "queue.md")
    with open(queue_md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    for g in queue_data["goals"]:
        assert f"`{g['name']}`" in content or g['name'] in content, f"Goal name {g['name']} not in queue.md"
        assert g['title'] in content, f"Goal title {g['title']} not in queue.md"
    print("queue.json vs queue.md consistency check passed.")

def test_audit_mapping(audit_data, queue_data):
    reqs = audit_data["requirements_mapping"]
    assert len(reqs) == 31, f"Expected 31 requirement mappings, got {len(reqs)}"
    valid_goal_ids = {g["id"] for g in queue_data["goals"]}
    for r in reqs:
        assert r["goal_id"] in valid_goal_ids, f"Invalid goal_id {r['goal_id']} in requirement {r['req_id']}"
    print("Audit mapping check passed (all 31 requirements mapped).")

def test_terminology_gate():
    prohibited = ["護城河"]
    files_to_check = []
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                files_to_check.append(os.path.join(root, file))
    for root, dirs, files in os.walk(TASKS_DIR):
        for file in files:
            if file.endswith(".md"):
                files_to_check.append(os.path.join(root, file))
                
    violations = []
    for fpath in files_to_check:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines, 1):
                if "新規追加・使用してはならない" in line or "新規混入を検出" in line or "を標準用語とする" in line or "新規追加しない" in line:
                    continue
                for p in prohibited:
                    if p in line:
                        violations.append((fpath, idx, p))
                        
    if violations:
        for v in violations:
            print(f"Terminology Violation in {v[0]}:{v[1]} - prohibited term '{v[2]}' found.")
        sys.exit(1)
    print("Terminology gate passed (no prohibited terms found).")


def main():
    print("Running GMA Quality Gate Tests...")
    queue_data, audit_data = test_json_parse()
    test_queue_dag(queue_data)
    test_queue_md_consistency(queue_data)
    test_audit_mapping(audit_data, queue_data)
    test_terminology_gate()
    print("All Quality Gate Tests Passed Successfully!")

if __name__ == "__main__":
    main()
