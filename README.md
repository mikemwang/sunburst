# sunburst

*preview of test.pdf, view test.pdf for full resolution*
![alt-text](test.png)

*for an explanation of what a sunburst diagram is, [here's a good overview](http://www.datavizcatalogue.com/methods/sunburst_diagram.html)*

# What's this?
A side project I started while at my internship with Tagup. I wrote some Python to generate sunburst diagrams using lists of words as the data set, so the innermost ring is divided proportionally based on which first letters were most commonly seen, the ring after that contains the letters following the first, and so on. Eventually the word terminates in a red section, which spells out the full word and indicates how many times the word showed up in the data set.

In this version the data set for the diagram on the left is the code from the Python files used to generate that diagram. While running, the Python code records the lines that were executed, and this record is used as the data set for the diagram on the right. 

Printed out and now hanging in my room!

![alt-text](photo2.jpg)

# How to use
Still very unpolished, for now running run.py with Python3 (won't work with 2!) will generate a pdf of the sunburst diagram using the Python source code as the set of data. Some settings can be specified in the config.yaml file but I didn't really test those so they may not work the way you think they do.

# Todos
- Refactor code for better efficency (had to get it out quickly while I still had access to a large scale printer)
- Put in comments soon before I forget why I did what I did
- Revamp the interface so that the code can work with other types of data, not just words
