#!/usr/local/bin/python3.6
"""csv_to_csvs the awesome way of conditionally spiting large csv files into smaller ones
Usage:
  csv_to_csvs.py split <file> cons <cons> [--case_sensitive \
(--use_bound | --use_bound_limit=<limit>) \
--use_ext=<ext> --pre_pend --out_csv_delim=<delim> --use_fn_delim=<delim> \
--no_column_labels --use_out_folder=<folder_name> --use_skip_list=<token_list>]
  csv_to_csvs.py -h | --help
  csv_to_csvs.py --version
Arguments:
    -h --help                       Show this message.
    --version                       Show version number.
    --case_sensitive                Case sensitive in labels
    --use_bound_limit=<limit>       Use a specific upper bound.
    --use_bound                     Use the bound  [default: 1000].
    --use_ext=<ext>                 Use custom outfile extension  [default: .csv].
    --pre_pend                      Enable prepend of strings with the csv label.
    --no_column_labels              Do not put column labels in created files first line.
    --use_fn_delim=<delim>          Use a specific delimiter for filenames [default: _].
    --out_csv_delim=<delim>         Use a specific delimiter for out files [default: ,].
    --in_csv_delim=<delim>          Use a specific delimiter for input file [default: ,].
    --use_skip_list=<token_list>    Use a skip list [default: [null]].
    --use_out_folder=<folder_name>  Use this to dump our files to [default: out].
"""
import csv
import os
from docopt import docopt

# iteration bound
high_bound = 100
# filename delimiter
fn_delim = "_"
# output files csv delimiter
out_csv_delim = ","
# input file csv delimiter
in_csv_delim = ","
# created files extension
fn_ext = ".csv"
# folder to place the results
out_folder = "out"
# first line
first_csv_line = ""
# first line length
max_line_tokens = 0

# the constraints which should be on the first line
cons = []
# enable case sensitive insertion
case_sensitive = False
# enable pre-pend by the constraint name
pre_pend = False
# stick initial line
put_column_labels = True
# enable if we want to have iteration bound
use_iteration_bound = False
# directory of execution
dir_path = os.path.dirname(os.path.realpath(__file__))
# count skip errors
skip_error_count = 0

# constraint key -> name map
cons_strings = {}
# each constraint dictionary
cons_dicts = []
# filename -> stream hash
file_streams = {}
# filename -> csv writer stream
csv_writers = {}
# skip-list
skip_token_list = ["null"]
# input file fd
par_csv = None
# input file csv stream
csv_stream = None


# Function to translate docopts -> program arguments
def parse_arguments():
    global high_bound
    global fn_delim
    global out_csv_delim
    global in_csv_delim
    global fn_ext
    global out_folder
    global cons
    global case_sensitive
    global pre_pend
    global put_column_labels
    global use_iteration_bound
    global skip_token_list

    # parse argument list
    arg_dict = docopt(__doc__, version='0.5b1')

    if arg_dict["--use_bound"]:
        use_iteration_bound = True

    if arg_dict["--use_bound_limit"]:
        use_iteration_bound = True
        high_bound = arg_dict["--use_bound_limit"]

    if arg_dict["--case_sensitive"]:
        case_sensitive = True

    if arg_dict["--no_column_labels"]:
        put_column_labels = False

    if arg_dict["--pre_pend"]:
        pre_pend = True

    if arg_dict["--use_skip_list"]:
        skip_token_list = \
            [m.strip() for m in arg_dict["--use_skip_list"][1:-1].split(",")]

    # build up constraints list
    cons = list(map(int, arg_dict["<cons>"][1:-1].split(",")))

    # properties that are used in general w/e the case
    fn_delim = arg_dict["--use_fn_delim"]
    out_csv_delim = arg_dict["--out_csv_delim"]
    in_csv_delim = arg_dict["--in_csv_delim"]
    fn_ext = arg_dict["--use_ext"]
    out_folder = arg_dict["--use_out_folder"]

    print(high_bound)
    # print(arg_dict)


