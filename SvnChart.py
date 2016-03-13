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
    if options.download or not os.path.isfile("log.xml"):
       downloadLogFile()

    log_entries = parseLogFile()

    #printCommitTotalByWeek(log_entries)
    #chartCommitTotalByWeek()
    printCommitPerUserByWeek(log_entries)
    chartCommitTotalPerUserByWeek()


class logEntry:

    def __init__(self, date, author):
        self.date = date
        self.author = author

def downloadLogFile():
     #print("username: " + options.username + " password: " + options.password )
    process = subprocess.Popen( ["svn", "log", args[0], "--xml", "--username", options.username, "--password", options.password], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = process.communicate()
    errcode = process.returncode

    f = open("log.xml", "wb")
    f.write(out)


def parseLogFile():
    
    log_entries = []
    e = xml.etree.ElementTree.parse('log.xml').getroot()

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

    current_date = first_date
    f = open('commits_total_by_week.csv', 'w+')
    f.write( "date,commits\n" )

    commit_count = 0

    for entry in log_entries:
        if entry.date > current_date:
            current_date += timedelta( weeks = 1 )
            date_as_string = str(current_date)
            f.write( date_as_string + "," + str(commit_count) + "\n" )
            commit_count = 0
    
        commit_count += 1

def printCommitPerUserByWeek(log_entries):
    first_date = log_entries[0].date
    last_date = log_entries[-1].date

    current_date = first_date
    f = open('commits_total_user_by_week.csv', 'w+')

    user_commit_count = dict()
    
    #There has to be a better way to do 
    for entry in log_entries:
        if entry.author not in user_commit_count:
            user_commit_count[entry.author] = 0

    f.write('date,')
    f.write( ','.join( user_commit_count.keys() ) + "\n" )

    for entry in log_entries:
        if entry.date > current_date:
            current_date += timedelta( weeks = 1 )
            date_as_string = str(current_date)#current_date.strftime("%B %d %Y")
            #f.write( date_as_string + "," + str(commit_count) + "\n" )

            f.write( date_as_string )
            #for key, value in user_commit_count.items():
            #    f.write( value
            #v = user_commit_count.values()
            #f.write( ','.join( str(x) for x in user_commit_count.values() ) + "\n" )
            for key in user_commit_count.keys():
                f.write( ',' + str( user_commit_count[key] ) )
            f.write("\n")
            #for key in user_commit_count.keys():
            #    user_commit_count[key] = 0
    
        user_commit_count[entry.author] += 1


def chartCommitTotalByWeek():
    commit_data = csv2rec('commits_total_by_week.csv')
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    #majors = ['Total Commits']


    #for rank, column in enumerate(majors):
        # Plot each line separately with its own color.
    #column_rec_name = column.replace('\n', '_').replace(' ', '_').lower()

    line = plt.plot(commit_data.date,
                    commit_data['commits'],
                    lw=2.5,
                    color='#1f77b4')

    # Add a text label to the right end of every line. Most of the code below
    # is adding specific offsets y position because some labels overlapped.
    #y_pos = gender_degree_data[column_rec_name][-1] - 0.5

   # if column in y_offsets:
    #    y_pos += y_offsets[column]

    # Again, make sure that all labels are large enough to be easily read
    # by the viewer.
    #plt.text(2011.5, y_pos, column, fontsize=14, color=color_sequence[rank])

    # Make the title big enough so it spans the entire plot, but don't make it
    # so big that it requires two lines to show.

    # Note that if the title is descriptive enough, it is unnecessary to include
    # axis labels; they are self-evident, in this plot's case.
    #plt.title('Percentage of Bachelor\'s degrees conferred to women in '
    #          'the U.S.A. by major (1970-2011)\n', fontsize=18, ha='center')

    # Finally, save the figure as a PNG.
    # You can also save it as a PDF, JPEG, etc.
    # Just change the file extension in this call.
    plt.savefig('commits_total_by_week.png', bbox_inches='tight')

def chartCommitTotalPerUserByWeek():
    commit_data = csv2rec('commits_total_user_by_week.csv')
    fig, ax = plt.subplots(1, 1, figsize=(30, 22.5))
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    #majors = ['Total Commits']
    #a = commit_data.dtype
    #z = a.shape
    length = 0
    #for x in numpy.ndenumerate( commit_data ):
    #    length = len(x[1]) - 1
    #    break # ugh

        #print( x + ':' + y )

    #length = len( (numpy.ndenumerate(commit_data))[1] )
    #for x in numpy.ndenumerate(commit_data):
    #    print( x + ":" + y )

   # s = commit_data.size
    #d = commit_data.names

    #for rank, column in enumerate(majors):
        # Plot each line separately with its own color.
    #column_rec_name = column.replace('\n', '_').replace(' ', '_').lower()

    #d = commit_data.dtype
    #e = d.descr

    column_count = len(commit_data.dtype.descr)
    #first_date = commit_data['date'][0]
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
        #print(y_pos)
        #print(len(commit_data.dtype.descr))
        # Again, make sure that all labels are large enough to be easily read
        # by the viewer.
        user_commit_count = d[-1]
        plt.text(last_date, y_pos, "{user} ({commits})".format( user=column_name, commits=user_commit_count ), fontsize=8, color=randColor)

    # Add a text label to the right end of every line. Most of the code below
    # is adding specific offsets y position because some labels overlapped.
    #y_pos = gender_degree_data[column_rec_name][-1] - 0.5

   # if column in y_offsets:
    #    y_pos += y_offsets[column]

    # Again, make sure that all labels are large enough to be easily read
    # by the viewer.
    #plt.text(2011.5, y_pos, column, fontsize=14, color=color_sequence[rank])

    # Make the title big enough so it spans the entire plot, but don't make it
    # so big that it requires two lines to show.

    # Note that if the title is descriptive enough, it is unnecessary to include
    # axis labels; they are self-evident, in this plot's case.
    #plt.title('Percentage of Bachelor\'s degrees conferred to women in '
    #          'the U.S.A. by major (1970-2011)\n', fontsize=18, ha='center')

    # Finally, save the figure as a PNG.
    # You can also save it as a PDF, JPEG, etc.
    # Just change the file extension in this call.
    plt.savefig('commits_total_by_week.png', bbox_inches='tight')

if __name__=="__main__":
   main()