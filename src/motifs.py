import os
import sys

class Motif:
    """
    Motif discovery for the time series data
    """

    def __init__(self,ts):
        """
        ts: multi-dimensional time series data, each dimension is represented by a list, 
        all dimensional lists together forms a dictionary of lists
        _ts:[
                "accX":[1,2,3,4...],
                "accY":[1,2,3,4...],
            ]
        """
        self._ts = ts

        """
        _motif_dict:{
            "motif_1":[{
                        "accX":[1,2,3,.....]
                        "axxY":[...........]
                  },
                  {
                        "accX":[1,2,3....]
                        "accY":[...........]
                  },
                  ... ...
                  ],
            "motif_2":
                    ...
                    ...
        }
        """
        self._motif_dict = dict()

    def get_motifs(self,motif_id,start_end_list):
        """
        start_len_list:[(start,len),(another_start,another_len)...]
        """
        # For now, just get the motifs for existing points
        if not self._motif_dict.has_key(motif_id):
            self._motif_dict.update({motif_id:list()})
        for each in start_end_list:
            self._motif_dict[motif_id].append(self.sub_ts(each[0],each[1]))

        return self._motif_dict
    
    def sub_ts(self,start,end):
        """
        Retrieve the time seires data into a dict sample
        sample_ts:{
                        "accX":[1,2,3,4...]
                        "accY":[1,2,3,4....]
                  }
        """
        sample_ts = dict()
        for each in self._ts.keys():
            sample_ts.update({each:self._ts[each][start:end]})

        return sample_ts

    def generate_motifs(self):
        """
        return a list of [(starts,len)...]
        """
        print "TODO"

