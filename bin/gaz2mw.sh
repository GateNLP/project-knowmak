#!/bin/bash

# read from stdin and output everything from column 1 that has a space

cat | cut -f 1 | sort -u | grep -P '\s' 
