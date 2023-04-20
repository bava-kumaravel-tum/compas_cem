# -*- coding: utf-8 -*-
from __future__ import print_function

import contextlib
import tempfile
import glob
import os
import sys
from shutil import rmtree

from invoke import Exit
from invoke import task

try:
    input = raw_input
except NameError:
    pass


BASE_FOLDER = os.path.dirname(__file__)


class Log(object):
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self.out = out
        self.err = err

    def flush(self):
        self.out.flush()
        self.err.flush()

    def write(self, message):
        self.flush()
        self.out.write(message + '\n')
        self.out.flush()

    def info(self, message):
        self.write('[INFO] %s' % message)

    def warn(self, message):
        self.write('[WARN] %s' % message)


log = Log()


def confirm(question):
    while True:
        response = input(question).lower().strip()

        if not response or response in ('n', 'no'):
            return False

        if response in ('y', 'yes'):
            return True

        print('Focus, kid! It is either (y)es or (n)o', file=sys.stderr)


@task(default=True)
def help(ctx):
    """Lists available tasks and usage."""
    ctx.run('invoke --list')
    log.write('Use "invoke -h <taskname>" to get detailed help for a task.')


@task(help={
    'docs': 'True to clean up generated documentation, otherwise False',
    'bytecode': 'True to clean up compiled python files, otherwise False.',
    'builds': 'True to clean up build/packaging artifacts, otherwise False.',
    'ghuser': 'True to clean up ghuser files, otherwise False.'})
def clean(ctx, docs=True, bytecode=True, builds=True, ghuser=True):
    """Cleans the local copy from compiled artifacts."""
    with chdir(BASE_FOLDER):
        if builds:
            ctx.run('python setup.py clean')

        if bytecode:
            for root, dirs, files in os.walk(BASE_FOLDER):
                for f in files:
                    if f.endswith('.pyc'):
                        os.remove(os.path.join(root, f))
                if '.git' in dirs:
                    dirs.remove('.git')

        folders = []

        if docs:
            folders.append('docs/api/generated')
            folders.append('dist/')

        if bytecode:
            for t in ('src', 'tests'):
                folders.extend(glob.glob('{}/**/__pycache__'.format(t), recursive=True))

        if builds:
            folders.append('build/')
            folders.append('src/compas_cem.egg-info/')

        if ghuser:
            folders.append('src/compas_cem/ghpython/components/ghuser')

        for folder in folders:
            rmtree(os.path.join(BASE_FOLDER, folder), ignore_errors=True)


@task(help={
      'rebuild': 'True to clean all previously built docs before starting, otherwise False.',
      'doctest': 'True to run doctests, otherwise False.',
      'check_links': 'True to check all web links in docs for validity, otherwise False.'})
def docs(ctx, doctest=False, rebuild=False, check_links=False):
    """Builds package's HTML documentation."""

    if rebuild:
        clean(ctx)

    with chdir(BASE_FOLDER):
        if doctest:
            testdocs(ctx)

        opts = '-E' if rebuild else ''
        ctx.run('sphinx-build {} -b html docs dist/docs'.format(opts))

        if check_links:
            linkcheck(ctx, rebuild=rebuild)


@task()
def lint(ctx):
    """Check the consistency of coding style."""
    log.write('Running flake8 python linter...')
    ctx.run('flake8 src')


@task()
def testdocs(ctx):
    """Test the examples in the docstrings."""
    log.write('Running doctest...')
    ctx.run('pytest --doctest-modules')


@task()
def linkcheck(ctx, rebuild=False):
    """Check links in documentation."""
    log.write('Running link check...')
    opts = '-E' if rebuild else ''
    ctx.run('sphinx-build {} -b linkcheck docs dist/docs'.format(opts))


@task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""

    with chdir(BASE_FOLDER):
        lint(ctx)

        log.write('Checking MANIFEST.in...')
        ctx.run('check-manifest')

        log.write('Checking metadata...')
        ctx.run('python setup.py check --strict --metadata')


@task(help={
      'checks': 'True to run all checks before testing, otherwise False.'})
def test(ctx, checks=False, doctest=False):
    """Run all tests."""
    if checks:
        check(ctx)

    with chdir(BASE_FOLDER):
        cmd = ['pytest']
        if doctest:
            cmd.append('--doctest-modules')

        ctx.run(' '.join(cmd))


