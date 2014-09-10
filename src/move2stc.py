import os
import sys
import requests
import itertools
import copy
from joblib import Parallel, delayed
import re,collections
import time

class Move2Stc:
    
    def __init__(self,cm=None):

        self.default_moves = [["00000110","01010000","00000000","00000001"],["00000100","01100000","00000101","00000101"]]
        self.server_addr_moves = "http://128.113.106.95:8080/SmartGloveWS/rest/sgws/moves"
        self.server_addr_taps = "http://128.113.106.95:8080/SmartGloveWS/rest/sgws/taps"
        self.server_addr_words = "http://128.113.106.95:8080/SmartGloveWS/rest/sgws/words"
        self.left1mask = 1<<4
        self.left2mask = 1<<5
        self.right1mask = 1
        self.right2mask = 1<<1
        self.up1mask = 1<<2
        self.up2mask = 1<<3
        self.down1mask = 1<<6
        self.down2mask = 1<<7
        self.keyboard = [[1,2,3],[4,5,6],[7,8,9]]
        '''
        00   00   00 00
        down,left,up,right
        '''
        self.label2code_dict = {
            "cvt-1-2":"00000001",
            "cvt-1-3":"00000010",
            "cvt-1-4":"01000000",
            "cvt-1-5":"01000001",
            "cvt-1-6":"01000010",
            "cvt-1-7":"10000000",
            "cvt-1-8":"10000001",
            "cvt-1-9":"10000010",
            "cvt-3-4":"01100000",
            "cvt-3-5":"01010000",
            "cvt-3-7":"10100000",
            "cvt-3-8":"10010000",
            "cvt-7-2":"00001001",
            "cvt-7-3":"00001010",
            "cvt-7-5":"00000101",
            "cvt-7-6":"00000110",
            "cvt-9-1":"00101000",
            "cvt-9-2":"00011000",
            "cvt-9-3":"00001000",
            "cvt-9-4":"00100100",
            "cvt-9-5":"00010100",
            "cvt-9-6":"00000100",
            "cvt-9-7":"00100000",
            "cvt-9-8":"00010000",
            "cvt-5-5":"00000000"}
        self.code2label_dict = dict()
        for key,val in self.label2code_dict.iteritems():
            self.code2label_dict.update({val:key})

        # cm_dict is a confusion matrix with key in move code and values in move code
        self.cm_dict = dict()
        # Filter those entries larger than 0.001
        if cm:
            for key in cm.keys():
                self.cm_dict.update({self.label2code_dict[str(key)]:[]})
                for sub_key in cm[key].keys():
                    if cm[key][sub_key]>0.1:
                        self.cm_dict[self.label2code_dict[str(key)]].append(self.label2code_dict[str(sub_key)])
        else:
            try:
                f = open('cm.text','r')
                cm = eval(f.read())
                for key in cm.keys():
                    self.cm_dict.update({self.label2code_dict[str(key)]:[]})
                    for sub_key in cm[key].keys():
                        if cm[key][sub_key]>0.1:
                            self.cm_dict[self.label2code_dict[str(key)]].append(self.label2code_dict[str(sub_key)])
                f.close()
            except:
                self.cm_dict = dict()
        
    def label2code(self,label):
        return self.label2code_dict[label]

    def code2label(self,code):
        return self.code2label_dict[code]

    def m2s(self,move_list=None):
        if not move_list:
            move_list = self.default_moves
        param_str_list = []
        for each in move_list:
            param_str_list.append(",".join(each))
        param_str = ";".join(param_str_list)
        payload = {'movestr': param_str}
        r = requests.get(self.server_addr, params=payload)
        return r.text
        
    def tap2word(self,tap_list=None):
        if not tap_list:
            tap_list = [2,6,9]
        param_str = ",".join([str(x) for x in tap_list])
        payload = {'tapstr':param_str}
        r = requests.get(self.server_addr_taps,params=payload)
        return r.text

    def word2stc(self,wordstr=None):
        if not wordstr:
            wordstr = "hello,aloha;world,word"
        payload = {'wordstr':wordstr}
        r = requests.get(self.server_addr_words,params=payload)
        return r.text
        
    def infer_possible_moves(self,one_word_seq):
        # input: a list of move sequences
        # output: a list of list of move sequences
        one_word_moves = []
        for each_move in one_word_seq:
            one_word_moves.append(self.cm_dict[each_move])
        one_word_all_moves = [list(each_one) for each_one in list(itertools.product(*one_word_moves))]
        return one_word_all_moves
        
    def infer_possible_stc(self,seq):
        possible_seqs = []
        for each_word_seq in seq:
            one_word_moves = []
            for each_letter_move in each_word_seq:
                one_word_moves.append(self.cm_dict[each_letter_move])
            one_word_all_moves = list(itertools.product(*one_word_moves))
            possible_seqs.append(list(one_word_all_moves))
        all_possible_seqs_combination = list(itertools.product(*possible_seqs))
        return all_possible_seqs_combination
        
    def movelist2intlist(self,movelist):
        for i in range(len(movelist)):
            movelist[i] = int(movelist[i],2)
        return movelist
        
    def moves_valid(self,movelist):
        movelist = self.movelist2intlist(movelist)
        left_moves,right_moves,up_moves,down_moves = 0,0,0,0
        for i in range(len(movelist)):
            if (movelist[i]&self.down2mask)==self.down2mask:
                down_moves+=2
            if (movelist[i]&self.down1mask)==self.down1mask:
                down_moves+=1
            if (movelist[i]&self.left1mask)==self.left1mask:
                left_moves+=1
            if (movelist[i]&self.left2mask)==self.left2mask:
                left_moves+=2
            if (movelist[i]&self.up1mask)==self.up1mask:
                up_moves+=1
            if (movelist[i]&self.up2mask)==self.up2mask:
                up_moves+=2
            if (movelist[i]&self.right1mask)==self.right1mask:
                right_moves+=1
            if (movelist[i]&self.right2mask)==self.right2mask:
                right_moves+=2
            if abs(right_moves-left_moves)>2 or abs(up_moves-down_moves)>2:
                return False

        return True

    def movestr2index(self,movestr,row,col):
        move_digit = int(movestr)
        if move_digit&self.down2mask == self.down2mask:
            row+=2
        if move_digit&self.down1mask == self.down1mask:
            row+=1
        if move_digit&self.left1mask == self.left1mask:
            col-=1
        if move_digit&self.left2mask == self.left2mask:
            col-=2
        if move_digit&self.up1mask == self.up1mask:
            row-=1
        if move_digit&self.up2mask == self.up2mask:
            row-=2
        if move_digit&self.right1mask == self.right1mask:
            col+=1
        if move_digit&self.right2mask == self.right2mask:
            col+=2
        return (row,col)
        
    def seqs2tapbox(self,seq):
        # Input: Sequence in a list of list of move codes
        all_possible_tap_seqs = []
        if(self.moves_valid(seq)):
            tap_seq = []
            for i in range(9):
                j = i/3
                k = i%3
                tap_seq.append(self.keyboard[j][k])

                for l in range(len(seq)):
                    j,k = self.movestr2index(seq[l],j,k)
                    try:
                        tap_seq.append(self.keyboard[j][k])
                    except:
                        # Invalid position
                        tap_seq = []
                        break

                if len(tap_seq)>0:
                    all_possible_tap_seqs.append(list(tap_seq))
                    tap_seq = []
                else:
                    pass

        return all_possible_tap_seqs
        
    def word_seqs2tapbox(self,seqs):
        # Generate all possible moves according to confusion matrix
        all_seqs = self.infer_possible_moves(seqs)
        # Converet those move sequences to valid tap box
        all_possible_taps = []
        for each_seq in all_seqs:
            all_possible_taps = all_possible_taps + self.seqs2tapbox(each_seq)

        return all_possible_taps
        
    def p_stc_seqs2tapbox(self,seqs_list):
        # Input: [["00000001","00000001"],["00000001","00000001"]]
        # Output: [[],[]]
        # Note to create a copy of all stateless functions here....otherwise parallel not working
        taps_list = []
        for each_move in seqs_list:
            taps_list = taps_list + [p_move2words(each_move,self.cm_dict)]
        return taps_list
        
    def p_stc_tap2word(self,taps_list):
        words_list = []
        for each_tap in taps_list:
            words_candidates = []
            words_candidates = p_tap2word(each_tap)
            words_list.append(list(words_candidates))
        return words_list
        
    def words2stc(self,words_list):
        param_val = ";".join([",".join(x) for x in words_list])
        payload = {"wordstr":param_val}
        r = requests.get(self.server_addr_words,params=payload)
        return r.text.split(';')[:5]
    
