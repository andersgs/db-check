'''
Check a FASTA DB for odd entries

Depends on CD-HIT
'''

import collections
import pathlib
import re

import pandas as pd


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
    If the line is a record in a cluster, parse the record.

    Examples:
    0       1269nt, >71|z4,z32... *
    1       1269nt, >72|z4,z32... at +/100.00%

    Return
    For 0
    {length: 1269,
     seqid: 71\|z4,z32,
     is_centroid: True,
     match: 1,
     cluster_id: 597}

     For 1
    {length: 1269,
     seqid: 71\|z4,z32,
     is_centroid: False,
     match: 1,
     cluster_id: 597}
    '''
    # pattern is used to pull the percent identity
    pat = re.compile(r'[0-9]{1,3}\.?[0-9]?[0-9]?')
    record = collections.OrderedDict()
    record['clusterid'] = cluster_id
    *_, length, seqid = line.strip().split(None, 2)
    length = length.replace("nt,", "")
    fasta_header, match = seqid.split("...")
    record['seqid'] = fasta_header[1:].replace("|", "\|")
    record['length'] = length
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


def parse_categories(dataframe, **parse_args):
    '''
    A function to parse out categories from sequence IDs

    parse_arguments can be:
    - delimiter: character vector to split ID
    - field: field number in 0-index designating which field to keep
    OR
    - regex: a regex expression with a single capture group
    OR
    - callback: a function that takes the seqid and returns the 
        category
    '''
    if "delimiter" in parse_args.keys():
        # must check that delimiter and field are both set
        # in the command line option
        delimiter = parse_args['delimiter']
        field = int(parse_args['field'])
        dataframe['category'] = dataframe.seqid.str.split(
            delimiter).str.get(field)
    elif "regex" in parse_args.keys():
        regex = parse_args['regex']
        dataframe['category'] = dataframe.seqid.str.extract(
            regex, expand=False)
    elif "callback" in parse_args.keys():
        callback = parse_args['callback']
        dataframe['category'] = dataframe.seqid.apply(lambda s: callback(s))
    else:
        raise Exception("Not sure how to parse categories.")
    return dataframe
