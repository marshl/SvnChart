from optparse import OptionParser
from subprocess import call, Popen
import subprocess
import xml.etree.ElementTree
import os.path;
import dateutil.parser
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec
from matplotlib.cbook import get_sample_data
import numpy
import random

parser = OptionParser()
parser.add_option("-u", "--username", dest="username",
                  help="the user to connect as")

parser.add_option("-p", "--password", dest="password",
                  help="the password of the user")

parser.add_option("-d", "--download", action="store_true", dest="download",
                  help="Whether to download the file or not")


(options, args) = parser.parse_args();

def main():
    if options.download or not os.path.isfile("svn_log.xml"):
       downloadLogFile()

    log_entries = parseLogFile()

    printCommitTotalByWeek(log_entries)
    chartCommitTotalByWeek()

    printCommitPerUserByWeek(log_entries)
    chartCommitTotalPerUserByWeek()


class logEntry:

    def __init__(self, date, author):
        self.date = date
        self.author = author

def downloadLogFile():
    
    process = subprocess.Popen( ["svn", "log", args[0], "--xml", "--username", options.username, "--password", options.password], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = process.communicate()
    errcode = process.returncode

    with open("svn_log.xml", "wb") as f:
        f.write(out)

def parseLogFile():
    
    log_entries = []
    e = xml.etree.ElementTree.parse('svn_log.xml').getroot()

    # Only find the log entries that have an author
    for entry in e.findall('logentry[author]'):
        date = dateutil.parser.parse( entry.find('date').text )
        author = entry.find('author').text
        l = logEntry( date, author )
        log_entries.append( l )
    

    log_entries = sorted( log_entries, key=lambda entry: entry.date )
    return log_entries


def printCommitTotalByWeek(log_entries):
    first_date = log_entries[0].date
    last_date = log_entries[-1].date

    with open('commits_total.csv', 'w+') as f:
        f.write( "date,commits\n" )

        current_date = first_date
        commit_count = 0

        for entry in log_entries:
            if entry.date > current_date:
                current_date += timedelta( weeks = 1 )
                date_as_string = str(current_date)
                f.write( date_as_string + "," + str(commit_count) + "\n" )
    
            commit_count += 1

def printCommitPerUserByWeek(log_entries):
    first_date = log_entries[0].date
    last_date = log_entries[-1].date

    current_date = first_date
    

    user_commit_count = dict()
    
    # Find all unique author names (there has to be a better way to do this)
    for entry in log_entries:
        if entry.author not in user_commit_count:
            user_commit_count[entry.author] = 0

    with open('commits_per_user.csv', 'w+') as f:
        f.write('date,')
        f.write( ','.join( user_commit_count.keys() ) + "\n" )

        for entry in log_entries:
            if entry.date > current_date:
                current_date += timedelta( weeks = 1 )            
                f.write( str(current_date) )
            
                for key in user_commit_count.keys():
                    f.write( ',' + str( user_commit_count[key] ) )

                f.write("\n")
    
            user_commit_count[entry.author] += 1

def chartCommitTotalByWeek():
    commit_data = csv2rec('commits_total.csv')
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    line = plt.plot(commit_data.date,
                    commit_data['commits'],
                    lw=2.5,
                    color='#1f77b4')

    plt.savefig('commits_total.svg', bbox_inches='tight')

def chartCommitTotalPerUserByWeek():

    commit_data = csv2rec('commits_per_user.csv')
    fig, ax = plt.subplots(1, 1, figsize=(30, 22.5))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    
    column_count = len(commit_data.dtype.descr)
    last_date = commit_data['date'][-1]

    for i in commit_data.dtype.descr:
        column_name = i[0]

        if column_name == 'date':
            continue

        d = commit_data[column_name]
        
        randColor = "#%06x" % random.randint(0, 0xFFFFFF)

        line = plt.plot(commit_data.date,
                    d,
                    lw=2.5,
                    color=randColor)

        y_pos = commit_data[column_name][-1] - 0.5
        user_commit_count = d[-1]
        plt.text(last_date, y_pos, "{user} ({commits})".format( user=column_name, commits=user_commit_count ), fontsize=8, color=randColor)

    plt.savefig('commits_per_user.svg', bbox_inches='tight')

if __name__=="__main__":
   main()