import os
import sys
import csv
import matplotlib.pyplot as plt
import datetime
import numpy as np
from motifs import Motif
import json

def main():
    
    # Creating a dict to store the location of all sample data
    start_end_dict = collect_features()
    
    for each in start_end_dict:
        path = os.getcwd()
        parent_path = os.sep.join(path.split(os.sep)[:-1])
        da = DataAdaptor(parent_path+"/data/raw-data/2014-06-21/cvt/"+"cvt"+each+".csv")
        da.set_range_list(start_end_dict[each],400)
        da.set_motif_len(400)
        da.write_samples_to_file()

    #da.plot_3_dim(da.get_csv_data())

def collect_features():
    # Creating a dict to store the location of all sample data
    """
        {
            "1-2"::[110......],
            more elements

        }
    """
     # First try manually get the data from the time series
    start_12 = {"1-2":[850,1600,2200,2800,3300,4000,4500,5100,5700,6300]}
    start_13 = {"1-3":[1000,1600,2200,2800,3300,3900,4400,5000,5500,6100]}
    start_14 = {"1-4":[800,1400,2000,2600,3200,3800,4400,5000,5700,6300]}
    start_15 = {"1-5":[1100,1700,2400,3000,3700,4400,5000,6400,7100]}
    start_16 = {"1-6":[1100,1700,2200,2700,3300,3800,4400,5000,5500,6000]}
    start_17 = {"1-7":[1200,1700,2300,3000,3600,4200,4800,6700]}
    start_18 = {"1-8":[1100,1600,2200,2800,3400,4000,4600,5100,5700,6300]}
    start_19 = {"1-9":[1600,2300,3000,3700,4400,5100,5900,6500,7200,7800]}
    start_34 = {"3-4":[1200,1800,2400,3000,3600,4300,5000,5600,6200,6800]}
    start_35 = {"3-5":[1800,2500,3500,4300,5100,5900,6600,7300,8100]}
    start_37 = {"3-7":[1200,1800,2400,3000,3600,4300,5000,5700,6400,7000]}
    start_38 = {"3-8":[1400,2000,2600,3300,3900,4500,5200,5900,6800,7600]}
    start_72 = {"7-2":[1400,2000,2600,3300,3900,4400,5200,5900,6800,7600]}
    start_73 = {"7-3":[900,1400,2000,2700,3300,4000,4600,5300,6000,6600]}
    start_75 = {"7-5":[900,1400,2000,2700,3300,4000,4600,5300,6000,6600]}
    start_76 = {"7-6":[800,1400,2100,2800,3400,4100,4700,5300,5900,6600]}
    start_91 = {"9-1":[900,1500,2100,2800,3400,4000,4700,5200,5800,6400]}
    start_92 = {"9-2":[900,1500,2200,2800,3400,4000,4700,5400,6000,6700]}
    start_93 = {"9-3":[1200,1900,2600,3400,4000,4800,5500,6200,6900,7600]}
    start_94 = {"9-4":[1100,1700,2400,3100,3900,4700,5500,6200,6800,7500]}
    start_95 = {"9-5":[900,1500,2200,2900,3600,4300,5000,5600,6300,7000]}
    start_96 = {"9-6":[1200,1900,2500,3200,3900,4600,5300,6000,6800]}
    start_97 = {"9-7":[1200,1800,2500,3200,3900,4600,5300,6000,6800]}
    start_98 = {"9-8":[1300,1900,2600,3300,4000,4600,5400,6100,6800]}
    
    start_end_dict = dict()
    start_end_dict = dict(start_end_dict.items()+start_12.items()+start_13.items()+start_14.items()+start_15.items()+start_16.items())
    start_end_dict = dict(start_end_dict.items() + start_17.items()+start_18.items()+start_19.items()+start_34.items()+start_35.items())
    start_end_dict = dict(start_end_dict.items() + start_37.items()+start_38.items()+start_72.items()+start_73.items()+start_75.items())
    start_end_dict = dict(start_end_dict.items() + start_76.items()+start_91.items()+start_92.items()+start_93.items()+start_94.items())
    start_end_dict = dict(start_end_dict.items() + start_95.items()+start_96.items()+start_97.items()+start_98.items())

    return start_end_dict

