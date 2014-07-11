import os
import sys
import csv

def main():
    path = os.getcwd()
    parent_path = os.sep.join(path.split(os.sep)[:-1])
    data_dir = parent_path+"/data/raw-data/2014-06-21"
    all_csv = [each for each in os.listdir(data_dir) if each.endswith(".csv")]

    if not os.path.exists(data_dir+"/cvt"):
        os.mkdir(data_dir+"/cvt")

    for each_csv in all_csv:
        convert_file(data_dir,each_csv)
    return "Done"

def convert_file(data_dir,csv_file):
    
    csv_data_input = open(data_dir+"/"+csv_file,"r")
    csv_data_output = open(data_dir+"/cvt/"+"cvt"+csv_file,"w")
    while True:
        line = csv_data_input.readline()
        if len(line) == 0: 
            break
        try:
            x,y,z = convert_data(tuple(float(x) for x in line.split(",")))
        except:
            print csv_file
            print line
        csv_data_output.write(str(x)+","+str(y)+","+str(z)+"\r\n")
    csv_data_input.close()
    csv_data_output.close()

    print csv_file+":done"

def convert_data(input_tuple):
    x = float(input_tuple[0])
    y = float(input_tuple[1])
    z = float(input_tuple[2])

    # Convert according to the equation
    xmin1 = 272
    xmax1 = 794
    ymin1 = 332
    ymax1 = 841
    zmin1 = 175
    zmax1 = 700

    xmin0 = 200
    xmax0 = 565
    ymin0 = 240
    ymax0 = 610
    zmin0 = 110
    zmax0 = 500
    ax = ((x * (xmax0 - xmin0)) + (xmin0 + xmax0) - (xmin1 + xmax1)) / (xmax1 - xmin1)
    ay = ((y * (ymax0 - ymin0)) + (ymin0 + ymax0) - (ymin1 + ymax1)) / (ymax1 - ymin1)
    az = ((z * (zmax0 - zmin0)) + (zmin0 + zmax0) - (zmin1 + zmax1)) / (zmax1 - zmin1)

    # Write the file with prefix: cvtXXX
    return (ax,ay,az)

if __name__=="__main__":
    main()

