# CSV to CSVs

This is a simple utility that *conditionally* splits a huge CSV 
file into smaller ones given some constraints. This is useful 
in many use-cases, but mine was that I wanted to examine/modify 
portions of the CSV file while not having to re-parse it or 
load it again in memory.
 
Remember, storing on a disk is *much* cheaper than just 
putting everything in RAM.
  
# Features
  
This command line utility has a lot of options that you can customize the splitting
based on your preferences. It supports the following things:

 * Splitting based on *multiple* column constraints
 * Use an upper bound for iterations
 * Use custom extension for your output files (different than `.csv``)
 * Option to enable column name prepend against arguments.
 * Option to suppress the first line naming (MatLab users rejoice! no more row offset!)
 * Use different delimiters for input/output files
 * Use a skip list that enables you to skip rows based on this
  
# Quick syntax overview

The general syntax of the command is this:

```
./csv_to_csvs.py split file.csv cons "[1, 2...,n]"
```

Where `file.csv` the file you want to split and the `cons` being the constraint list you
want to have when you split the file; the constraint list has the following format:

```
"[idx1, idx2,...,idxn]"
```

# Examples

It's a string, so it must be enclosed in `"""`, and have a list of column label indexes
in the order of enforcement, thus `"[0, 1]""` and `"[1, 0]"` are not the same.


Let's say you have the following column labels in csv file:

```
Index,Arrival_Time,Creation_Time,x,y,z,User,Model,Device,gt
```

Now say you want to get file splits based on each User, what you could do is:

```
./csv_to_csvs.py split myfile.csv cons "[6]"
```

Now you would get a number of csv files containing each information respective to each
*unique* user found during execution.

Now let's take it a step further, say you want to create the csv files based on each
Device and User, that could the achieved like so:

```
./csv_to_csvs.py split myfile.csv cons "[6]"
```

# License
 
Unless otherwise noted, this work is licensed under  the terms 
and conditions of GPLv3.