# -*- coding: utf-8 -*-
""" SVN Chart
"""

# Imports
from optparse import OptionParser
# from subprocess import call, Popen
# import subprocess
# import xml.etree.ElementTree
# import os.path
# import dateutil.parser
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec
import svn.utility
# from matplotlib.cbook import get_sample_data
import numpy

# import random

color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

graph_time_delta = timedelta(days=1)


class LogEntry:
    def __init__(self, date, author):
        self.date = date
        self.author = author


def get_svn_log(url, username, password):
    repo = svn.utility.get_client(url)

    return sorted(list(repo.log_default()), key=lambda x: x.date)


def print_commit_total(log_entries):
    with open('commits_total.csv', 'w+') as f:
        f.write("date,commits\n")

        current_date = min(x.date for x in log_entries)
        commit_count = 0

        for entry in log_entries:

            while entry.date > current_date:
                current_date += graph_time_delta
                f.write(str(current_date) + "," + str(commit_count) + "\n")

            commit_count += 1

        current_date += graph_time_delta
        f.write(str(current_date) + "," + str(commit_count) + "\n")


def print_commit_total_per_user(log_entries):
    first_date = min(x.date for x in log_entries)

    current_date = first_date

    # Create a dictionary of each author to their commit count (starting at 0)
    user_commit_dict = dict([x.author or "unknown", 0] for x in log_entries)

    with open('commits_per_user.csv', 'w+') as f:
        f.write('date,')
        f.write(','.join(user_commit_dict.keys()) + "\n")

        for entry in log_entries:
            while entry.date > current_date:
                current_date += timedelta(days=1)
                f.write(str(current_date))

                for key in user_commit_dict.keys():
                    f.write(',' + str(user_commit_dict[key]))

                f.write("\n")

            user_commit_dict[entry.author] += 1


def chart_commit_total():
    commit_data = csv2rec('commits_total.csv')
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    line = plt.plot(commit_data.date,
                    commit_data['commits'],
                    lw=2.5,
                    color=color_sequence[0])

    plt.savefig('commits_total.svg', bbox_inches='tight')


def chart_commit_total_per_user():
    all_commit_data = csv2rec('commits_per_user.csv')
    fig, ax = plt.subplots(1, 1, figsize=(30, 22.5))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    last_date = all_commit_data['date'][-1]

    for i in range(len(all_commit_data.dtype.descr)):

        desc = all_commit_data.dtype.descr[i]
        column_name = desc[0]

        # The date column is used as the X axis, and doesn't need to be graphed
        if column_name == 'date':
            continue

        data = all_commit_data[column_name]
        last_commit_count = data[-1]

        # Remove all the records with the same commit count as the last record
        # That way the line stops when the author stops making commits
        truncated_data = numpy.delete(data,
                                      numpy.where(data == last_commit_count))

        # Except we just removed the last record, better put that back
        truncated_data = numpy.append(truncated_data, last_commit_count)

        # Shrink the size of the date list to match the data list
        truncated_dates = numpy.resize(all_commit_data.date,
                                       truncated_data.shape)

        lineColour = color_sequence[i % len(color_sequence)]

        line = plt.plot(truncated_dates,
                        truncated_data,
                        lw=2.5,
                        color=lineColour)

        msg = "{user} ({commits})".format(user=column_name,
                                          commits=last_commit_count)

        plt.text(truncated_dates[-1] + timedelta(days=1),
                 last_commit_count - 0.5,
                 msg,
                 fontsize=8,
                 color=lineColour)

    plt.savefig('commits_per_user.svg', bbox_inches='tight')


def build_option_parser():
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username",
                      help="the user to connect as")

    parser.add_option("-p", "--password", dest="password",
                      help="the password of the user")

    parser.add_option("-d", "--download", action="store_true", dest="download",
                      help="downloads the log file even if it already exists")

    return parser


if __name__ == "__main__":
    parser = build_option_parser()
    (options, args) = parser.parse_args()

    log_entries = get_svn_log(args[0], options.username, options.password)

    print_commit_total(log_entries)
    chart_commit_total()

    print_commit_total_per_user(log_entries)
    chart_commit_total_per_user()
