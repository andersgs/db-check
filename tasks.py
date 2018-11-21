'''
Automate deployment to PyPi
'''

import invoke


@invoke.task
def deploy_patch(ctx):
    '''
    Automate deployment
    rm -rf build/* dist/*
    bumpversion patch --verbose
    python3 setup.py sdist bdist_wheel
    twine upload dist/*
    git push --tags
    '''
    ctx.run("rm -rf build/* dist/*")
    ctx.run("bumpversion patch --verbose")
    ctx.run("python3 setup.py sdist bdist_wheel")
    ctx.run("twine check dist/*")
    ctx.run("twine upload dist/*")
    ctx.run("git push --tags")