server_addr = "http://128.113.106.95:8080/SmartGloveWS/rest/sgws/"

def tap2word(tap_list=None):
    if not tap_list:
        tap_list = [[2,6,9],[3,4,5],[2,2,9]]
    res =[x for x in Parallel(n_jobs=10)(delayed(lm_request)('taps','tapstr',[str(y) for y in x]) for x in tap_list if not 1 in x) if len(x)>0]
    merged_res = []
    for each in res:
        merged_res = merged_res + each
    return merged_res

def lm_request(service_name,param_name,param_val):
    payload = {param_name:",".join(param_val)}
    r = requests.get(server_addr+service_name,params=payload)
    res = [y for y in [x.strip() for x in r.text.split(";")] if len(y)>0]
    return res

def p_move2words(move_seq,cm_dict):
    # Input: ["00000001","00000001"]
    # Output: [word0,word1,...]

    # Spawn moves according to the confusion matrix
    move_list = Parallel(n_jobs=10)(delayed(p_possible_moves)(cm_dict,x) for x in move_seq)
    # Cross product the move_list to get all possible combinations
    # Parallel each possible moves combinations
    taps_list = Parallel(n_jobs=10)(delayed(search_tap_seq)(list(each_move_seq)) for each_move_seq in list(itertools.product(*move_list)))
    
    new_taps_list = []
    for each in taps_list:
        new_taps_list = new_taps_list + each
    return new_taps_list

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

