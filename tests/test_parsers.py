'''
Tests for the parsers
'''

from collections import OrderedDict

import pytest

from db_check.parsers import *


def test_parse_cluster_id():
    '''
    Make sure parse_cluster_id returns the correct ID
    '''
    clusterid = ">Cluster 597"
    assert parse_cluster_id(clusterid) == "597"


@pytest.mark.parametrize("test_input, expected", [
    ("0       1269nt, > 71|z4,z32... *",
     OrderedDict([('clusterid', '580'), ('seqid', ' 71\\|z4,z32'), ('length', '1269'), ('is_centroid', True), ('match', 1.0)])),
    ("1       1269nt, >72|z4,z32... at +/100.00%",
     OrderedDict([('clusterid', '580'), ('seqid', '72\\|z4,z32'), ('length', '1269'), ('is_centroid', False), ('match', 1.0)]))]
)
def test_cluster_member(test_input, expected):
    '''
    Make sure cluster_member returns correct dictionary
    '''
    assert parse_cluster_member(test_input, "580") == expected
