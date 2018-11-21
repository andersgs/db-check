'''
Defining how clustering of the DB is done.

Here, we use CD-HIT to perform the clustering.
'''

import pathlib
import shutil
import sh
import re
import tempfile

from db_check.messages import error, info, success


def check_dependencies():
    '''
    Check if CD-HIT is available
    '''
    version_pat = re.compile(r'.*([0-9]{1}\.[0-9]{1,2}).*')
    info("Checking if CD-HIT is present in the PATH...")
    cdhit_path = shutil.which('cd-hit-est')
    if cdhit_path is None:
        error("Could not find CD-HIT in your PATH.")
        error("Please make sure to add it to your PATH or install it. You can use brew or conda.")
        raise FileNotFoundError
    cdhit = sh.Command('cd-hit-est')
    p = cdhit("-h", _ok_code=[0, 1])
    [version_string, *_] = version_pat.search(p.stdout.decode('utf8')).groups()
    success(f"Found CD-HIT version {version_string}")


def cluster_db(filename, prefix, threads=4):
    '''
    Given a FASTA DB, cluster it using CD-HIT. In this case, using cd-hit-est.
    '''
    cdhit = sh.Command('cd-hit-est')
    fn = pathlib.Path(filename)
    tmpdir = tempfile.TemporaryDirectory()
    workdir = pathlib.Path(tmpdir.name)
    wd_prefix = workdir / prefix
    p = cdhit('-i', f'{fn.as_posix()}', '-o', f'{wd_prefix.as_posix()}',
              '-c', '1.00', '-g', '1', '-T', threads, '-d', '0')
    return f"{wd_prefix}.clstr", tmpdir
