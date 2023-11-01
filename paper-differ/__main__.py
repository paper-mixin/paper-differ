import asyncio
import subprocess
import os
import argparse

from util import parse_git_out, run_git_diff, get_upstream_rev

PAPER_REPO_URL = "https://github.com/PaperMC/Paper"
CLONE_REPO_URL = "git@github.com:paper-mixin/paper-server-tree.git"


def configure_diff_git(repo: str):
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


def apply_patches():
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


def diff_commit(rev: str, repo: str):
    subprocess.run([
        "git",
        "reset",
        "--hard",
        rev
    ], cwd="paper-git")
    configure_diff_git(repo)
    apply_patches()

    # Commit & push

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
    parser.add_argument("--initial", type=bool, help="Initial repository initialization step."
                                                     "this should only be done once per branch.", default=False)
    args = parser.parse_args()

    if not os.path.isdir("paper-git"):
        # We likely want to clone the paper repository before doing anything else
        subprocess.run([
            "git",
            "clone",
            args.paper_repo,
            "paper-git"
        ])
    else:
        # Make sure the repository is updated
        subprocess.run([
            "git",
            "pull"
        ], cwd="paper-git")

    if args.initial:
        apply_patches()
        configure_diff_git(args.repo)

        upstream_latest = {
            "Spigot": get_upstream_rev("Spigot/Spigot-Server"),
            "Paper": get_upstream_rev("../Paper-Server")
        }

        for upstream in upstream_latest:
            rev = upstream_latest[upstream]

            subprocess.run([
                "git",
                "reset",
                "--hard",
                rev
            ], cwd="paper-git/Paper-Server")

            run_git_diff([
                "git",
                "add",
                "."
            ])

            run_git_diff([
                "git",
                "commit",
                "-m",
                f"🎯 Checkpoint: {upstream} (at {rev})"
            ])
        run_git_diff([
            "git",
            "push",
            "-u",
            "origin",
            "main",
            "--force"
        ])

    else:
        current_rev = parse_git_out(
            subprocess.check_output("git rev-parse HEAD".split(" "), cwd="paper-git"))

        diff_commit(current_rev, args.repo)


if __name__ == "__main__":
    asyncio.run(main())
