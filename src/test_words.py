import os
import sys
import subprocess
from subprocess import call
import shlex

def main():
    proc = subprocess.Popen(['cat','/usr/share/dict/words'], stdout=subprocess.PIPE)
    result = proc.stdout.read()
    result = result.split("\n")
    filter = ['e','t','a','o','i','n','s','h','r','d']
    goody = list()
    counter = 0
    
    for each_word in result:
        for each_letter in each_word:
            if each_letter in filter:
                counter += 1
        if counter == len(each_word):
            goody.append(each_word)
        counter = 0
    
    output_file = open('freq_words.txt','w')
    for each_goody in goody:
        output_file.write(each_goody+"\r\n")
    output_file.close()

if __name__=="__main__":
    main()
