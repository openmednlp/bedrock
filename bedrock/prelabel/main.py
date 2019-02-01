import pandas as pd
import os
import json
import re
import csv

# Either one can load a folder containing json files (= folder)
# or one json file (= file)
folder = ''
file = ''
# If you want to do regex in a Patho excel file you need the path to that file
filename = ''
# Finally you need a regex

# As an alternative you can let the user directly write the upper 4 Parameters
# into the console instead of hardcoding it in here

# filename = input('Path to the excel file (case Patho): ')
# folder = input('Path to the folder with the json files (Radio case): ')
# file = input('Path to one single json file: ')
# regex = input('Choose a pattern to find (eg. r\'(TNM)\'): ')


def main_patho(filename, regex):
    
    excel_file = pd.read_excel(filename)
    klin = excel_file['E_KlinischeAngaben']
    diag = excel_file['R_Diagnose']
    zusf = excel_file['R_Zusammenfassung']
    diag_b = excel_file['R_Diagnosebeschrieb']
    komm = excel_file['R_Kommentar']
    frage = excel_file['R_FragenandenKliniker']

    for i in range(0, len(klin)):
        summe = (str(klin[i]) + str(diag[i]) + str(zusf[i]) +
                 str(diag_b[i]) + str(komm[i]) + str(frage[i]))
            
        vec, match = findpattern(regex, summe)
