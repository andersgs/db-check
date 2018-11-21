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
from db_check.messages import error, info


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.pass_context
def check_params(ctx):
    '''
    Check that if delimter is set that field is also set. 
    Check that if regex is set, delimeter and field are not
    '''
    opts = [ctx.params.get('delimiter', None) is None,
            ctx.params.get('field', None) is None,
            ctx.params.get('regex', None) is None]
    if all(opts):
        return
    if opts[0] and opts[1] and not opts[2]:
        return
    if not opts[0] and not opts[1] and opts[2]:
        return
    error(
        "ERROR: Delimiter and field must be specified OR regex OR None.")
    ctx.exit()


def run_example(ctx, param, value):
    '''
    Run example data
    '''
    if not value:
        return
    fasta = pathlib.Path(__file__).parent / "examples" / "example_db.fasta"
    ctx.invoke(run_db_check, delimiter=None, field=None,
               regex=".*~~(.*)", threads=1, author="Example", db_name="Example DB",
               prefix="example", keep_files=False, fasta=fasta)
    ctx.exit()


@click.command("db-check", context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--delimiter", default=None, help="When parsing a category from seqid, split on this delimiter (use -1 for last element, -2 for second to last, etc.).")
@click.option("-f", "--field", default=None, help="When parsing a category from seqid using a delimiter, keep this field number (0-index).", type=int)
@click.option("-r", "--regex", default=None, help="When parsing a category from seqid extract using this regex.")
@click.option("-a", "--author", default=f"{os.getlogin()}", help="Who is running the check. (default: $USER)")
@click.option("-n", "--db_name", default=None, help="Name of the Database. (default: filename)")
@click.option("-t", "--threads", default=1, help="How many threads to give CD-HIT (default: 1)")
@click.option("-p", "--prefix", default="cdhit", help="Prefix of output files from CD-HIT (default: cdhit)")
@click.option("-k", "--keep_files", help="Whether to keep CD-HIT output files (default: False)", is_flag=True)
@click.option("--example", help="Run an example set", is_flag=True, is_eager=True, callback=run_example)
@click.version_option(version=version_string, message=f"db-check v{version_string}")
@click.argument("fasta")
def run_db_check(delimiter, field, regex, author, db_name, threads, prefix, example, keep_files, fasta):
    '''
    Check a FASTA DB for potential issues.
    '''
    info("Welcome do db-check.")
    info("Running some routine checks...")
    check_params()
    check_dependencies()
    if db_name is None:
        db_name = pathlib.Path(fasta).stem
    info("Clustering your DB...")
    [clusters, workdir] = cluster_db(fasta, prefix, threads=threads)
    info("Parsing the results...")
    tab = parse_clustering(clusters)
    if delimiter is not None and field is not None:
        tab = parse_categories(tab, delimiter=delimiter, field=field)
    elif regex is not None:
        tab = parse_categories(tab, regex=regex)
    info("Going over all the checks...")
    checklist = DBChecklist(tab, author=author, db_name=db_name)
    checklist.ticks()
    info("Printing your report...")
    generate_report(checklist)
    if keep_files:
        info("You decided to keep the files... Here you go...")
        wd = pathlib.Path(workdir.name)
        for f in wd.glob(prefix+"*"):
            info(f"Keeping {f.name}")
            shutil.copyfile(f.absolute(), f.name)
    workdir.cleanup()
    info("Happy publishing!")


if __name__ == "__main__":
    run_db_check()
