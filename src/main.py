import os
import sys
from gr_model import *
from move2stc import Move2Stc
from glove_data_input import GloveData
import copy
import time

def main():
    print "Starting..."
    # Train gesture recognition model
    print "Preparing gesture recognition model..."

    # 1 
    gr_models,cm = train_gesture_recognition_model()

    # Prepare feature extractor
    print "Preparing feature extractor..."
    # 2
    fte = Feature_Target_Extractor()

    # raw_ts = [[x_t0,y_t0,z_t0],[x_t1,y_t1,z_t1]...]
    # ft_data = fte.transform2ft(raw_ts)
    # move_label = gr_models.test_single(ft_data)

    # Setup connection to language model service
    print "Preparing language model..."
    lm_model = Move2Stc(cm)
    #lm_model = Move2Stc()
    # stc = lm_model.m2s([[00000000,00000001],[01000000,01010000]])
    
    # Setup sensor data reading
    print "Preparing glove..."
    gd = GloveData('/dev/tty.usbmodem1411')
    # Start collecting data
    one_sample_data = []
    sample_counter = 0
    tap_one_found = False
    end_of_stc_found = False
    one_word = []
    word_move_sequence = []
    stc_sequence = []
    time_last = []
    f = open('time_last.txt','w')

    while True:
        one_piece = gd.serial_obj().readline()
        start = time.time()
        sample_point = one_piece.split(",")
        if len(sample_point)==17:
            if tap_one_found:
                if sample_counter<gd.get_sample_limit():
                    # Within tap
                    one_sample_data.append(list([float(x) for x in sample_point[2:5]+sample_point[14:17]]))
                    sample_counter+=1
                else:
                    # Time expired
                    tap_one_found = False
                    sample_counter = 0
                    one_sample_data = []
        elif len(sample_point)==8:
            if sample_point[-1]=="tap-1\r\n" or sample_point[-1]=="tap-2\r\n":
                tap_one_found = True
            elif sample_point[-1]=="flip\r\n" or sample_point[-1]=="none\r\n":
                tap_one_found = False
            elif sample_point[-1]=="triple-tap\r\n":
                # TODO: What's the representation of 3 tap?
                end_of_stc_found = True
                tap_one_found = False

            if len(one_sample_data)>0:
                if tap_one_found:
                    # For continuous tap
                    sample_counter = 0
                    # Push the one letter data into one word array
                    if len(one_sample_data)>0:
                        one_word.append(list(one_sample_data))
                elif not tap_one_found and not end_of_stc_found:
                    # Flip detected, which means end of a word
                    # Send flip signal to start finding a possible word
                    for each_letter in one_word:
                        move_label = gr_models.test_single(fte.transform2ft(each_letter))
                        print "move",move_label
                        word_move_sequence.append(lm_model.label2code(str(move_label)))
                    stc_sequence.append(list(word_move_sequence))
                    word_move_sequence = []
                    one_word = []
                elif end_of_stc_found:
                    # send stc_sequence to language model
                    print "move sequence:",stc_sequence

                    # Find all possible sequences based on confusion matrix
                    taps_list = lm_model.p_stc_seqs2tapbox(stc_sequence)
                    words_list = lm_model.p_stc_tap2word(taps_list)
                    print "words_list",words_list
                    stc_list = lm_model.words2stc(words_list)
                    print stc_list

                    stc_sequence = []
                    one_word = []
                    word_move_sequence = []
                    end_of_stc_found = False
                    end_of_word_found = False
                    
            one_sample_data = []
        end = time.time()
        f.write(str(end-start)+'\r\n')

    f.close()

    # Keeps collecting data
    # Detecting moves before a flip is detected as a separator for one word
    # Once a 3-tap is detected to trigger calls to language model

    # Send movements data to language model to detect sentences

if __name__=="__main__":
    main()