def words(text): return re.findall('[a-z]+', text.lower()) 
NWORDS = train(words(file('british_dict.txt').read()))
def known(words): return [w for w in words if w in NWORDS]

def p_tap2word(taps_list):
    # input: [[4,5,6],[7,8,9]]
    # output: ["hello", "ahalo"]
    res_a = []
    for each in taps_list:
        words_per_tap = single_tap2word(each)
        if len(words_per_tap)>0:
            res_a.append(words_per_tap)
    #res_a = Parallel(n_jobs=20)(delayed(single_tap2word)(each_tap) for each_tap in taps_list)
    taps_words_list = [x for x in res_a if x>0]
    my_words_list = []
    for each in taps_words_list:
        my_words_list = my_words_list + each
    return my_words_list

def single_tap2word(tap):
    # input:[4,5,6]
    # output: hello,aloha
    if 1 in tap:
        return []
    each_tap_letter_list = []
    for each_tap_box in tap:
        each_tap_letter_list.append(cell2letter_dict[each_tap_box])
    letter_combination_list = ["".join(each_combination) for each_combination in list(itertools.product(*each_tap_letter_list))]
    
    known_words = known(letter_combination_list)
    
    return known_words

def search_tap_seq(move_seq):
    # Convert move seqs to possible taps sequence
    # Input: Sequence in a list of list of move codes
    keyboard = [[1,2,3],[4,5,6],[7,8,9]]
    all_possible_tap_seqs = []
    if(moves_valid(move_seq)):
        tap_seq = []
        for i in range(9):
            j = i/3
            k = i%3
            tap_seq.append(keyboard[j][k])

            for l in range(len(move_seq)):
                j,k = movestr2index(move_seq[l],j,k)
                try:
                    tap_seq.append(keyboard[j][k])
                except:
                    # Invalid position
                    tap_seq = []
                    break

            if len(tap_seq)>0:
                all_possible_tap_seqs.append(list(tap_seq))
                tap_seq = []
            else:
                pass

    return all_possible_tap_seqs

