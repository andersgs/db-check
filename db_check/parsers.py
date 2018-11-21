'''
Check a FASTA DB for odd entries

Depends on CD-HIT
'''

import collections
import pathlib
import re

import click
import pandas as pd
import sh
from tabulate import tabulate


def parse_cluster_id(line):
    '''
    If the line is a cluster ID, return the cluster number

    Example:
    >Cluster 597
    return 597
    '''
    line = line.strip().split()
    return line[1]


def parse_cluster_member(line, cluster_id):
    '''
    If the line is a record in a cluster, parse the record

    Examples:
    0       1269nt, >71|z4,z32... *
    1       1269nt, >72|z4,z32... at +/100.00%

    Return
    For 0
    {length: 1269,
     seqid: 71|z4,z32,
     is_centroid: True,
     match: 1,
     antigen: z4,z32}

     For 1
    {length: 1269,
     seqid: 71|z4,z32,
     is_centroid: False,
     match: 1,
     antigen: z4,z32}
    '''
    # pattern is used to pull the percent identity
    pat = re.compile(r'[0-9]{1,3}\.?[0-9]?[0-9]?')
    record = collections.OrderedDict()
    record['clusterid'] = cluster_id
    *_, length, seqid = line.strip().split(None, 2)
    length = length.replace("nt,", "")
    fasta_header, match = seqid.split("...")
    *_, category = fasta_header.split("|")
    record['seqid'] = fasta_header[1:]
    record['length'] = length
    record['category'] = category
    if match[-1] == '*':
        is_centroid = True
        match = 1.0
    else:
        is_centroid = False
        try:
            match = float(pat.search(match).group())/100
        except:
            print("Could not parse percent match from {line}".format(line))
            match = -1.0
    record['is_centroid'] = is_centroid
    record['match'] = match
    return record


def parse_record(line, cluster_id):
    '''
    Make decisions about the line
    '''
    if line[0] == '>':
        return True, parse_cluster_id(line)
    else:
        return False, parse_cluster_member(line, cluster_id)


def parse_clustering(filename):
    '''
    Given a clustering file produced from CD-HIT return a pandas.DataFrame
    with all the information
    '''
    cluster_file = pathlib.Path(filename)
    cluster_data = []
    cluster_id = 0
    with open(cluster_file, 'rt') as cf:
        for line in cf:
            new_cluster, record = parse_record(line, cluster_id)
            if new_cluster:
                cluster_id = record
            else:
                cluster_data.append(record)
    result = pd.DataFrame(cluster_data)
    return result


def cluster_db(filename, threads=4):
    '''
    Given a FASTA DB, cluster it using CD-HIT. In this case, using cd-hit-est.
    '''
    cdhit = sh.Command('cd-hit-est')
    p = cdhit('-i', filename, '-o', 'cdhit', '-c',
              '1.00', '-g', '1', '-T', threads, '-d', '0')
    return "cdhit.clstr"


def summarise_clustering(dataframe):
    '''
    Generate various summaries
    '''
    total_entries = dataframe.shape[0]
    total_clusters = dataframe.clusterid.nunique()
    n_unique_sequences = dataframe.seqid.nunique()
    unique_categories = dataframe.groupby(
        'clusterid')['category'].nunique().describe().to_frame().transpose()
    cluster_size_dist = dataframe.groupby(
        'clusterid')['clusterid'].count().describe().to_frame().transpose()
    print("#"*80)
    print("SOME SUMMARY INFORMATION...")
    print()
    print("Total records: {}".format(total_entries))
    print("Total clusters: {}".format(total_clusters))
    print("Total unique sequence IDs: {}".format(n_unique_sequences))
    print()
    print("#"*80)
    print("SOME DETAILS...")
    print()
    print("Distribution of cluster sizes:")
    print(cluster_size_dist)
    print()
    print("Summary of count of categories associated with each clusters:")
    print(unique_categories)
    print()
    if total_entries > n_unique_sequences:
        print("#"*80)
        print("CHECKING DUPLICATE IDS...")
        print()
        ix = dataframe.duplicated('seqid', keep=False)
        g = dataframe[ix].groupby("seqid")
        for h in g.groups:
            print("## Duplicate ID {}".format(h))
            print(g.get_group(h))
            print()
    g = dataframe.groupby('clusterid')
    ix = g.size() > 1
    ix = sorted(ix.index[ix], key=int)
    if len(ix) > 0:
        print("#"*80)
        print("LOOKING CLOSER...")
        print()
        print("Found clusters with more than one sequences...")
        print("Checking if there are any with multiple categories...")
        for i in ix:
            h = g.get_group(i)
            if h.category.nunique() > 1:
                print("## Cluster {}".format(i))
                print(h)
                print()
    print("#"*80)
    print("Done!")


@click.command()
@click.argument("fasta")
def run_db_check(fasta):
    clusters = cluster_db(fasta)
    tab = parse_clustering(clusters)
    summarise_clustering(tab)


if __name__ == "__main__":
    run_db_check()
