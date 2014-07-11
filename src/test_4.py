from nlp_correction import NLP_Correction
import os
import sys
import itertools
import math
import random
import Levenshtein as lv

def main():
    nlp_test = NLP_Correction()
    '''
    test_phrase_list = ["tskk to yiu lqtrr","hrllo wirld","wgat aee ypu dping","wrkcome to cguna"]
    for each_phrase in test_phrase_list:
        print "="*20
        nlp_test.best_correction(each_phrase.lower())
    '''
    #nlp_test.words_level_correction("windaws")

    
    # Testing with bulk data
    
    # Collecting candidate phrases
    # Suppose all phrases are list
    # Randomly collect 10 phrases from each, tosses them and test
    w2_words = open("w2_.txt","r").readlines()
    w3_words = open("w3_.txt","r").readlines()
    w4_words = open("w4_.txt","r").readlines()
    w5_words = open("w5_.txt","r").readlines()
    
    test_num = 10
    pos_list = [int(math.floor(random.random()*len(w2_words))) for i in range(0,test_num)]
    all_phrases = []
    i = 0
    w2_candi_phrase = ""
    w3_candi_phrase = ""
    w4_candi_phrase = ""
    w5_candi_phrase = ""
    print "Loading phrases..."
    for item in pos_list:

        w2_pos = item
        while any(sym in ' '.join(w2_words[w2_pos].strip().split('\t')[1:]) for sym in ('\'','-','_',':',';','+','.')):
          w2_pos = item + i
          i+=1
        w2_candi_phrase = ' '.join(w2_words[w2_pos].strip().split('\t')[1:])
        i = 0
        
        w3_pos = item
        while any(sym in ' '.join(w3_words[w3_pos].strip().split('\t')[1:]) for sym in ('\'','-','_',':',';','+','.')):
          w3_pos = item + i
          i+=1
        w3_candi_phrase = ' '.join(w3_words[w3_pos].strip().split('\t')[1:])
        i = 0

        w4_pos = item
        while any(sym in ' '.join(w4_words[w4_pos].strip().split('\t')[1:]) for sym in ('\'','-','_',':',';','+','.')):
          w4_pos = item + i
          i+=1
        w4_candi_phrase = ' '.join(w4_words[w4_pos].strip().split('\t')[1:])
        i = 0

        w5_pos = item
        while any(sym in ' '.join(w5_words[w5_pos].strip().split('\t')[1:]) for sym in ('\'','-','_',':',';','+','.')):
          w5_pos = item + i
          i+=1
        w5_candi_phrase = ' '.join(w5_words[w5_pos].strip().split('\t')[1:])
        i = 0

        all_phrases.append(w2_candi_phrase)
        all_phrases.append(w3_candi_phrase)
        all_phrases.append(w4_candi_phrase)
        all_phrases.append(w5_candi_phrase)
    print "Phrases loaded!"

    # And there are a total number of 
    # Testing data include:
    # 2, 3, 4, 5 gram 
    # Citation requires: 
    # Davies, Mark. (2011) N-grams data from the Corpus of Contemporary American English (COCA). Downloaded from http://www.ngrams.info on February 02, 2014
    # for each dataset, change 20%, 40%, 60%, 80% and 100% of character
    len_cases = [2,3,4,5]
    proportion_cases = [4]
    performance_record = []
    print "Case by Case testing..."
    for exp_case in itertools.product(*[len_cases,proportion_cases]):
        test_phrase_list = [phrase for phrase in all_phrases if len(phrase.split(" ")) == exp_case[0]]
        tossed_phrase_list = []
        for each_test_phrase in test_phrase_list:
            tossed_phrase = []
            for each_word in each_test_phrase.split(" "):
                each_word = toss_random_char(each_word,exp_case[1])
                tossed_phrase.append(each_word)
            tossed_phrase_list.append([each_test_phrase,' '.join(tossed_phrase)])

        # Now that we have a list of [(right,tossed)...], ran the algorithm 
        print "Round:"
        print "ngram:"+str(exp_case[0])+" edit:"+str(exp_case[1])
        correct_t1 = 0;
        correct_t3 = 0;
        correct_t5 = 0;
        total = 0;
        distance = 0;
        entropy_tossed = 0;
        entropy_correct = 0;
        #print "tossed list:"
        #print tossed_phrase_list
        for each_phrase in tossed_phrase_list:
            #print "tossed: "+str(each_phrase)
            possible_matches,garb_entropy,correct_entropy = nlp_test.best_correction(each_phrase[1],exp_case[1])
            if len(possible_matches) > 0:
                top1_match = [each[0] for each in possible_matches[:1]]
                top3_match = [each[0] for each in possible_matches[:3]]
                top5_match = [each[0] for each in possible_matches[:5]]
                #print "Top 5 match"
                #print top5_match
                candidates = [each[0] for each in possible_matches]
                #print "Target :"+str(each_phrase)
                if each_phrase[0] in top1_match:
                    correct_t1 += 1
                if each_phrase[0] in top3_match:
                    correct_t3 += 1
                if each_phrase[0] in top5_match:
                    correct_t5 += 1
                total += 1
                # Calculate information gained, i.e. calcualte average num of different letters
                total_distance = 0
                for each_cand in candidates:
                    total_distance += lv.distance(each_cand,each_phrase[0])

                #print "Candidate"
                #print candidates
                #print "Phrase"
                #print each_phrase[0]

                avg_distance_per_word = float(total_distance)/float(len(candidates))/float(len(each_phrase[0].split(" ")))
                distance += avg_distance_per_word
                entropy_tossed += garb_entropy
                entropy_correct += correct_entropy

        percentage_t1 = float(correct_t1)/float(total)
        percentage_t3 = float(correct_t3)/float(total)
        percentage_t5 = float(correct_t5)/float(total)
        avg_distance = distance/float(total)
        avg_garb_entropy = entropy_tossed/float(total)
        avg_correct_entropy = entropy_correct/float(total)
        print "Performance"
        print [exp_case[0],exp_case[1],percentage_t1,percentage_t3,percentage_t5,avg_distance,avg_garb_entropy,avg_correct_entropy]
        performance_record.append([exp_case[0],exp_case[1],percentage_t1,percentage_t3,percentage_t5,avg_distance,avg_garb_entropy,avg_correct_entropy])
    # Write to file
    record_data = open("record_4.txt","w")
    record_data.write(str(performance_record))
    record_data.close()

