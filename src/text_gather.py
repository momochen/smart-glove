import os
import sys

def gather_ngram():
    print "gathering data"
    gram_2 = []
    gram_3 = []
    gram_4 = []
    gram_5 = []
    all_words = []
    files = open('head.txt','r').readlines()
    i = 0 
    for line in files:
        i += 1
        print i
        if not any(sym in line for sym in ('\'','-','_',':',';','+')):
            grams = line.strip().split('\t')[1:]
            if len(grams)==2:
                gram_2.append(grams)
            elif len(grams)==3:
                gram_3.append(grams)
            elif len(grams)==4:
                gram_4.append(grams)
            elif len(grams)==5:
                gram_5.append(grams)
            all_words = all_words + grams

    f_all_gram = [gram_2,gram_3,gram_4,gram_5]
    f = open('all_ngrams_corpus.txt','w')
    f.write(' '.join(all_words))
    
    #return (all_words,f_all_gram)

def main():
    gather_ngram()

if __name__=='__main__':
    main()
