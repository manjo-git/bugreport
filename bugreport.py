#! /usr/bin/python
# Author: Manoj Iyer manoj.iyer@canonical.com
# License: GPLv3
from launchpadlib.launchpad import Launchpad
from launchpadlib.uris import LPNET_SERVICE_ROOT
from launchpadlib.credentials import Credentials
from optparse import OptionParser
from re import compile
from datetime import datetime as dt
from collections import defaultdict as coldict
import numpy as np
import os
import sys


def gen_bug_report(lp, lp_bugs, project, verbose):
    bug_summary_info = coldict(dict)
    bug_details_info = coldict(dict)
    url = compile('https://api.launchpad.net/1.0/~|/')

    for task in lp_bugs:
        bug_info = {}
        bug_subtask = []

        if task.status in bug_summary_info[task.importance]:
            bug_summary_info[task.importance][task.status] += 1
        else:
            bug_summary_info[task.importance][task.status] = 1

        if '#Bugs Processed' in bug_summary_info[task.importance]:
            bug_summary_info[task.importance]['#Bugs Processed'] += 1
        else:
            bug_summary_info[task.importance]['#Bugs Processed'] = 1

        if '#Bugs Closed' not in bug_summary_info[task.importance]:
            bug_summary_info[task.importance]['#Bugs Closed'] = 0

        # A bug could affect multiple projects, we care only whether
        # the project we are tracking is complete.
        lp_bug_tasks = lp.bugs[task.bug.id].bug_tasks
        for bugtask in lp_bug_tasks:
            if bugtask.bug_target_name in project:
                bug_is_complete = bugtask.is_complete
            if verbose is True:
                bug_subtask.append(
                    '%s: %s' % (bugtask.bug_target_name, bugtask.status))

        if bug_is_complete is True:
            if '#Bugs Closed' in bug_summary_info[task.importance]:
                bug_summary_info[task.importance]['#Bugs Closed'] += 1

        if verbose is True:
            inactive_days = 0
            if bug_is_complete is not True:
                inactive_days = np.busday_count(
                    task.bug.date_last_updated.strftime("%Y-%m-%d"),
                        dt.now().strftime("%Y-%m-%d"))

            active_days = np.busday_count(
                task.bug.date_created.strftime("%Y-%m-%d"),
                    task.bug.date_last_updated.strftime("%Y-%m-%d"))

            assignee = 'Unassigned' if task.assignee_link is None \
                else url.sub('', task.assignee_link)

            bug_info[task.bug.id] = [
                task.bug.date_created.strftime("%Y-%m-%d"),
                    task.bug.date_last_updated.strftime("%Y-%m-%d"),
                    active_days,
                    inactive_days, task.bug.message_count, assignee,
                    "''<br>''".join(bug_subtask)]

            bug_details_info[task.importance].update(bug_info)

    return bug_summary_info, bug_details_info


def main():
    parser = OptionParser(usage='usage: %prog [options]', version='%prog 1.0')
    parser.add_option('-d', '--date', dest='start_date', action='store',
                      default='2017-01-01',
                      type='string', help='start date for bug search')
    parser.add_option('-p', '--project', dest='project', action='store',
                      default='ubuntu-power-systems',
                      type='string', help='name of the launchpad project')
    parser.add_option('-s', '--status', dest='bug_status', action='store',
                      default=('New,Opinion,Invalid,Won\'t Fix,Expired,'
                               'Confirmed,Triaged,In Progress,Fix Committed,'
                               'Fix Released,Incomplete'),
                      type='string',
                      help='bug status (or quoted and comma seperated list)')
    parser.add_option('-i', '--importance', dest='bug_importance',
                      default=(
                          'Unknown,Undecided,Critical,High,Medium,Low,Wishlist'),
                      type='string',
                      help='bug importance (or comma seperated list, no spaces)')
    parser.add_option('-t', '--tag', dest='bug_tag', default=None,
                      help='bug tag (or quoted and comma seperated list)')
    parser.add_option('-m', '--modify', dest='bug_tag_modify', default='Any',
                      help='search any or all tags (valid args: any or all)')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help='verbose output with bug details')
    parser.add_option('-a', '--author', dest='author',
                      default='Manoj Iyer manoj.iyer@canonical.com',
                      help='"Firstname Lastname first.last@canonical.com"')
    parser.add_option('-o', '--outfile', dest='outfile',
                      help='filename to store output (default stdout)')

    (options, args) = parser.parse_args()

    if len(args) is None:
        parser.error("No arguments found!")

    script_name = sys.argv[0].split("/")[-1].split('.')[0]
    cachedir = os.path.expanduser('~/.launchpadlib/cache')

    launchpad = Launchpad.login_with(script_name, LPNET_SERVICE_ROOT, cachedir)
    lp_project = launchpad.projects[options.project]

    lp_bugs = [
        task for task in lp_project.searchTasks(
            created_since=None if options.start_date is None else
                        dt.strptime(options.start_date,
                                    '%Y-%m-%d').isoformat(),
                status=options.bug_status.split(','),
                importance=options.bug_importance.title().replace(
                    ' ', '').split(','),
                tags=None if options.bug_tag is None else
                        options.bug_tag.split(','),
                tags_combinator=options.bug_tag_modify.title())]

    with (open(options.outfile, 'w') if options.outfile else sys.stdout) as f:
        f.write("Bug activity in %s project since %s\n\n\n" % (options.project,
                options.start_date))
        f.write(" || {:<35} | {:<20} |\n".format('Created By', 'Date'))
        f.write("  | [%s]" % (options.author) + " | %%mtime(%A %B %d, %Y) |\n")

        if f is not sys.stdout and options.verbose is True:
            sys.stdout.write("Bug activity in %s project since %s\n" %
                             (options.project, options.start_date))
            sys.stdout.write("Generating detailed report in %s \n" %
                             options.outfile)
            sys.stdout.write("Please wait...\n")
            sys.stdout.flush()

        summary_report, detailed_report = gen_bug_report(launchpad, lp_bugs,
                                                         options.project,
                                                         options.verbose)

        for k, v in sorted(summary_report.iteritems()):
            f.write("\n= Summary of %s bugs =\n" % k)
            f.write("|| {:<14} | {:<8} |\n".format('Status', 'Count'))
            for x, y in sorted(v.iteritems()):
                f.write("| {:<15} | {:<8} |\n".format(x, y))
            if options.verbose is True:
                f.write("== Details on %s bugs ==\n" % k)
                f.write("|| Bug# | Created | Last Updated | Active Period "
                        "| Dormant Period | #Comments | Assignee | Status |\n")

                for a, b in sorted(detailed_report[k].iteritems(),
                                   key=lambda item: item[1][1], reverse=True):
                    f.write("| [%s https://launchpad.net/bugs/%s] | %s |\n" %
                            (a, a, ' | '.join(map(str, b))))

        if f is not sys.stdout:
            f.close()


if __name__ == '__main__':
    main()
