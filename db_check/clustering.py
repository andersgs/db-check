'''
Defining how clustering of the DB is done.

Here, we use CD-HIT to perform the clustering.
'''

import sh


def cluster_db(filename, threads=4):
    '''
    Given a FASTA DB, cluster it using CD-HIT. In this case, using cd-hit-est.
    '''
    cdhit = sh.Command('cd-hit-est')
    p = cdhit('-i', filename, '-o', 'cdhit', '-c',
              '1.00', '-g', '1', '-T', threads, '-d', '0')
    return "cdhit.clstr"
