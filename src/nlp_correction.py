import os
import sys
import re
import collections
import operator
import itertools
#sys.path.insert(0,'/Users/cheny/Downloads/stanford-parser-python-r22186/src/stanford_parser')
#from parser import Parser
import urllib2

alphabet = 'abcdefghijklmnopqrstuvwxyz'
def words(text):
    return re.findall('[a-z]+',text.lower())

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

words_dict = train(words(file('big.txt').read()))

class NLP_Correction:

    def __init__(self):
        self.confusion_table = dict()
        self.load_confusion_table(self.confusion_table)
        # Get the one-gram list ready for word level correction
        self.one_grams = list()
        # Get the N-gram list ready for sentence level correction
        self.n_grams = list()
        # Train the model 
        print "Training ngram model"
        self.lm = self.train_ngram_model()

    def train_ngram_model(self):
        import nltk
        from nltk.model import NgramModel
        from nltk.probability import *
        from nltk.corpus import webtext,brown
        #train_corpus = [word.lower() for word in webtext.words()]

        train_corpus = [word.lower() for word in brown.words(categories="news")]
        estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2) 
        #estimator = lambda fdist, bins: KneserNeyProbDist(fdist) 
        lm = NgramModel(5, train_corpus, estimator=estimator)
        return lm
        
    def best_correction(self,garb_stc,bits):
        # Using DP to find the best correction
        stc_words = garb_stc.split(" ")
        stc_words_crc_dict = [self.words_level_correction(x,bits) for x in stc_words]
        all_stc_candi = dict()
        # Populate cartesian product
        filtered_phrase_dict = stc_words_crc_dict[0]
        num_top_candidate = 10
        print "predictions..."
        for i in range(1,len(stc_words_crc_dict)):
            top_candidates = dict()
            for each_pre_phrase in filtered_phrase_dict.keys():
                for each_post_word in stc_words_crc_dict[i].keys():
                    phrase_cost = filtered_phrase_dict[each_pre_phrase]*1.0/self.lm.prob(each_post_word,[each_pre_phrase])*stc_words_crc_dict[i][each_post_word]
                    if len(top_candidates) < num_top_candidate:
                      top_candidates.update({str(each_pre_phrase+" "+each_post_word):phrase_cost})
                    else:
                        max_value =  max(top_candidates.values())
                        if phrase_cost < max_value:
                            del top_candidates[[x for x in top_candidates.keys() if top_candidates[x]==max_value][0]]
                            top_candidates.update({str(each_pre_phrase+" "+each_post_word):phrase_cost})

            filtered_phrase_dict = top_candidates

        #print "Most possible phrases are:"
        #print sorted(filtered_phrase_dict.iteritems(), key=operator.itemgetter(1))
        '''
        for element in itertools.product(*pop_words_list):
            stc_raw_cost = 0
            dict_counter = 0
            for each_words in element:
                stc_raw_cost+=stc_words_crc_dict[dict_counter][each_words]
                dict_counter+=1
                if stc_raw_cost > 100:
                    break
            if stc_raw_cost <= 100:
                all_stc_candi.update({str(' '.join(element)):stc_raw_cost})
        '''

        #sorted_dict = sorted(all_stc_candi.iteritems(), key=operator.itemgetter(1))
        #filtered_candidate_list = sorted_dict[:100]
        #print "Validating phrases..."
        # ==Plan A==
        # Consider the gain due to the n-gram occurance in the sentence
        # Analyze the semantic structure of the phrase
        '''
        stanford_parser = Parser()
        for each_phrase in filtered_candidate_list:
            print each_phrase
            dependencies = stanford_parser.parseToStanfordDependencies(str(each_phrase[0]))
            print dependencies
        '''
        # ==Plan B==
        # Query Google's Ngram Viewer
        # If there is a match, we assume it is a good phrase; otherwise, refuse the result
        '''
        valid_phrase = []
        for each_phrase in filtered_candidate_list:
            try:
                res = urllib2.urlopen("https://books.google.com/ngrams/graph?content="+str(('+'.join(str(each_phrase[0]).split(" "))))).read()
                if res :
                    valid_phrase.append(each_phrase)
            except:
                pass
        print "Valid Phrases are: "
        print valid_phrase
        '''
        # ==Plan C==
        # Train a ngram language model from web chats and brown u dataset
        '''
        print "Training language model..."
        import nltk
        from nltk.model import NgramModel
        from nltk.probability import LidstoneProbDist
        from nltk.corpus import webtext,brown
        train_corpus = [word.lower() for word in webtext.words()]
        estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2) 
        lm = NgramModel(5, train_corpus, estimator=estimator)
        '''
        # Using the prob(text,context) can give the probability of having "text" as the next word following "context"
        # Then the task become finding the maximum probability path from the first words to the last
        # Each time, collect the top 5 sub-phrase and carry on
        '''
        print "Calculating predictions..."
        phrase_prob_dict = dict()
        for each_phrase in filtered_candidate_list:
            phrase_list = each_phrase[0].split(" ")
            phrase_prob_dict.update({each_phrase:0})
            for i in range(1,len(phrase_list)):
                phrase_prob_dict[each_phrase]+=lm.prob(phrase_list[i],phrase_list[0:i])

        print "Results based on language model..."
        sorted_dict = sorted(phrase_prob_dict.iteritems(), key=operator.itemgetter(1))
        print sorted_dict
        '''
	print "candidate"
	result_list = sorted(filtered_phrase_dict.iteritems(), key=operator.itemgetter(1))
	if len(result_list)!=0:
        	return (result_list[:10],self.lm.entropy(garb_stc.split(" ")),self.lm.entropy(result_list[0][0].split(" ")))
	else:
		return (list(),0,0)
    def words_level_correction(self,garbage_word,bits):
        # Enum each possible correction within distance 

        if bits == 5:
            total_set,total_dict = self.edit5(garbage_word)
        elif bits == 4:
            total_set,total_dict = self.edit4(garbage_word)
        elif bits == 3:
            total_set,total_dict = self.edit3(garbage_word)
        elif bits == 2:
            total_set,total_dict = self.edit2(garbage_word)
        elif bits == 1:
            total_dict = dict()
            total_set,total_dict = self.edit1(garbage_word,total_dict)

        # Find those in the dict
        new_dict = dict()
        for each_key in total_set:
            if words_dict.has_key(each_key):
              new_dict.update({each_key:total_dict[each_key]})

        #print sorted(new_dict.iteritems(), key=operator.itemgetter(1))[:10]
        return new_dict

    def train(self,features):
        model = collections.defaultdict(lambda: 1)
        for f in features:
            model[f] += 1
        return model

    def words(self,text):
        return re.findall('[a-z]+',text.lower())

    def cost_calc(self,a,b):
        # return the costs that a is recognized as b
        if a == ' ' or b ==' ':
            return 30.0
        elif self.confusion_table[a].has_key(b):
            return round(1/self.confusion_table[a][b],2)
        else:
            return 30.0

    
    def edit5(self,word):
        edit5_dict = dict()
        edit5_set = set()
        edit4_set, edit4_dict = self.edit4(word)
        edit5_dict = edit4_dict
        for each_word in edit4_set:
            new_set,edit5_dict = self.edit1(word,edit5_dict)
            edit5_set = edit5_set.union(new_set)
        return (edit5_set,edit5_dict)

    def edit4(self,word):
        edit4_dict = dict()
        edit4_set = set()
        edit3_set, edit3_dict = self.edit3(word)
        edit4_dict = edit3_dict
        for each_word in edit3_set:
            new_set,edit4_dict = self.edit1(word,edit4_dict)
            edit4_set = edit4_set.union(new_set)
        return (edit4_set,edit4_dict)

    def edit3(self,word):
        edit3_dict = dict()
        edit3_set = set()
        edit2_set, edit2_dict = self.edit2(word)
        edit3_dict = edit2_dict
        for each_word in edit2_set:
            new_set,edit3_dict = self.edit1(word,edit3_dict)
            edit3_set = edit3_set.union(new_set)
        return (edit3_set,edit3_dict)

    def edit2(self,word):
        edit2_dict = dict()
        edit1_set,edit1_dict = self.edit1(word,edit2_dict)
        edit2_dict = edit1_dict
        edit2_set = set()
        for each_word in edit1_set:
            new_set,edit2_dict = self.edit1(each_word,edit2_dict)
            edit2_set = edit2_set.union(new_set)
        return (edit2_set,edit2_dict)


    def edit1(self,word,edit_dict):
        # Also include the word itself
        if not edit_dict.has_key(word):
            edit_dict.update({word:0.0001})

        splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes    = [a + b[1:] for a, b in splits if b]
        for a, b in splits:
            if b:
              if not edit_dict.has_key(str(a+b[1:])):
                  if edit_dict.has_key(str(a+b)):
                     edit_dict.update({str(a + b[1:]):self.cost_calc(b[0],' ')+edit_dict[str(a+b)]})
                  else:
                     edit_dict.update({str(a + b[1:]):self.cost_calc(b[0],' ')})

        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        for a, b in splits:
            if len(b)>1:
              if not edit_dict.has_key(str(a+b[1]+b[0]+b[2:])):
                  if edit_dict.has_key(str(a+b)):
                      edit_dict.update({str(a+b[1]+b[0]+b[2:]):(self.cost_calc(b[0],b[1])+self.cost_calc(b[1],b[0])+edit_dict[str(a+b)])})
                  else:
                      edit_dict.update({str(a+b[1]+b[0]+b[2:]):(self.cost_calc(b[0],b[1])+self.cost_calc(b[1],b[0]))})

        replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
        for a,b in splits:
            for c in alphabet:
                if b:
                  if not edit_dict.has_key(str(a+c+b[1:])):
                     if edit_dict.has_key(str(a+b)):
                        edit_dict.update({str(a+c+b[1:]):(self.cost_calc(b[0],c)+edit_dict[str(a+b)])})
                     else:
                        edit_dict.update({str(a+c+b[1:]):self.cost_calc(b[0],c)})

        
        inserts    = [a + c + b     for a, b in splits for c in alphabet]
        for a,b in splits:
            for c in alphabet:
              if not edit_dict.has_key(str(a+c+b)):
                  if edit_dict.has_key(str(a+b)):
                     edit_dict.update({str(a+c+b):(5*self.cost_calc(' ',c)+edit_dict[str(a+b)])})
                  else:
                     edit_dict.update({str(a+c+b):5*self.cost_calc(' ',c)})

              
        return (set([word] + deletes + transposes + replaces + inserts),edit_dict)

    def load_confusion_table(self,confusion_table):
        if len(confusion_table) == 0:
            # If empty then us the confusion table from previous research results
            self.confusion_table = {'a':{'s':0.097,'e':0.0515,'z':0.0152,'d':0.0061},
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
                }
        else:
            self.confusion_table = confusion_table
