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
from uuid import uuid4 as uid
from pwd import getpwuid as getname
import numpy as np
import os
import sys
import pwd
try:
    import txt2tags
except:
    print sys.exc_info()
    print "\nsudo apt install txt2tags"


def gen_bug_report(lp, lp_bugs, project, searchtags, verbose):
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

        if task.bug.id not in bug_details_info[task.importance]:
            if '#Bugs Processed' in bug_summary_info[task.importance]:
                bug_summary_info[task.importance]['#Bugs Processed'] += 1
            else:
                bug_summary_info[task.importance]['#Bugs Processed'] = 1
            if searchtags is not None:
                for tags in searchtags.split(','):
                    if tags in task.bug.tags:
                        tag_name = '#%s tags' % tags
                        if tag_name in bug_summary_info[task.importance]:
                            bug_summary_info[task.importance][tag_name] += 1
                        else:
                            bug_summary_info[task.importance][tag_name] = 1

        if project is not None:
            if '#Bugs Closed' not in bug_summary_info[task.importance]:
                bug_summary_info[task.importance]['#Bugs Closed'] = 0

        # A bug could affect multiple projects, we care only whether
        # the project we are tracking is complete.
        lp_bug_tasks = lp.bugs[task.bug.id].bug_tasks
        for bugtask in lp_bug_tasks:
            if project is not None and bugtask.bug_target_name in project:
                bug_is_complete = bugtask.is_complete
            if verbose is True:
                bug_subtask.append(
                    '%s: %s' % (bugtask.bug_target_name, bugtask.status))

        if project is not None and bug_is_complete is True:
            if '#Bugs Closed' in bug_summary_info[task.importance]:
                bug_summary_info[task.importance]['#Bugs Closed'] += 1

        if verbose is True:
            assignee = 'Unassigned' if task.assignee_link is None \
                else url.sub('', task.assignee_link)

            bug_info[task.bug.id] = [
                task.bug.date_created.strftime("%Y-%m-%d"),
                    task.bug.date_last_updated.strftime("%Y-%m-%d"),
                    task.bug.message_count, assignee,
                    "''<br>''".join(bug_subtask)]

            bug_details_info[task.importance].update(bug_info)

    return bug_summary_info, bug_details_info


def main():
    parser = OptionParser(usage='usage: %prog [options]', version='%prog 1.0')
    parser.add_option('-d', '--date', dest='start_date', action='store',
                      default=None,
                      type='string', 
                      help='start date (YYYY-MM-DD) for bug search')
    parser.add_option('-p', '--project', dest='project', action='store',
                      default=None,
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
                      default='%s %s' % (
                          getname(os.getuid())[4].strip(','),
                          os.environ.get('DEBEMAIL')),
                      help='"Firstname Lastname first.last@canonical.com"')
    parser.add_option('-o', '--outfile', dest='outfile',
                      help='filename to store output (default stdout)')

    (options, args) = parser.parse_args()

    if len(args) is None:
        parser.error("No arguments found!")

    script_name = sys.argv[0].split("/")[-1].split('.')[0]
    cachedir = os.path.expanduser('~/.launchpadlib/cache')

    launchpad = Launchpad.login_with(script_name, LPNET_SERVICE_ROOT, cachedir)
    lp_object = launchpad.projects[options.project] if options.project is not None else launchpad.bugs

    lp_bugs = [
        task for task in lp_object.searchTasks(
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
        f.write("Bug activity report since %s\n\n\n" % (options.start_date))
        f.write(" || {:<38} | {:<20} |\n".format('Created By', 'Date'))
        f.write("  | [%s] | %s |\n" % 
            (options.author, dt.today().strftime('%A %B %d, %Y')))

        if f is not sys.stdout and options.verbose is True:
            sys.stdout.write("Bug activity report since %s\n" %
                             (options.start_date))
            sys.stdout.write("Generating detailed report please wait...\n");
            sys.stdout.flush()

        summary_report, detailed_report = gen_bug_report(launchpad, lp_bugs,
                                                         options.project,
                                                         options.bug_tag,
                                                         options.verbose)

        for k, v in sorted(summary_report.iteritems()):
            f.write("\n= Summary of %s bugs =\n" % k)
            f.write("|| {:<14} | {:<8} |\n".format('Status', 'Count'))
            for x, y in sorted(v.iteritems()):
                f.write("| {:<15} | {:<8} |\n".format(x, y))
            if options.verbose is True:
                f.write("== Details on %s bugs ==\n" % k)
                f.write("|| Bug# | Created | Last Updated | "
                        "#Comments | Assignee | Status |\n")

                for a, b in sorted(detailed_report[k].iteritems(),
                                   key=lambda item: item[1][1], reverse=True):
                    f.write("| [%s https://launchpad.net/bugs/%s] | %s |\n" %
                            (a, a, ' | '.join(map(str, b))))

        if f is not sys.stdout:
            f.close()
            htmlconv = str(uid())
            with open(htmlconv, 'w') as tf:
                tf.write("""%!options: --toc-level 4
%!postproc(html): '(?i)(<TH)' '\\1 style="text-align:left;"'
%!postproc(html): '(?i)(<TR)' '\\1 style="font-size:11; font-family:ubuntu,sans-serif; text-align:left;"'
%!postproc(html): <HEAD>      '<HEAD>\\n<STYLE TYPE="text/css">\\n</STYLE>'
%!postproc(html): (</STYLE>)  'h1 {color:#740946; font-size:16; font-family:ubuntu,sans-serif;} \\n\\1'
%!postproc(html): (</STYLE>)  'h2 {color:#740946; font-size:14; font-family:ubuntu,sans-serif;} \\n\\1'
%!postproc(html): (</STYLE>)  'h3 {color:#740946; font-size:12; font-family:ubuntu,sans-serif;} \\n\\1'
%!postproc(html): (</STYLE>)  'h4 {color:#740946; font-size:11; font-family:ubuntu,sans-serif;} \\n\\1'
%!postproc(html): (</STYLE>)  'body {font-size:11; font-family:ubuntu,sans-serif;;} \\n\\1'\n""")
                tf.flush()
                tf.close()

                cmd='-t html -C %s -i %s' % (htmlconv, options.outfile)
                txt2tags.exec_command_line(cmd.split())
            os.remove(htmlconv)
            os.remove(options.outfile)


if __name__ == '__main__':
    main()
