#!/usr/bin/env python
"""
Example of a UDP txosc receiver with Twisted.

This example is in the public domain.
"""
from twisted.internet import reactor
from txosc import osc
from txosc import dispatch
from txosc import async
from gr_model_new import *
from move2stc import Move2Stc
from glove_data_input import GloveData
import copy
import time

def foo_handler(message, address):
    """
    Function handler for /foo
    """
    print("foo_handler")
    print("  Got %s from %s" % (message, address))

class UDPReceiverApplication(object):
    """
    Example that receives UDP OSC messages.
    """
    def __init__(self, port):
        self.port = port
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        print("Listening on osc.udp://localhost:%s" % (self.port))
        #self.receiver.addCallback("/foo", foo_handler)
        #self.receiver.addCallback("/ping", self.ping_handler)
        #self.receiver.addCallback("/quit", self.quit_handler)
        #self.receiver.addCallback("/ham/egg", self.ham_egg_handler)
        #self.receiver.addCallback("/*/egg", self.any_egg_handler)
        self.receiver.addCallback('/exo/hand/gesture',self.get_gesture)
        self.receiver.addCallback('/exo/hand/motion',self.raw_series)

        # Now, let's demonstrate how to use address nodes:
        # /cheese:
        self.cheese_node = dispatch.AddressNode("cheese")
        self.cheese_node.addCallback("*", self.cheese_handler)
        self.receiver.addNode("cheese", self.cheese_node)
        # /cheese/cheddar:
        self.cheddar_node = dispatch.AddressNode("cheddar")
        self.cheddar_node.addCallback("*", self.cheese_cheddar_handler)
        self.cheese_node.addNode("cheddar", self.cheddar_node)
        self.status = False
        self.starting_msg = []
        self.ts = []
        self.one_word = []
        self.one_sample_data = []
        self.tap_one_found = False
        self.end_of_stc_found = False
        self.word_move_sequence = []
        self.stc_sequence = []
        #self.receiver.fallback = self.fallback

        # Init everything about the gesture recognition
        print "starting..."
        print "gesture recognition model..."
        self.gr_models,self.cm = train_gesture_recognition_model()
        print "feature extractor..."
        self.fte = Feature_Target_Extractor()
        print "language model..."
        self.lm_model = Move2Stc(self.cm)

    def raw_series(self,message, address):
        msg_list = message.getValues()
        if self.status:
            # Good to start collecting raw_data
            if abs(msg_list[2])<1000:
                self.ts.append([float(msg_list[2])/230-0.05,float(msg_list[3])/230,float(msg_list[4])])
            
    def get_gesture(self,message, address):
        #print "raw data",message.getValues()
        msg_list = message.getValues()

        if 'tap' in msg_list[-1] and not 'triple-tap' in msg_list[-1]:
            if not self.status:
                # triggered to start
                self.status = True
            elif self.status:
                if self.ts and len(self.ts)<150:
                    # finish one, start a new one
                    self.status = False
                    self.one_word.append(self.ts)
                    #print "current one word",len(self.one_word)
                    self.ts = []
                    self.status = True
                elif len(self.ts)>=150:
                    # last move, ignore the data
                    self.status = False
                    self.ts = []
                else:
                    # self.ts is empty
                    pass
        elif 'flip' in msg_list[-1] or 'none' in msg_list[-1]:
            # wrap for one word:
            for each_letter in self.one_word:
                move_label = self.gr_models.test_single(self.fte.transform2ft(each_letter))
                print "move",move_label
                self.word_move_sequence.append(self.lm_model.label2code(str(move_label)))
                #self.word_move_sequence.append("00000001")
            #print "one word",self.word_move_sequence
            self.stc_sequence.append(self.word_move_sequence)
            self.word_move_sequence = []
            self.one_word = []
            self.status = False
            self.ts = []
        elif 'triple-tap' in msg_list[-1]:
            print "one stc",self.stc_sequence
            # Language model code here
            invalid = False
            for i in range(len(self.stc_sequence)):
                if len(self.stc_sequence[i])==0:
                    invalid = True
                    break
            if not invalid:
                try:
                    taps_list = self.lm_model.p_stc_seqs2tapbox(self.stc_sequence)
                    words_list = self.lm_model.p_stc_tap2word(taps_list)
                    print "words_list",words_list
                    stc_list = self.lm_model.words2stc(words_list)
                    print "stc list",stc_list
                except e:
                    pass
            else:
                print "None"
            self.stc_sequence = []
            self.one_word = []
            self.word_move_sequence = []
            self.status = False
            self.ts = []

    def cheese_handler(self, message, address):
        """
        Method handler for /ping
        """
        print("cheese_handler")
        print("  Got %s from %s" % (message, address))

    def cheese_cheddar_handler(self, message, address):
        """
        Method handler for /cheese/cheddar
        """
        print("cheese_cheddar_handler")
        print("  Got %s from %s" % (message, address))

    def any_egg_handler(self, message, address):
        """
        Method handler for /*/egg
        """
        print("any_egg_handler")
        print("  Got %s from %s" % (message, address))
    
    def fallback(self, message, address):
        """
        Fallback for any unhandled message
        """
        print("Fallback:")
        print("  Got %s from %s" % (message, address))

    def ping_handler(self, message, address):
        """
        Method handler for /ping
        """
        print("ping_handler")
        print("  Got %s from %s" % (message, address))

    def ham_egg_handler(self, message, address):
        """
        Method handler for /ham/egg
        """
        print("ham_egg_handler")
        print("  Got %s from %s" % (message, address))

    def quit_handler(self, message, address):
        """
        Method handler for /quit
        Quits the application.
        """
        print("quit_handler")
        print("  Got %s from %s" % (message, address))
        reactor.stop()
        print("Goodbye.")

if __name__ == "__main__":
    #app = UDPReceiverApplication(17779)
    app = UDPReceiverApplication(42003)
    reactor.run()

