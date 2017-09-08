# bugreport
This tool generates bug reports for bugs in a given project or bugs reported in launchpad.net since 'start date'. You can generate a quick summary or a summary with details on each bug catagorized by importance (Critical, High, etc).

## For full list of options use:
./bugreport -h 

# How to invoke the tool:
## Summary only:
You can generate a summary report for given project or all bugs in launchpad.net since 'start date'
1. Bug report for 'project' since 'start date'

   ./bugreport.py -p project -d start date 

2. Bug report for 'project' since 'start date' output to html file.

   ./bugreport.py -p project -d start date -o outfile

3. Bug report for all bugs in launchpad.net since 'start date'

   ./bugreport.py -d start date

4. Bug report for all bugs in launchpad.net since 'start date' for given tags

   ./bugreport.py -d start date -t sts,onsite

## Summary with details on bugs:
For each example above use -v option to generate bug report with details on each bug, use -o option to output to html file.
   ./bugreport.py -d start date -v -o outfile

## How to create PDF:
1. Open the outputfile.html in a web browser.
2. Print and save as PDF.