cell2letter_dict = {
    2:["a","b","c"],
    3:["d","e","f"],
    4:["g","h","i"],
    5:["j","k","l"],
    6:["m","n","o"],
    7:["p","q","r","s"],
    8:["t","u","v"],
    9:["w","x","y","z"]
    }
def movestr2index(movestr,row,col):
    move_digit = int(movestr)
    if move_digit&(1<<7) == (1<<7):
        row+=2
    if move_digit&(1<<6) == (1<<6):
        row+=1
    if move_digit&(1<<4) == (1<<4):
        col-=1
    if move_digit&(1<<5) == (1<<5):
        col-=2
    if move_digit&(1<<2) == (1<<2):
        row-=1
    if move_digit&(1<<3) == (1<<3):
        row-=2
    if move_digit&1 == 1:
        col+=1
    if move_digit&(1<<1) == (1<<1):
        col+=2
    return (row,col)
def movelist2intlist(movelist):
    for i in range(len(movelist)):
        movelist[i] = int(movelist[i],2)
    return movelist

def moves_valid(movelist):
    movelist = movelist2intlist(movelist)
    left_moves,right_moves,up_moves,down_moves = 0,0,0,0
    for i in range(len(movelist)):
        if (movelist[i]&(1<<7))==(1<<7):
            down_moves+=2
        if (movelist[i]&(1<<6))==(1<<6):
            down_moves+=1
        if (movelist[i]&(1<<4))==(1<<4):
            left_moves+=1
        if (movelist[i]&(1<<5))==(1<<5):
            left_moves+=2
        if (movelist[i]&(1<<2))==(1<<2):
            up_moves+=1
        if (movelist[i]&(1<<3))==(1<<3):
            up_moves+=2
        if (movelist[i]&1)==1:
            right_moves+=1
        if (movelist[i]&(1<<1))==(1<<1):
            right_moves+=2
        if abs(right_moves-left_moves)>2 or abs(up_moves-down_moves)>2:
            return False

    return True


def p_possible_moves(cm_dict,move):
    return cm_dict[move]

def test(a):
    a+=2
    return a
    
def main():
    m = Move2Stc()
    moves = [["00100100","00000101","10000000"],["10010000","00001010"],["00000100","01010000"],["01000000","00100000","00000010","00100000"]]
    #moves = [["01000000","01000000"],["00000001","00000001","01000000"],["00000001","00000001"]]
    #stc = m.m2s(moves[:1]).split(";")
    '''
    for each in stc:
        print each
    '''
    '''
    # Testing code for inferencing based on tap
    all_words = []
    for each in moves[:4]:
        each_word_taps = m.word_seqs2tapbox(each)
        single_words = []
        for each_tap_seq in each_word_taps:
            words = m.tap2word(each_tap_seq).split(";")[:3]
            if len(words)>2:
                single_words = single_words + [x.strip() for x in words if len(x)>0]
        all_words.append(list(single_words))

    for i in range(len(all_words)):
        all_words[i] = ",".join(all_words[i])

    print m.word2stc(";".join(all_words))
    '''
    start = time.time()
    taps_list = m.p_stc_seqs2tapbox(moves)
    print taps_list,'\r\n'

    words_list = m.p_stc_tap2word(taps_list)
    print words_list
    end = time.time()
    print end-start
    stc_list = m.words2stc(words_list)
    print stc_list
    
if __name__=="__main__":
    main()
