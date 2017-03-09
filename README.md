# CSV to CSVs

This is a simple utility that *conditionally* splits a huge CSV 
file into smaller ones given some constraints. This is useful 
in many use-cases, but mine was that I wanted to examine/modify 
portions of the CSV file while not having to re-parse it or 
load it again in memory.
 
Remember, storing on a disk is *much* cheaper than just 
putting everything in RAM.
  
# Notes on usage
 
Right now every options has to be edited from source, but
in a future iteration (soon-ish!) you will be able to use
command line to give arguments.
 
# License
 
Unless otherwise noted, this work is licensed under  the terms 
and conditions of GPLv3.