# bugreport
This tool generates bug reports for bugs in a given project or bugs reported in launchpad.net since 'YYYY-MM-DD'. You can generate a quick summary or a summary with details on each bug catagorized by importance (Critical, High, etc).

## For full list of options use:
./bugreport -h 

# How to invoke the tool:
## Summary only:
You can generate a summary report for given project or all bugs in launchpad.net since 'YYYY-MM-DD'
1. Bug report for 'project' since 'YYYY-MM-DD'

   ./bugreport.py -p project -d YYYY-MM-DD 

2. Bug report for 'project' since 'YYYY-MM-DD' output to html file.

   ./bugreport.py -p project -d YYYY-MM-DD -o outfile

3. Bug report for all bugs in launchpad.net since 'YYYY-MM-DD'

   ./bugreport.py -d YYYY-MM-DD

4. Bug report for all bugs in launchpad.net since 'YYYY-MM-DD' for given tags

   ./bugreport.py -d YYYY-MM-DD -t tag1,tag2

5. Bug report for all bugs in launchpad.net since 'YYYY-MM-DD' for bug status in "New,Confirmed,Triaged,In Progress,Incomplete" and tags in tag1,tag2

   ./bugreport.py -d YYYY-MM-DD -t tag1,tag2 -s "New,Confirmed,Triaged,In Progress,Incomplete"

## Summary with details on bugs:
For each example above use -v option to generate bug report with details on each bug, use -o option to output to html file.
   ./bugreport.py -d YYYY-MM-DD -v -o outfile

## How to create PDF:
1. Open the outputfile.html in a web browser.
2. Print and save as PDF.