# The main stub for our utility
def csv_stub():
    # parse command line arguments
    parse_arguments()

    # open the csv file
    open_csv()

    # create the constraints
    build_constraints()

    # split the file to children based on constraints
    perform_splitting()
    # perform closing stuff.
    cleanup()


# Open the csv file and create the csv reader stream
def open_csv():
    global par_csv
    global in_csv_delim
    global first_csv_line
    global max_line_tokens
    global csv_stream

    par_csv = open('data/Phones_accelerometer.csv', 'r')
    csv_stream = csv.reader(par_csv, delimiter=in_csv_delim)
    first_csv_line = csv_stream.__next__()
    max_line_tokens = len(first_csv_line)
    print("INFO -- Using data-out folder: {0}"
          .format(out_folder))


# Perform clean up tasks
def cleanup():
    global par_csv
    global file_streams
    global skip_error_count
    print("INFO -- Splitting done, created {0} child files"
          .format(len(file_streams)))
    print("INFO -- Skip errors where: {0}"
          .format(skip_error_count))
    # close the streams
    for k, fs in file_streams.items():
        fs.close()

    # close the csv
    par_csv.close()


# Function to perform the CSV splitting
def perform_splitting():
    global csv_stream
    global high_bound
    global use_iteration_bound
    if not use_iteration_bound:
        # we don't have a bound to enforce, just run through.
        for row in csv_stream:
            # write the row to the respective csv stream
            write_row(row)
    else:
        # zip the value to force an upper bound
        for zipped_row in zip(range(high_bound), csv_stream):
            # write the row to the respective csv stream
            write_row(zipped_row[1])


# Attempt to write the row to its respective csv stream
def write_row(row):
    global max_line_tokens
    # sanity check for values
    if len(row) > max_line_tokens:
        print("ERROR -- Irregularly sized line found, skipping")
        return
    # grab the filename
    csv_writer = cons_fn(row)
    # write the line to the csv stream
    if csv_writer is not None:
        csv_writer.writerow(row)


# Build the particular constraints and their
# dictionaries to track each particular file
# creation.
def build_constraints():
    global cons_strings
    global cons_dicts
    for c in cons:
        if c < max_line_tokens:
            # add the particular string
            cons_strings[c] = first_csv_line[c]
            # create a dictionary for particular constraint
            cons_dicts.append({})
        else:
            print("ERROR -- first line constraint index {0} out of bounds".format(c))


# Construct the filename per line to check if we need
# to create another csv stream, otherwise return the
# already existing one.
def cons_fn(row):
    global cons_dicts
    global file_streams
    global csv_writers
    global skip_error_count
    # build up the filename
    fn = ""
    for i, d in enumerate(cons_dicts):
        # skip null tuples
        if [row[cons[i]].lower() if not case_sensitive else row[cons[i]]] \
                in skip_token_list:
            skip_error_count += 1
            # print("ERROR -- Skip list matched value found: ({0}), skipping..."
            #      .format(row[cons[i]].lower()))
            return None

        if pre_pend:
            fn = fn + cons_strings[cons[i]] + fn_delim + \
                 row[cons[i]] + fn_delim
        else:
            fn = fn + row[cons[i]] + fn_delim

        if row[cons[i]] not in d:
            d[row[cons[i]]] = 0

    fn = fn[:-1] + fn_ext

    # create a new file
    if fn not in file_streams:
        print("INFO -- Opening csv stream at: {0}".format(fn))
        f = create_file(fn)
        file_streams[fn] = f
        r = csv.writer(f, delimiter=out_csv_delim)
        csv_writers[fn] = r
        r.writerow(first_csv_line)
    # finally return the file stream to append
    return csv_writers[fn]


# Create a file while also creating the required subdirectories
def create_file(fn):
    fp = dir_path + "/" + out_folder + "/" + fn
    # print(fn)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return open(fp, "w")


if __name__ == '__main__':
    csv_stub()
