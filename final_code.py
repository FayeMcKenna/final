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


def graph_production(dic):
    '''Creates a graph with y being the value and x being the dilution'''
    plots = dic['Plate 1'] #Considering only plate 1 in the dictionary for ease of testing
    group = plots.groupby('patient_id') #Groups by the patient ID
    lst = ['PSMalpha2','ABA','PSMalpha3'] #For testing purposes, to see accuracy of plotting 3 different columns
    plotting_columns = plots.loc[:,'PSMalpha2':'Tetanus Toxoid'] #Saves all columns between to plotting_columns to plot
    cols_dropped_NaN = plotting_columns.dropna(axis=1,how='all') #Gets rid of all columns containing NaN
    col_to_plot = cols_dropped_NaN.columns #Extracts all the column names and saves it to a variable
    for i,j in group: #For loops through the grouped dataframe
        group2 = j.groupby('replicate') #Groups by the replicate (V1,V2,V3..)
        for key,values in group2: #Goes through the keys (V1,V2,V3) and the corresponding values
            for l in lst: #Goes through the list of columns you want to print, lst is for testing, col_to_plot is the final list
                fig, ax = plt.subplots()
                group2.plot(values['dilution'], l,label = key,ax = ax, logy = True)
                plt.ylabel('Intensity',fontsize= 14,fontweight = 'bold')
                plt.xlabel('Dilution',fontsize = 14,fontweight = 'bold')
                if i != 'Standard': #If the sample is not a standard the title becomes the gender, age and hospital, formatted
                    title = '{}({} {} {}) {}'.format(i,j.iloc[0]['Gender'],j.iloc[0]['Age'], j.iloc[0]['Hospital '],l )
                else: #else it just becomes the Standard
                    title = 'Standard'
                fig.suptitle(title,fontsize= 14,fontweight = 'bold')
    plt.show()

# Things to fix before moving on
# Fix the legends, instead of the correct replciates i.e V1,V2,V3 it prints the same thing over and  over i.e V1 V1 V1
# also sometimes it prints the name of the column in the legends.

# Once the legend thing is figured out then make another function that goes through all of the plates and applies
# the graph_production function on them




graph_production(new_columns)

# Step5 function
def filefunc(filedata,coldata):
    data = pd.read_excel(filedata, header=1, sheetname=None) #read in data excel sep filename column name
    for h in range(0, len(data)): #for each sheet in excel
        PIDl = [] #empty list to get PIDL
        vl = [] #empty list to get vl
        dill = [] #empty list to get dill

        get_key = list(data.keys())[h] #go through sample IDs
        for g in data[get_key].loc[:, coldata]: #for the visit in the data
            key1 = re.compile('[V][1-3]') #get the dilusion
            key2 = key1.search(g)
            key3 = re.compile('100*(?![1-9]|[ ][A-Z])')
            key4 = key3.search(g) #get the patient ID
            key5 = re.compile(
                '\A(Standard[1-9]?|Healthy[ ][A-Z][A-Z].?|[0-9][0-9]+(?![ ][A-Z][A-Z]+)|.*(?=[ ][V][1-3]))')
            key6 = key5.search(g) #if exists add match to list
            if key2 is not None:
                key2.append(key2.group())
            else:
                key2.append(np.nan)
            if key4 is not None:
                key4.append(key4.group())
            else:
                key4.append(np.nan)
            if key6 is not None:
                key6.append(key6.group())
            else:
                key6.append(np.nan)
            re.purge() #purge 
        data[get_key].insert(loc=1, column='PatientID', value=PIDl) #add lists to data df
        data[get_key].insert(loc=2, column='Replicate/visit', value=vl)
        data[get_key].insert(loc=3, column='Dilution', value=dill)
        try: #try to get missing data
            data[get_key]['Hospital '] = data[get_key].groupby('PatientID')['Hospital '].ffill()
            data[get_key]['Age'] = data[get_key].groupby('PatientID')['Age'].ffill()
            data[get_key]['Gender'] = data[get_key].groupby('PatientID')['Gender'].ffill()
        except KeyError:
            pass #save each file as txt
        data[get_key].to_csv(get_key +'.txt',sep='\t')

#run function
filefunc('Assignment4/06222016 Staph Array Data.xlsx', 'sampleid') # whats our sampid name variable?
