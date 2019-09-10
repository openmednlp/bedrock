"""
Split German compound words
"""

__author__ = 'don.tuggener@gmail.com'

import re
import sys
from bedrock.libs.CharSplit.ngram_probs import suffix, infix, prefix


def split_compound(word: str):
    """
    Return list of possible splits, best first
    :param word: Word to be split
    :return: List of all splits
    """

    word = word.lower()

    # If there is a hyphen in the word, return part of the word behind the last hyphen
    if '-' in word:
        return [[1., word.title(), re.sub('.*-', '', word.title())]]
    
    scores = [] # Score for each possible split position
    # Iterate through characters, start at forth character, go to 3rd last
    for n in range(3, len(word)-2):

        pre_slice = word[:n]
        
        # Cut of Fugen-S
        if pre_slice.endswith('ts') or pre_slice.endswith('gs') or pre_slice.endswith('ks') \
                or pre_slice.endswith('hls') or pre_slice.endswith('ns'):
            if len(word[:n-1]) > 2: pre_slice = word[:n-1]

        # Start, in, and end probabilities
        pre_slice_prob = []
        in_slice_prob = []
        start_slice_prob = []
        
        # Extract all ngrams
        for k in range(len(word)+1, 2, -1):
        
            # Probability of first compound, given by its ending prob
            if pre_slice_prob == [] and k <= len(pre_slice):
                end_ngram = pre_slice[-k:]  # Look backwards
                pre_slice_prob.append(suffix.get(end_ngram, -1))    # Punish unlikely pre_slice end_ngram
                    
            # Probability of ngram in word, if high, split unlikely
            in_ngram = word[n:n+k]
            in_slice_prob.append(infix.get(in_ngram, 1)) # Favor ngrams not occurring within words
                                  
            # Probability of word starting
            if start_slice_prob == []:
                ngram = word[n:n+k]
                # Cut Fugen-S
                if ngram.endswith('ts') or ngram.endswith('gs') or ngram.endswith('ks') \
                        or ngram.endswith('hls') or ngram.endswith('ns'):
                    if len(ngram[:-1]) > 2:
                        ngram = ngram[:-1] 
                start_slice_prob.append(prefix.get(ngram, -1))

        if pre_slice_prob == [] or start_slice_prob == []: continue
        
        start_slice_prob = max(start_slice_prob)
        pre_slice_prob = max(pre_slice_prob)    # Highest, best preslice
        in_slice_prob = min(in_slice_prob)      # Lowest, punish splitting of good ingrams                               
        score = start_slice_prob - in_slice_prob + pre_slice_prob
        scores.append([score, word[:n].title(), word[n:].title()])

    scores.sort(reverse=True)
    if scores == []:
        scores=[ [0, word.title(), word.title()] ]
    return sorted(scores, reverse = True)


def germanet_evaluation(print_errors: bool=False):
    """ Test on GermaNet compounds from http://www.sfs.uni-tuebingen.de/lsd/compounds.shtml """
    cases, correct = 0, 0
    for line in open('split_compounds_from_GermaNet13.0.txt','r').readlines()[2:]:
        cases += 1
        sys.stderr.write('\r'+str(cases))
        sys.stderr.flush()
        line = line.strip().split('\t')
        if not len(line) == 3:
            continue   # A few corrupted lines
        split_result = split_compound(line[0])
        if split_result != []:
            if split_result[0][2] == line[2]:
                correct += 1
            elif print_errors:
                print(line, split_result)
        if cases % 10000 == 0: print(' Accuracy (' + str(correct) + '/' + str(cases) + '): ', 100*correct/cases)
    print(' Accuracy (' + str(correct) + '/' + str(cases) + '): ', 100*correct/cases)


if __name__ == '__main__':
    do_eval = False
    if do_eval:
        germanet_evaluation(print_errors=False)
    for x in split_compound(sys.argv[1]):
        print('\t'.join([str(y) for y in x]))