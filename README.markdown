Introduction
------------

This script finds inconsistently-capitalized-or-hyphenated phrases in documents.

For example, say `document.txt` contains both "machine-learning" and "Machine learning".

Then, `python inconsistency.py document.txt` will output

    machinelearning
        machine-learning
        Machine learning

For TeX/LaTeX users, [detex](http://www.ctan.org/tex-archive/support/detex) can be used to generate a plain-text file for use with this script.

This script depends on [NLTK](http://www.nltk.org/) to split documents into sentences.


Related software
----------------

[PerfectIt](http://www.intelligentediting.com) is a commercial consistency checker that has many more features than this script.

[style-check.rb](http://www.cs.umd.edu/~nspring/software/style-check-readme.html) is a style-checker for English prose that also offers tips on LaTeX formatting. [GNU diction](http://www.gnu.org/software/diction/) is similar.
