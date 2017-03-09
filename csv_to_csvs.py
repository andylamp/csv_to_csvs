import csv
import os

# iteration bound
high_bound = 100
# filename delimiter
fn_delim = "_"
# created files extension
fn_ext = ".csv"
# folder to place the results
out_folder = "out"
# first line
first_csv_line = ""
# first line length
max_line_tokens = 0

# the constraints which should be on the first line
cons = [6, 8, 9]
# enable case sensitive insertion
case_sensitive = False
# enable pre-pend by the constraint name
pre_pend = False
# stick initial line
init_line_stick = True
# enable if we want to have iteration bound
use_iteration_bound = True
# directory of execution
dir_path = os.path.dirname(os.path.realpath(__file__))

# constraint key -> name map
cons_strings = {}
# each constraint dictionary
cons_dicts = []
# filename -> stream hash
file_streams = {}
# filename -> csv writer stream
csv_writers = {}


# The main stub for our utility
def csv_stub():
    global first_csv_line
    global max_line_tokens

    par_csv = open('data/Phones_accelerometer.csv', 'r')
    r = csv.reader(par_csv)
    first_csv_line = r.__next__()
    max_line_tokens = len(first_csv_line)
    print("INFO -- Using data-out folder: {0}"
          .format(out_folder))

    # create the constraints
    build_constraints()

    # print the extracted constraints
    # print(cons_strings)

    # split the file to children based on constraints
    perform_splitting(r)
    # perform closing stuff.
    cleanup(par_csv)


# Perform clean up tasks
def cleanup(par_csv):
    global file_streams
    print("INFO -- Splitting done, created {0} child files"
          .format(len(file_streams)))
    # close the streams
    for k, fs in file_streams.items():
        fs.close()

    # close the csv
    par_csv.close()


# Function to perform the CSV splitting
def perform_splitting(csv_reader):
    if not use_iteration_bound:
        # we don't have a bound to enforce, just run through.
        for row in csv_reader:
            # write the row to the respective csv stream
            write_row(row)
    else:
        # zip the value to force an upper bound
        for zipped_row in zip(range(high_bound), csv_reader):
            # write the row to the respective csv stream
            write_row(zipped_row[1])


# Attempt to write the row to its respective csv stream
def write_row(row):
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
    # build up the filename
    fn = ""
    for i, d in enumerate(cons_dicts):
        # skip null tuples
        if row[cons[i]].lower() == "null":
            print("ERROR -- Null value found, skipping...")
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
        r = csv.writer(f)
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
