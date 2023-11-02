import subprocess
import tempfile
import shutil


def pull_git_history(clone_repo: str):
    temp_repo_path = tempfile.mkdtemp()
    subprocess.run([
        "git",
        "clone",
        clone_repo,
        temp_repo_path
    ])

    shutil.copytree(f"{temp_repo_path}/.git", ".paper-git")
    shutil.rmtree(temp_repo_path)


def get_upstream_rev(upstream_name: str) -> str:
    """Get upstream revisions"""
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
        "GIT_DIR": "../../.paper-git",
        "GIT_WORK_TREE": "."
    })


def run_git(args: list):
    """Run git command in the Paper-Server git tree"""

    subprocess.run(args, cwd="paper-git/Paper-Server")
