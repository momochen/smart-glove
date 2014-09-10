import os
import sys
import serial

class GloveData:
    
    def __init__(self,addr):
        self.device = addr
        self.rate = 115200
        self.ser = serial.Serial(self.device,self.rate)
        self.sample_limit = 100
        # A list of feature list
        # [[lta_0,lta_1,lta_2...],[ltb_0,ltb_1...]]
        self.one_word = []

    def get_sample_limit(self):
        return self.sample_limit

    def get_movement_raw_data(self):
        # one_sample_data will be a list of list of accelerometer data
        one_sample_data = []
        sample_counter = 0
        tap_one_found = False

        while True:
            one_piece = self.ser.readline()
            sample_point = one_piece.split(",")
            if len(sample_point)==17:
                if tap_one_found:
                    if sample_counter<self.sample_limit:
                        # Within tap
                        # Conversion:
                        # x = x_val/230-0.05, y = y_val/230, z = z_val/230
                        one_sample_data.append(list(sample_point[2:5]))
                        #one_sample_data.append(list(sample_point[2:5])+list(sample_point[14:17]))
                        sample_counter+=1
                    else:
                        # Time expired
                        tap_one_found = False
                        sample_counter = 0
                        one_sample_data = []
            elif len(sample_point)==8:
                if sample_point[-1]=="tap-1\r\n" or sample_point[-1]=="tap-2\r\n":
                    tap_one_found = True
                elif sample_point[-1]=="flip\r\n":
                    tap_one_found = False

                if len(one_sample_data)>0 and tap_one_found:
                    # For continuous tap
                    print sample_point[-1]
                    print "one sample here:"
                    print "length:",len(one_sample_data)
                    print "sample point:",one_sample_data[0]
                    counter = 0
                    # Push the one letter data into one word array
                    self.one_word.append([list(one_sample_data)])
                else:
                    # Flip detected, which means end of a word
                    # Send flip signal to start finding a possible word
                    pass

                one_sample_data = []
        return 

    def serial_obj(self):
        return self.ser

    def get_one_word(self):
        # Get raw data for one word
        return self.one_word

def main():
    gd = GloveData('/dev/tty.usbmodem1411')
    #gd.get_movement_raw_data()
    while True:
        print gd.serial_obj().readline()

if __name__=="__main__":
    main()
