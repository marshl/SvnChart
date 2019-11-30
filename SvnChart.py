# -*- coding: utf-8 -*-
""" SVN Chart
"""

# Imports
from optparse import OptionParser
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec
import svn.utility
import numpy

commits_total_csv_path = "commits_total.csv"
commits_per_user_csv_path = "commits_per_user.csv"

commits_total_svg_path = "commits_total.svg"
commits_per_user_svg_path = "commits_per_user.svg"

color_sequence = [
    "#1f77b4",
    "#aec7e8",
    "#ff7f0e",
    "#ffbb78",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
    "#8c564b",
    "#c49c94",
    "#e377c2",
    "#f7b6d2",
    "#7f7f7f",
    "#bcbd22",
    "#dbdb8d",
    "#17becf",
    "#9edae5",
]

graph_time_delta = timedelta(days=1)


def get_repo(url):
    return svn.utility.get_client(url)


def get_svn_log(url, username, password):
    repo = get_repo(url)

    return sorted(list(repo.log_default()), key=lambda x: x.date)


def print_commit_total(log_entries):
    with open(commits_total_csv_path, "w+") as f:
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


def print_commit_total_per_user(log_entries, url, chart_line_changes=False):
    first_date = min(x.date for x in log_entries)
    current_date = first_date

    repo = get_repo(url)

    # Create a dictionary of each author to their commit count (starting at 0)
    user_commit_dict = dict([x.author or "unknown", 0] for x in log_entries)

    with open(commits_per_user_csv_path, "w+") as f:
        f.write("date,")
        f.write(",".join(user_commit_dict.keys()) + "\n")

        for entry in log_entries:

            author = entry.author or "unknown"

            while entry.date > current_date:
                current_date += graph_time_delta
                f.write(str(current_date))

                for key in user_commit_dict.keys():
                    f.write("," + str(user_commit_dict[key]))

                f.write("\n")

            if chart_line_changes:
                try:
                    print("Diffing revision {0}".format(entry.revision))
                    diffs = repo.diff(int(entry.revision), int(entry.revision) + 1)
                    for diff in diffs:
                        user_commit_dict[author] += diff["diff"].count("\n+")

                except Exception as ex:
                    print(ex)

            else:
                user_commit_dict[author] += 1


def chart_commit_total():
    commit_data = csv2rec(commits_total_csv_path)
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    line = plt.plot(
        commit_data.date, commit_data["commits"], lw=2.5, color=color_sequence[0]
    )

    plt.savefig(commits_total_svg_path, bbox_inches="tight")


def chart_commit_total_per_user():
    all_commit_data = csv2rec(commits_per_user_csv_path)
    fig, ax = plt.subplots(1, 1, figsize=(30, 22.5))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    user_labels = []

    for i in range(len(all_commit_data.dtype.descr)):

        desc = all_commit_data.dtype.descr[i]
        column_name = desc[0]

        # The date column is used as the X axis, and doesn't need to be graphed
        if column_name == "date":
            continue

        data = all_commit_data[column_name]
        last_commit_count = data[-1]

        # Remove all the records with the same commit count as the last record
        # That way the line stops when the author stops making commits
        truncated_data = numpy.delete(data, numpy.where(data == last_commit_count))

        # Except we just removed the last record, better put that back
        truncated_data = numpy.append(truncated_data, last_commit_count)

        # Shrink the size of the date list to match the data list
        truncated_dates = numpy.resize(all_commit_data.date, truncated_data.shape)

        line_colour = color_sequence[i % len(color_sequence)]

        user_labels.append(
            {
                "username": column_name,
                "commits": last_commit_count,
                "last_date": truncated_dates[-1],
                "colour": line_colour,
            }
        )

        line = plt.plot(truncated_dates, truncated_data, lw=2.5, color=line_colour)

    for label in user_labels:
        plt.text(
            label["last_date"],
            label["commits"],
            " {0} ({1})".format(label["username"], label["commits"]),
            fontsize=8,
            color=label["colour"],
        )

    plt.savefig(commits_per_user_svg_path, bbox_inches="tight")


def build_option_parser():
    opt_parser = OptionParser()
    opt_parser.add_option(
        "-u", "--username", dest="username", help="the user to connect as"
    )

    opt_parser.add_option(
        "-p", "--password", dest="password", help="the password of the user"
    )

    opt_parser.add_option(
        "-d",
        "--download",
        action="store_true",
        dest="download_files",
        help="downloads the log file even if it already exists",
    )

    opt_parser.add_option(
        "-l",
        "--lines",
        action="store_true",
        dest="count_lines",
        help="count the number of line changes in each diff",
    )

    return opt_parser


if __name__ == "__main__":
    parser = build_option_parser()
    (options, args) = parser.parse_args()

    svn_url = args[0]

    if options.download_files:

        log_entries = get_svn_log(svn_url, options.username, options.password)

        if options.count_lines:
            print_commit_total_per_user(log_entries, svn_url, True)
        else:
            print_commit_total(log_entries)
            print_commit_total_per_user(log_entries, svn_url, False)

    chart_commit_total()
    chart_commit_total_per_user()
