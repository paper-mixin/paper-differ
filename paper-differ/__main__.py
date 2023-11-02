import asyncio
import subprocess
import os
import argparse

from util import parse_git_out, run_git_diff, get_upstream_rev, pull_git_history, run_git

PAPER_REPO_URL = "https://github.com/PaperMC/Paper"

CLONE_REPO_URL = "https://github.com/paper-mixin/paper-server-tree.git"


def configure_diff_git(repo: str, pull: bool = True):
    if not os.path.isdir(".paper-git") and pull:
        pull_git_history(repo)

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
    apply_patches()
    configure_diff_git(repo)

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
    parser.add_argument("--paper_repo", type=str, help="The URL for the paper repository", default=PAPER_REPO_URL)
    parser.add_argument("--repo", type=str, help="The URL for the clone repository", default=CLONE_REPO_URL)
    parser.add_argument("--initial", type=bool, help="Repository initialization step."
                                                     "This should only be done once per branch.", default=False)
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
        configure_diff_git(args.repo, pull=False)
        run_git(["git", "checkout", "tags/base"])

        upstream_latest = {
            "Bukkit": get_upstream_rev("CraftBukkit"),
            "Spigot": get_upstream_rev("Spigot/Spigot-Server")
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

        run_git(["git", "checkout", "master"])

        run_git_diff(["git", "add", "."])
        run_git_diff([
            "git",
            "commit",
            "-m",
            f"🎯 Checkpoint: Paper"
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
