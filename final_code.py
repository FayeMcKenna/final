#course final
#psuedo code

#data sheet plot dilusion versus intensity from staph array data via line graph
#1 read sheet in via panda
#2 parse first column into 3 separate columns and handle diff formatting (PatientID, Replicate/visit, Dilution)
    #import regular expressions 're' lib
#3 Line plot, one line per visit

from collections import defaultdict
import pandas as pd
import re
import numpy as np
import xlrd
import matplotlib.pyplot as plt
data = pd.ExcelFile('06222016 Staph Array Data.xlsx')

sheets = {}
for sheet in data.sheet_names:
    sheets[sheet] = data.parse(sheet)

def col_names(dic):
    '''Goes through every sheet and turns the first row into the column name'''
    new_dic = {}
    for k,v in dic.items():
        new_head = v.iloc[0]
        v = v[1:]
        v.columns = new_head
        new_dic[k] = v
    return new_dic
new_sheets = col_names(sheets)

def matching(dic):
    '''iterates through the dictionary and matches each sample ID with a regular expression which is then split
    and made into new columns'''
    final_dic = {}
    for k,v in dic.items():
        patient = []
        rep = []
        dil = []
        for i in v['Sample ID']:
            if re.match(r'(\D+)\s(\d+)',i):
                splitted = i.split()
                patient.append(splitted[0])
                dil.append(splitted[1])
                rep.append('NA')
            elif re.match(r'(\d+)\s(.\d)\s(\d+)',i):
                splitted = i.split()
                patient.append(splitted[0])
                rep.append(splitted[1])
                dil.append(splitted[2])
            elif re.match(r'(\D+)(\d)',i):
                if len(i.split()) > 1:
                    splitted = i.split()
                    patient.append(splitted[0])
                    rep.append(splitted[1])
                    dil.append(splitted[2])
                else:
                    patient.append(i[:-1])
                    dil.append(i[-1])
                    rep.append('NA')
            elif re.match(r'(\d+)\s+(\d+)', i):
                splitted = i.split()
                patient.append(splitted[0])
                rep.append('NA')
                dil.append(splitted[-1])
            elif re.match(r'(\d+)\s(\D\d)\s+(\d+)',i):
                splitted = i.split()
                patient.append(splitted[0])
                rep.append(splitted[1])
                dil.append(splitted[2])
            elif re.match(r'(\d+\D+)\s(\D+\d?)\s(\d+)',i):
                splitted = i.split()
                Id = ' '.join(splitted[0:3])
                patient.append(Id)
                rep.append(splitted[-2])
                dil.append(splitted[-1])
            else:
                splitted = i.split()
                patient.append(splitted[0])
                rep.append(splitted[-1][:2])
                dil.append(splitted[-1][2:])
        v['patient_id'] = patient
        v['replicate'] = rep
        v['dilution'] = dil
        final_dic[k] = v
    return final_dic

new_columns = matching(new_sheets)



def this_is_it(dic):
    plots = dic['Plate 1']
    # pats = set(plots['patient_id'])
    group = plots.groupby('patient_id')
    list_of_columns = plots.columns
    # print(list_of_columns)
    title = ['Hospital ','Age','Gender']
    for i,j in group:
        group2 = j.groupby('replicate')
        fig,ax = plt.subplots()
        for key,values in group2:
            group2.plot(values['dilution'], 'ABA', label = key,ax = ax, logy = True)
            # print(i, '-------------',list(j['ABA']), j['Age'][:1])
            plt.ylabel('Intensity',fontsize= 14,fontweight = 'bold')
            print(list_of_columns)
            plt.xlabel('Dilution',fontsize = 14,fontweight = 'bold')
            x = '{}({} {} {}) {}'.format(i,j.iloc[0]['Gender'],j.iloc[0]['Age'], j.iloc[0]['Hospital '],'ABA' )
            fig.suptitle(x,fontsize= 14,fontweight = 'bold')
    plt.show()


#To do list
# Get the title figues right
# Make it log scale
# Fix the legend
#
