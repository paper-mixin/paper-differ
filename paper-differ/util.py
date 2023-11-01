import subprocess


def parse_git_out(out: bytes) -> str:
    return out.decode("utf-8").removesuffix("\n")


def run_git_diff(args):
    """Run git command in diff git tree"""

    subprocess.run(args, cwd="paper-git/Paper-Server", env={
        "GIT_DIR": "../.diff-git-tree",
        "GIT_WORK_TREE": "."
    })