def toss_random_char(word,bits):
    original_word = word
    confusion_matrix = {'a':{'s':0.097,'e':0.0515,'z':0.0152,'d':0.0061},
                'b':{'n':0.2199,'v':0.1064,'g':0.0355,'h':0.0213},
                'c':{'x':0.0791,'v':0.0621,'d':0.0282,'f':0.0282},
                'd':{'s':0.1804,'e':0.1031,'f':0.0412,'t':0.0309},
                'e':{'r':0.0555,'w':0.0104,'s':0.0087,'a':0.0069},
                'f':{'d':0.1931,'g':0.1379,'e':0.0552,'r':0.0552},
                'g':{'h':0.0941,'f':0.0765,'e':0.0412,'t':0.0412},
                'h':{'j':0.0984,'g':0.0710,'n':0.0383,'u':0.0383},
                'i':{'u':0.0775,'o':0.0630,'l':0.0097,'j':0.0048},
                'j':{'h':0.1341,'k':0.1159,'u':0.0976,'m':0.0549},
                'k':{'l':0.1852,'i':0.1481,'j':0.0864,'u':0.0432},
                'l':{'o':0.0681,'i':0.0419,'k':0.0419,'j':0.0052},
                'm':{'n':0.2298,'j':0.0373,'h':0.0248,'l':0.0248},
                'n':{'m':0.1495,'b':0.0619,'h':0.0515,'j':0.0258},
                'o':{'i':0.1522,'p':0.0727,'r':0.0069,'l':0.0035},
                'p':{'o':0.2766,'l':0.0160,'i':0.0106,'r':0.0053},
                'q':{'e':0.3050,'a':0.1064,'w':0.0426,'l':0.0071},
                'r':{'e':0.3578,'t':0.0856,'a':0.0061,'u':0.0061},
                's':{'a':0.3092,'e':0.0723,'d':0.0683,'x':0.0080},
                't':{'r':0.1837,'y':0.0408,'e':0.0367,'g':0.0122},
                'u':{'i':0.2465,'y':0.0563,'j':0.0070,'k':0.0070},
                'v':{'c':0.1643,'b':0.1357,'g':0.0357,'n':0.0286},
                'w':{'e':0.6752,'q':0.1401,'a':0.0446,'s':0.0191},
                'x':{'c':0.1959,'z':0.1892,'a':0.0676,'s':0.0405},
                'y':{'u':0.2486,'t':0.1622,'i':0.0324,'r':0.0216},
                'z':{'a':0.2708,'x':0.2041,'s':0.0903,'c':0.0208},
                };
    
    bits_changed = min(len(word),bits)
    for i in range(0,bits_changed):
        pos = int(math.floor(random.uniform(1,len(word))))
        try:
            candi_keys = confusion_matrix[word[pos]].keys()
            candi_key = candi_keys[int(math.floor(random.uniform(1,len(candi_keys))))]
            word = word[:pos-1]+candi_key+word[pos:]
        except:
            print original_word
    return word

if __name__=='__main__':
    main()
