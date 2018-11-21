'''
A module for different checks that should be performed
'''

import inspect
from db_check.messages import *


class DBChecklist():
    '''
    A class to hold all the necessary summary data and checks
    '''

    def __init__(self, dataframe, author, db_name):
        '''
        Initialise the instance and attached the dataframe
        '''
        self.author = author
        self.db_name = db_name
        self.df = dataframe
        self.issues = []
        self._summarise()
        if 'category' in self.df.columns:
            self._summarise_categories()

    def _summarise(self):
        '''
        Add some summary data to the instance.
        '''
        dataframe = self.df
        self.total_entries = dataframe.shape[0]
        self.total_clusters = dataframe.clusterid.nunique()
        self.n_unique_sequences = dataframe.seqid.nunique()
        self.cluster_size_dist = dataframe.groupby(
            'clusterid')['clusterid'].count().describe().to_frame().transpose()

    def _summarise_categories(self):
        '''
        Given we have parsed categories, summarise them.
        '''
        dataframe = self.df
        self.n_unique_categories = dataframe.category.nunique()
        self.categories_by_cluster_dist = dataframe.groupby(
            'clusterid')['category'].nunique()
        self.categories_by_cluster_dist_sum = self.categories_by_cluster_dist.describe(
        ).to_frame().transpose()

    def ticks(self):
        '''
        Run checks and tick them off.
        '''
        checks = {method_name: method for method_name, method in inspect.getmembers(
            self, predicate=inspect.ismethod) if method_name.startswith("_check")}
        for check in checks:
            checks[check]()

    def _check_for_duplicates(self):
        '''
        Are there two or more sequences with same ID?
        '''
        info("Checking for duplicated sequence IDs...")
        if self.n_unique_sequences == self.total_entries:
            success("Found no duplicate sequences")
        else:
            warning("Found possibly duplicated sequence IDs")
            self.issues.append('More than one sequence with same ID.')

    def _check_for_overlapping_seqs(self):
        '''
        Are there two or more sequences with 100% identity indicating sub-sequences or completely duplicated sequences?
        '''
        info(
            "Checking for partially or completely overlapping sequences...")
        if self.total_clusters == self.total_entries:
            success("All sequences are unique")
        else:
            warning(
                "Found partially and/or completely overlapping sequences")
            self.issues.append(
                'Partially and/of completely overlapping sequences.')

    def _check_for_overlapping_seqs_distinct_categories(self):
        '''
        Are there partially and/or completely overlapping sequences that have distinct categories?

        Only run if categories are parsed out.
        '''
        if 'category' not in self.df.columns:
            return
        info(
            "Checking for partially and/or completely overlapping sequences with distinct categories...")
        if self.categories_by_cluster_dist.max() == 1:
            success(
                "There were no partially and/or overlapping sequences with distinct categories.")
        else:
            warning(
                "Found partially and/or completely overlapping sequences with distinct categories.")
            self.issues.append(
                'Partially and/of completely overlapping sequences with distinct categories.')
