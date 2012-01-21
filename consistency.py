import sys
from collections import defaultdict
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.util import ingrams, bigrams


def strip_common_fixes(a, b):
    """
    >>> strip_common_fixes("of machine learning tasks".split(),
    ...                    "of machine-learning tasks".split())
    (['machine', 'learning'], ['machine-learning'])
    """
    x = a[:]
    y = b[:]
    while len(x) > 0 and len(y) > 0 and x[0] == y[0]:
        del x[0]
        del y[0]
    while len(x) > 0 and len(y) > 0 and x[-1] == y[-1]:
        del x[-1]
        del y[-1]
    return (x, y)


def lower_case(x):
    """
    >>> lower_case("Apple")
    'apple'
    >>> lower_case("Batch Gradient")
    'Batch Gradient'
    """
    if len(x.split()) == 1:
        return x[0].lower() + "".join(x[1:])
    else:
        return x


def consistency(s):
    """
    >>> m = consistency("Batch gradient descent algorithms "
    ...                 "... in Batch Gradient Descent ...")
    >>> [(x, sorted(y)) for (x, y) in m.items() if len(y) >= 2]
    [('gradientdescent', ['Gradient Descent', 'gradient descent'])]
    """
    tokenizer = TreebankWordTokenizer()
    tokens = tokenizer.tokenize(s)
    mappings = defaultdict(set)
    # Map normalized ngrams
    for x in range(1, 10):
        for ngram in ingrams(tokens, x):
            norm = "".join(x.lower() for x in ngram).strip(",. ").replace("-", "")
            source = " ".join(ngram).strip(",. ")
            mappings[norm].add(source)
    # For normalized forms with mutiple values, filter out longer ngrams that
    # may be covered by shorter ones or that are trivial capitalization differences
    for (key, values) in mappings.items():
        if len(values) > 1:
            for (a, b) in bigrams(values):
                (x, y) = [" ".join(x) for x in strip_common_fixes(lower_case(a).split(),
                                                                  lower_case(b).split())]
                if (x, y) != (a, b):
                    del mappings[key]
                    break
        else:
            del mappings[key]
    return mappings


def _test():
    import doctest
    doctest.testmod()


def main():
    mappings = consistency(open(sys.argv[1]).read())
    # Output the mappings
    for (key, values) in sorted(mappings.items()):
        print key
        for value in values:
            print "    %s" % value


if __name__ == "__main__":
    main()
