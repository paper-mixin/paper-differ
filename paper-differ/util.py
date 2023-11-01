import subprocess


def get_upstream_rev(upstream_name: str) -> str:
    return parse_git_out(subprocess.check_output([
        "git",
        "rev-parse",
        "head"
    ], cwd=f"paper-git/work/{upstream_name}"))


def parse_git_out(out: bytes) -> str:
    return out.decode("utf-8").removesuffix("\n")


def run_git_diff(args):
    """Run git command in the diff's git tree"""

    subprocess.run(args, cwd="paper-git/Paper-Server", env={
        "GIT_DIR": "../.diff-git-tree",
        "GIT_WORK_TREE": "."
    })
