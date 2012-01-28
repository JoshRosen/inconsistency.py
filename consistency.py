import sys
import string
from collections import defaultdict
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.tokenize.punkt import PunktSentenceTokenizer
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


def is_uppercase(x):
    return x and x[0] in string.uppercase


def canonicalize(ngram):
    """
    Produce dictionary keys for ngrams, so that potential inconsistencies
    map to the same key.
    """
    if ngram is str:
        ngram = (ngram, )
    return "".join(x.lower() for x in ngram).strip(",. ").replace("-", "")


def consistency(s):
    """
    >>> m = consistency("Batch gradient descent algorithms "
    ...                 "... in Batch Gradient Descent ...")
    >>> [(x, sorted(y)) for (x, y) in m.items() if len(y) >= 2]
    [('gradientdescent', ['Gradient Descent', 'gradient descent'])]

    >>> m = consistency("This sentence's first word appears uncapitalized in "
    ...                 "this sentence.  Hadoop should be capitalized as "
    ...                 " Hadoop, not hadoop.")
    >>> [(x, sorted(y)) for (x, y) in m.items() if len(y) >= 2]
    [('hadoop', ['Hadoop', 'hadoop'])]

    If the second word of a sentence is capitalized, it will be be considered
    if and only if the following word is uncapitalized:

    >>> m = consistency("The Operator may be replaced by another operator")
    >>> [(x, sorted(y)) for (x, y) in m.items() if len(y) >= 2]
    [('operator', ['Operator', 'operator'])]
    >>> m = consistency("The Operator Descriptor describes an operator")
    >>> [(x, sorted(y)) for (x, y) in m.items() if len(y) >= 2]
    []

    """
    sent_tokenizer = PunktSentenceTokenizer()
    tokenizer = TreebankWordTokenizer()
    mappings = defaultdict(set)

    sentences = sent_tokenizer.tokenize(s)
    for sent in sentences:
        tokens = tokenizer.tokenize(sent)
        # The capitalization of individual words poses a problem: we would like
        # to detect cases where names are miscapitalized (e.g. hadoop instead
        # of Hadoop), but we want to avoid false-positives due to capitalized
        # words that start a sentence or are part of capitalized phrases.

        # Therefore, we only add mappings for capitalized unigrams if they do
        # not start a sentence and are not adjacent to other capitalized words.
        for i in range(1, len(tokens)):
            prev_token = tokens[i-1]
            token = tokens[i]
            if i+1 < len(tokens):
                next_token = tokens[i+1]
            else:
                next_token = ""
            adjacent_uppercase = (i > 1 and is_uppercase(prev_token)) or \
                                 is_uppercase(next_token)
            if is_uppercase(token) and adjacent_uppercase:
                continue
            norm = canonicalize(token)
            source = token.strip(",. ")
            mappings[norm].add(source)
        # Map normalized ngrams
        for x in range(2, 10):
            for ngram in ingrams(tokens, x):
                norm = canonicalize(ngram)
                source = " ".join(ngram).strip(",. ")
                if len(source.split()) == x:
                    mappings[norm].add(source)

    # For normalized forms with mutiple values, filter out longer ngrams that
    # may be covered by shorter ones or that are trivial capitalization
    # differences
    for (key, values) in mappings.items():
        if len(values) > 1:
            for (a, b) in bigrams(values):
                (x, y) = [" ".join(x) for x in strip_common_fixes(a.split(),
                                                                  b.split())]
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
