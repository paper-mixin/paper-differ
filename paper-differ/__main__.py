import asyncio
import subprocess
import os
import argparse

from util import parse_git_out, run_git_diff

PAPER_REPO_URL = "https://github.com/PaperMC/Paper"
CLONE_REPO_URL = "git@github.com:paper-mixin/paper-server-tree.git"


def diff_commit(rev: str,  repo: str):
    subprocess.run([
        "git",
        "reset",
        "--hard",
        rev
    ], cwd="paper-git")

    # old script check
    if os.path.exists("paper-git/applyPatches.sh"):
        subprocess.run([
            "./upstreamMerge.sh"
        ], cwd="paper-git")
        subprocess.run([
            "./applyPatches.sh"
        ], cwd="paper-git")
    else:
        # New paperclip script
        subprocess.run([
            "./gradlew",
            "applyServerPatches"
        ], cwd="paper-git")

    run_git_diff([
        "git",
        "init"
    ])

    # Set author
    run_git_diff([
        "git",
        "config",
        "user.name",
        "PaperMC"
    ])

    run_git_diff([
        "git",
        "config",
        "user.email",
        "admin@papermc.io"
    ])

    # Commit & push
    run_git_diff([
        "git",
        "branch",
        "-M",
        "main"
    ])

    run_git_diff([
        "git",
        "remote",
        "add",
        "origin",
        repo
    ])

    run_git_diff([
        "git",
        "add",
        "."
    ])

    run_git_diff([
        "git",
        "commit",
        "-m",
        f"Revision {rev} on PaperMC/Paper"
    ])

    run_git_diff([
        "git",
        "push",
        "-u",
        "origin",
        "main",
        "--force"
    ])


async def main():
    parser = argparse.ArgumentParser(description="Diffs the paper repository and uploads it to a private repository.")
    parser.add_argument("--paper_repo", type=str, help="The URL to the paper repository", default=PAPER_REPO_URL)
    parser.add_argument("--repo", type=str, help="The URL to the clone repository", default=CLONE_REPO_URL)
    parser.add_argument("--backlog", type=bool, help="If we should push the last 10 commits on the paper repository, "
                                                     "this should only be done once per tree.", default=False)
    args = parser.parse_args()

    if not os.path.isdir("paper-git"):
        # We likely want to clone the paper repository before doing anything else
        subprocess.run([
            "git",
            "clone",
            args.paper_repo,
            "paper-git"
        ])

    if args.backlog:
        # We don't want to go *too* far back, I think a big blob 10 commits away is good
        revisions = parse_git_out(subprocess.check_output([
            "git",
            "rev-list",
            "--reverse",
            "HEAD~10..HEAD"
        ], cwd="paper-git")).split("\n")

        for revision in revisions:
            diff_commit(revision, args.repo)
    else:
        current_rev = parse_git_out(
            subprocess.check_output("git rev-parse HEAD".split(" "), cwd="paper-git"))

        diff_commit(current_rev, args.repo)

if __name__ == "__main__":
    asyncio.run(main())
