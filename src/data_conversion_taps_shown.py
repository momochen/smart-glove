import os
import sys
import csv

def main():
    path = os.getcwd()
    parent_path = os.sep.join(path.split(os.sep)[:-1])
    data_dir = parent_path+"/data/raw-data/20140827momo"
    all_csv = [each for each in os.listdir(data_dir) if each.endswith(".csv")]

    if not os.path.exists(data_dir+"/cvt"):
        os.mkdir(data_dir+"/cvt")

    if not os.path.exists(data_dir+"/cvt/taps"):
        os.mkdir(data_dir+"/cvt/taps")

    for each_csv in all_csv:
        convert_file(data_dir,each_csv)
    return "Done"

def convert_file(data_dir,csv_file):
    
    csv_data_input = open(data_dir+"/"+csv_file,"r")
    csv_data_output = open(data_dir+"/cvt/"+"cvt-"+csv_file,"w")
    csv_data_output_taps = open(data_dir+"/cvt/taps/cvt-"+csv_file,"w")
    #relabel the time series with the absolute time stamps
    time_stamp_list = []
    while True:
        line = csv_data_input.readline()
        if len(line) == 0: 
            break
        try:
            #x,y,z = convert_data(tuple(float(x) for x in line.split(",")))
            line_list = line.split(",")
            if len(line_list)==17:
                # Raw data
                # For new data format
                uid,time_stamp,x,y,z,accel,ax,ay,az,gyro,gx,gy,gz,mag,mx,my,mz = tuple(line_list)
                #time_stamp,x,y,z = tuple(line_list)
                #csv_data_output.write(str(x)+","+str(y)+","+str(z)+","+str(mx)+","+str(my)+","+str(mz))
                csv_data_output.write(str(x)+","+str(y)+","+str(z)+"\r\n")
                time_stamp_list.append(str(time_stamp))
            elif len(line_list)==8:
                # Detected taps
                # For new data format
                uid,time_start,time_stop,sth,peak_x,peak_y,peak_z,tap_type = tuple(line_list)
                #time_start,time_stop,sth,peak_x,peak_y,peak_z,tap_type = tuple(line_list)
                '''
                if int(time_start)<0
                    time_start = int(time_start)+2**32
                if int(time_stop)<0:
                    time_stop = int(time_stop)+2**32
                '''
                start_index = time_stamp_list.index(str(time_start))
                end_index = time_stamp_list.index(str(time_stop))
                csv_data_output_taps.write(str(start_index)+","+str(end_index)+","+tap_type)
            else:
                # Just ignore those...
                pass
        except:
            print line
    csv_data_input.close()
    csv_data_output.close()
    csv_data_output_taps.close()

    print csv_file+":done"

if __name__=="__main__":
    main()

