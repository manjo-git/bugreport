How to invoke the tool:
1. Summary only:
./bugreport.py -p <project> -d <start date> 
Will generate a summary bug report based on importance (ie Critical, High etc).

2. Summary with bug details:
./bugreport.py -p <project> -d <start date> -v 
Will generate a summary bug report as above, and detailed report for each bug.

3. Summary for bugs by importance (high, medium, low etc)
./bugreport.py -p <project> -d <start date> -i high,medium,low
Please do not use spaces in comma separated list.

How to create HTML files:
1. ./bugreport.py -p ubuntu-power-systems -d 2017-08-01 -o out.t2t
Where out.t2t is an ascii text file, you could use the -v option to generate 
a full report.
2. txt2tags -C htmlconvert.conf -t html out.t2t
This will generate out.html.

How to create PDF:
1. Open the out.html in a web browser.
2. Print and save as PDF.
