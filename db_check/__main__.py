'''
Main db_check access point
'''
import os
import pathlib

import click

from db_check import __VERSION__ as version_string
from db_check.clustering import *
from db_check.parsers import *
from db_check.checklist import DBChecklist
from db_check.report import *


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def check_params():
    '''
    Check that if delimter is set that field is also set. 
    Check that if regex is set, delimeter and field are not
    '''
    ctx = click.get_current_context()
    opts = [ctx.params['delimiter'] is None,
            ctx.params['field'] is None,
            ctx.params['regex'] is None]
    if all(opts):
        return
    if opts[0] and opts[1] and not opts[2]:
        return
    if not opts[0] and not opts[1] and opts[2]:
        return
    click.secho(
        "ERROR: Delimiter and field must be specified OR regex OR None.", fg="red")
    ctx.exit()


@click.command("db-check", context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--delimiter", default=None, help="When parsing a category from seqid, split on this delimiter (use -1 for last element, -2 for second to last, etc.).")
@click.option("-f", "--field", default=None, help="When parsing a category from seqid using a delimiter, keep this field number (0-index).", type=int)
@click.option("-r", "--regex", default=None, help="When parsing a category from seqid extract using this regex.")
@click.option("-a", "--author", default=f"{os.getlogin()}", help="Who is running the check. (default: $USER)")
@click.option("-n", "--db_name", default=None, help="Name of the Database. (default: filename)")
@click.version_option(version=version_string, message=f"db-check v{version_string}")
@click.argument("fasta")
def run_db_check(delimiter, field, regex, author, db_name, fasta):
    '''
    Check a FASTA DB for potential issues.
    '''
    check_params()
    if db_name is None:
        db_name = pathlib.Path(fasta).stem
    clusters = cluster_db(fasta)
    tab = parse_clustering(clusters)
    if delimiter is not None and field is not None:
        tab = parse_categories(tab, delimiter=delimiter, field=field)
    elif regex is not None:
        tab = parse_categories(tab, regex=regex)
    checklist = DBChecklist(tab, author=author, db_name=db_name)
    checklist.ticks()
    generate_report(checklist)


if __name__ == "__main__":
    run_db_check()