class DataAdaptor:
    """
    Adapt the csv data into json for each of the sample with format of this:
    {
        "accX":
        "accY":
        "accZ":
        "key":
    }
    """
    def __init__(self,csv_file_name):
        self._csv_data = open(csv_file_name,"r").readlines()
        self._csv_file_name = csv_file_name
        self._range_list = None
        self._motif_len = None
        self._filename = csv_file_name.split("/")[-1].split(".csv")[0]
        self._data_sample_list = list()
        self._motif_dict = dict()

    def set_range_list(self,start_list,mtf_len):
        self._range_list = [(x,x+mtf_len) for x in start_list]

    def get_range_list(self):
        return self._range_list

    def set_motif_len(self,motif_len):
        self._motif_len = motif_len

    def get_motif_len(self):
        return self._motif_len
    
    def set_feature_list(self,feature_list):
        self._feature_list = feature_list
    
    def get_feature_list(self):
        return self._feature_list

    def set_motif_dict(self,motif_dict):
        self._motif_dict = motif_dict

    def get_motif_dict(self):
        return self._motif_dict

    def get_csv_data(self):
        return self._csv_data

    def write_samples_to_file(self):
        if self._range_list==None or self._motif_len==None:
            return None
        else:
            feature_list = self.get_data_samples(self._csv_data,self._filename,self._range_list)
            path = self._csv_file_name.split("/")
            sample_data_filename = "/".join(path[0:(len(path)-5)])+"/data/training-data/sample-"+self._filename.split(".csv")[0]+".json"

            f = open(sample_data_filename,"w")
            f.write(json.dumps(feature_list))
            f.close()

    def data_segmentation(self,csv_data):
        print ""

    def get_data_samples(self,csv_data,label,range_list):
        """
            csv_data: csv data for eah dimension
            label: label for the motifs
            pos_list:[(start_1,end_1),(start_2,end_2)...]
        """
        x,y,z = list(),list(),list()
        for row in csv_data:
            row_data = row.split(",")
            x.append(float(row_data[0]))
            y.append(float(row_data[1]))
            z.append(float(row_data[2]))
        ts = {"accX":x,"accY":y,"accZ":z}

        mtf = Motif(ts)
        mtf_dict = mtf.get_motifs(label,range_list)
        self.set_motif_dict(mtf_dict)
        data_samples = self.motif_dict_adaptor(mtf_dict)

        return data_samples

    def plot_3_dim(self,csv_data):
        """
        Plot 3 dimensions of data
        """
        x,y,z = list(),list(),list()
        for row in csv_data:
            row_data = row.split(",")
            x.append(float(row_data[0]))
            y.append(float(row_data[1]))
            z.append(float(row_data[2]))
        
        show_all = True
        if show_all:
            x = np.array(x)
            y = np.array(y)
            z = np.array(z)

            # Find the interesting samples
            plt.figure(1)
            plt.subplot(311)
            line_x = plt.plot(range(len(x)),x)
            plt.subplot(312)
            line_y = plt.plot(range(len(y)),y)
            plt.subplot(313)
            line_z = plt.plot(range(len(z)),z)
            plt.xticks(np.arange(min(range(len(x))),max(range(len(x)))+1,200))
            plt.setp(line_x, color='r', linewidth=2.0)
            plt.setp(line_y, color='g', linewidth=2.0)
            plt.setp(line_z, color='b', linewidth=2.0)
            plt.show()
        else:
            data_sample_list = self.get_data_samples(self._csv_data,"id1",self._range_list)

            for each in self._motif_dict["id1"]:
                x = np.array(each["accX"])
                y = np.array(each["accY"])
                z = np.array(each["accZ"])

                # Find the interesting samples
                plt.figure(1)
                plt.subplot(311)
                line_x = plt.plot(x)
                plt.subplot(312)
                line_y = plt.plot(y)
                plt.subplot(313)
                line_z = plt.plot(z)

                plt.setp(line_x, color='r', linewidth=2.0)
                plt.setp(line_y, color='g', linewidth=2.0)
                plt.setp(line_z, color='b', linewidth=2.0)
                plt.show()
            
    def motif_dict_adaptor(self,mtf_dict):
        """
        Convert motif dict to a list of feautures:
        [
            {
                "accX":
                "accY":
                "accZ":
                "key":
            }
        ]
        """ 
        feature_list = list()
        for each_key in mtf_dict.keys():
            key_dict = {"key":each_key}
            for each_ele in mtf_dict[each_key]:
                one_sample = dict(key_dict.items()+each_ele.items())
                feature_list.append(one_sample)

        return feature_list


if __name__=="__main__":
    main()
