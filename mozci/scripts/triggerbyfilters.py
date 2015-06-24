"""
This script retriggers N times every job that matches --includes and doesn't match --exclude .

usage:
python th_filters.py repo rev --includes "args to include" --exclude  "args to exclude --times N"
"""
import logging
import urllib

from argparse import ArgumentParser

from mozci.mozci import trigger_range, query_repo_name_from_buildername, query_builders
from mozci.platforms import filter_buildernames
from mozci.utils.misc import setup_logging


def parse_args(argv=None):
    """Parse command line options."""
    parser = ArgumentParser()

    # Required arguments

    parser.add_argument("repo",
                        help='Branch name')

    parser.add_argument("rev",
                        help='The 12 character representing a revision (most recent).')

    parser.add_argument('-i', "--includes",
                        dest="includes",
                        required=True,
                        type=str,
                        help="comma-separated treeherder filters to include.")

    parser.add_argument('-e', "--exclude",
                        dest="exclude",
                        type=str,
                        help="comma-separated treeherder filters to exclude.")

    parser.add_argument("--times",
                        dest="times",
                        type=int,
                        default=1,
                        help="Number of times to retrigger the push.")

    parser.add_argument("--dry-run",
                        action="store_true",
                        dest="dry_run",
                        help="flag to test without actual push.")

    parser.add_argument("--debug",
                        action="store_true",
                        dest="debug",
                        help="set debug for logging.")

    options = parser.parse_args(argv)
    return options


def main():
    options = parse_args()

    if options.debug:
        LOG = setup_logging(logging.DEBUG)
        LOG.info("Setting DEBUG level")
    else:
        LOG = setup_logging(logging.INFO)

    filters_in = options.includes.split(',') + [options.repo]
    filters_out = []

    if options.exclude:
        filters_out = options.exclude.split(',')

    buildernames = filter_buildernames(filters_in, filters_out, query_builders())

    cont = raw_input("%i jobs will be triggered, do you wish to continue? y/n/d (d=show details) "
                     % len(buildernames))
    if cont.lower() == 'd':
        LOG.info("The following jobs will be triggered: \n %s" % '\n'.join(buildernames))
        cont = raw_input("Do you wish to continue? y/n ")

    if cont.lower() != 'y':
        exit(1)

    for buildername in buildernames:
        trigger_range(
            buildername=buildername,
            revisions=[options.rev],
            times=options.times,
            dry_run=options.dry_run,
        )

        LOG.info('https://treeherder.mozilla.org/#/jobs?%s' %
                 urllib.urlencode({'repo': query_repo_name_from_buildername(buildername),
                                   'fromchange': options.rev,
                                   'tochange': options.rev,
                                   'filter-searchStr': buildername}))


if __name__ == '__main__':
    main()