@task
def prepare_changelog(ctx):
    """Prepare changelog for next release."""
    UNRELEASED_CHANGELOG_TEMPLATE = '\nUnreleased\n----------\n\n**Added**\n\n**Changed**\n\n**Fixed**\n\n**Deprecated**\n\n**Removed**\n'

    with chdir(BASE_FOLDER):
        # Preparing changelog for next release
        with open('CHANGELOG.rst', 'r+') as changelog:
            content = changelog.read()
            start_index = content.index('----------')
            start_index = content.rindex('\n', 0, start_index - 1)
            last_version = content[start_index:start_index + 11].strip()

            if last_version == 'Unreleased':
                log.write('Already up-to-date')
                return

            changelog.seek(0)
            changelog.write(content[0:start_index] + UNRELEASED_CHANGELOG_TEMPLATE + content[start_index:])

        ctx.run('git add CHANGELOG.rst && git commit -m "Prepare changelog for next release"')


@task(help={'release_type': 'Type of release follows semver rules. Must be one of: major, minor, patch.'})
def release(ctx, release_type):
    """Releases the project in one swift command!"""
    if release_type not in ('patch', 'minor', 'major'):
        raise Exit('The release type parameter is invalid.\nMust be one of: major, minor, patch')

    # Run checks
    ctx.run('invoke check test')

    # Bump version and git tag it
    ctx.run('bump2version %s --verbose' % release_type)

    # Build project
    ctx.run('python setup.py clean --all sdist bdist_wheel')

    # Prepare changelog for next release
    prepare_changelog(ctx)

    # Clean up local artifacts
    clean(ctx)

    # Upload to pypi
    if confirm('Everything is ready. You are about to push to git which will trigger a release to pypi.org. Are you sure? [y/N]'):
        ctx.run('git push --tags && git push')
    else:
        raise Exit('You need to manually revert the tag/commits created.')


@contextlib.contextmanager
def chdir(dirname=None):
    current_dir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(current_dir)


@task(help={
      'gh_io_folder': 'Folder where GH_IO.dll is located. If not specified, it will try to download from NuGet.',
      'ironpython': 'Command for running the IronPython executable. Defaults to `ipy`.'})
def ghplugin(ctx, gh_io_folder=None, ironpython=None):
    """Build Grasshopper user objects from source

    Notes
    -----
    If you are building the gh plugin on mac for the first time, you will 
    probably have to download mono, ironpython, the GH_IO.dll library and the 
    ipy.sh script. 

    You can get GH_IO.dll and the ipy.sh script from the temp/ folder in your
    last computer. Or look around online.
    
    Download the mono installer from https://www.mono-project.com.
    Then, download the ironpython installer from their github releases page:
    https://github.com/IronLanguages/ironpython2/releases

    Note that you may need to update the ipy.sh script to point to the correct
    version of mono and ironpython.

    Have fun.
    """
    clean(ctx, docs=False, bytecode=False, builds=False, ghuser=True)
    with chdir(BASE_FOLDER):
        with tempfile.TemporaryDirectory('actions.ghcomponentizer') as action_dir:
            source_dir = os.path.abspath('src/compas_cem/ghpython/components')
            target_dir = os.path.join(source_dir, 'ghuser')
            ctx.run('git clone https://github.com/compas-dev/compas-actions.ghpython_components.git {}'.format(action_dir))

            if not gh_io_folder:
                gh_io_folder = 'temp'
                import compas_ghpython
                compas_ghpython.fetch_ghio_lib(gh_io_folder)

            if not ironpython:
                # TODO ipy.sh is a file stored in the temp folder
                # The default approach from COMPAS was to invoke 'ipy'
                # But I replaced that here to make it work with my current install
                # macOS Catalina 10.15.7
                ironpython = 'sh temp/ipy.sh'  # 'ipy'

            gh_io_folder = os.path.abspath(gh_io_folder)
            componentizer_script = os.path.join(action_dir, 'componentize.py')

            ctx.run('{} {} {} {} --ghio "{}"'.format(ironpython, componentizer_script, source_dir, target_dir, gh_io_folder))
