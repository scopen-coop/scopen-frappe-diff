import click
import frappe

from frappe.commands import pass_context
from .frappe_diff_custom import generate_diff


@click.command('frappe-diff-custom', help='Test de command')
@click.argument("app")
@click.option("--source-branch", type=str, help="Source branch name")
@click.option("--source-commit", type=str, help="Source commit name, default : local files")
@click.option("--target-branch", type=str, help="Target ranch name")
@click.option("--target-commit", type=str, default="HEAD~1", help="Target commit name, default HEAD~1")
def frappe_diff_custom(app: str,
                       source_branch: str | None = None,
                       source_commit: str | None = None,
                       target_branch: str | None = None,
                       target_commit: str | None = None):
    generate_diff(app, source_branch, source_commit, target_branch, target_commit)


commands = [
    frappe_diff_custom,
]
