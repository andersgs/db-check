'''
Define different report sections and how to print them.
'''

import datetime as dt
from tabulate import tabulate
from markdown_strings import *

from db_check import __VERSION__ as version_string

SEP = horizontal_rule()
TABLEFMT = 'pipe'


def preamble(obj):
    '''
    Print some preamble data
    '''
    today = dt.date.today().strftime("%Y-%m-%d")
    title = header(f"db-check Report {obj.db_name}", 1)
    subtitle = italics(f"By {obj.author} on {today}")
    print(title, subtitle, SEP, sep='\n\n')


def summary(obj):
    '''
    Print the summary header component.
    '''
    title = header("Summary", 2)
    subtitle1 = header("Possible issues.", 3)
    if len(obj.issues) == 0:
        issues = bold("Congratulations! No issues were found.")
    else:
        issues = unordered_list(obj.issues)
    subtitle2 = header("Breakdown", 3)
    total_entries = f"- {bold('Total entries:')} {obj.total_entries}"
    total_clusters = f"- {bold('Total clusters:')} {obj.total_clusters}"
    n_unique_seq = f"- {bold('Unique sequence IDs:')} {obj.n_unique_sequences}"

    print(title,
          subtitle1,
          issues,
          subtitle2,
          total_entries,
          total_clusters,
          n_unique_seq,
          SEP, sep='\n\n')


def clusters_summary(obj):
    '''
    Given a DBChecklist object, print out some cluster summary data.
    '''
    tab = obj.cluster_size_dist
    col_header = tab.columns.values
    title = header("Cluster size distribution", 2)
    tab_cap = "Table: Distribution of cluster sizes (i.e., number of sequences)."
    tab_body = tabulate(tab,
                        showindex=False, tablefmt=TABLEFMT, headers=col_header)
    print(title,
          tab_cap,
          tab_body,
          SEP,
          sep="\n\n")
    if tab['max'].values[0] > 1:
        cluster_report(obj)
    else:
        msg = bold(
            "Congratulations! There were no clusters with more than one sequence.")
        print(msg, sep="\n")


def duplicate_report(obj):
    '''
    Print a duplicate report
    '''
    title = header("Summary of duplicated IDs", 2)
    tab = obj.df
    ix = tab.duplicated('seqid', keep=False)
    if sum(ix) == 0:
        msg = bold("Congratulations! No duplicated IDs found.")
        return
    print(title, sep="\n")
    g = tab[ix].groupby("seqid")
    for h in g.groups:
        subtitle = header(f"Duplicate ID {h}", 3)
        tab_cap = f"Table: Sequences with ID {h}"
        h = g.get_group(h)
        tab_body = tabulate(h, showindex=False,
                            headers=h.columns.values, tablefmt=TABLEFMT)
        print(subtitle,
              tab_cap,
              tab_body,
              "",
              sep="\n\n")
    print(SEP, sep="\n")


def cluster_report(obj):
    '''
    Given there are clusters, print out a cluster report, printing clusters with multiple hits
    '''
    tab = obj.cluster_size_dist
    subtitle = header("Clusters with more than one sequence", 3)
    print(subtitle, sep="\n")
    g = obj.df.groupby('clusterid')
    ix = g.size() > 1
    ix = sorted(ix.index[ix], key=int)
    for i in ix:
        h = g.get_group(i)
        subsubtitle = header(f"Cluster {i}", 4)
        col_headers = h.columns.values
        tab_cap = f"Title: Sequences in cluster {i}"
        tab_body = tabulate(h, showindex=False,
                            headers=col_headers, tablefmt=TABLEFMT)
        print(subsubtitle,
              tab_cap,
              tab_body,
              "",
              sep="\n\n")
    print(SEP, sep="\n")


def category_report(obj):
    '''
    Given categories have been parse, print out a category report.
    '''
    tab = getattr(obj, "categories_by_cluster_dist_sum", None)
    if tab is None:
        return
    col_header = tab.columns.values
    title = header("Category report", 2)
    subtitle = header("Distribution of categories by cluster of sequences.", 3)
    tab_cap = f"Table: Distribution of categories by cluster of sequences."
    tab_body = tabulate(tab, showindex=False,
                        headers=col_header, tablefmt=TABLEFMT)
    print(title,
          subtitle,
          tab_cap,
          tab_body,
          "",
          sep="\n\n")

    subtitle = header("Clusters with more than one category", 3)
    print(subtitle, sep="\n")
    if tab['max'].values[0] > 1:
        g = obj.df.groupby('clusterid')
        ix = g.size() > 1
        ix = sorted(ix.index[ix], key=int)
        for i in ix:
            h = g.get_group(i)
            if h.category.nunique() > 1:
                subsubtitle = header(f"Cluster {i}", 4)
                col_headers = h.columns.values
                tab_cap = f"Title: Sequences in cluster {i}"
                tab_body = tabulate(h, showindex=False,
                                    headers=col_headers, tablefmt=TABLEFMT)
                print(subsubtitle,
                      tab_cap,
                      tab_body,
                      "",
                      sep="\n\n")
    else:
        msg = bold(
            "Congratulations! There were no clusters with more than one category.")
        print(msg, sep="\n")
    print(SEP, sep="\n")


def footer():
    '''
    Print a footer
    '''
    footer1 = italics(f"Generated using db-check v{version_string}")
    footer2 = f"db-check is on {link('GitHub', 'https://github.com/andersgs/db-check')}. Please submit {link('issues', 'https://github.com/andersgs/db-check/issues')}"
    print(" ",
          footer1,
          footer2,
          sep="\n\n")


def generate_report(checklist_obj):
    '''
    Generate various summaries
    '''
    preamble(checklist_obj)
    summary(checklist_obj)
    clusters_summary(checklist_obj)
    duplicate_report(checklist_obj)
    category_report(checklist_obj)
    footer()
