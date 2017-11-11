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
import sys
%matplotlib inline
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
#Since plate 11 is empty in Gender, Age and Hospital, new columns were created under those names and made
#empty for ease of the graph_production function
new_columns['Plate11']['Gender'] = ''
new_columns['Plate11']['Age'] = ''
new_columns['Plate11']['Hospital ']= ''

def graph_production(dic):
    '''Creates a graph with y being the value and x being the dilution'''
    # plots = dic['Plate 1'] #Considering only plate 1 in the dictionary for ease of testing
    for plates,vals in dic.items(): #Goes through all the plates in the created dictionary
        group = vals.groupby('patient_id') #Groups by the patient ID
        lst = ['PSMalpha2','ABA'] #For testing purposes, to see accuracy of plotting 3 different columns
        plotting_columns = vals.loc[:,'PSMalpha2':'Tetanus Toxoid'] #Saves all columns between to plotting_columns to plot
        cols_dropped_NaN = plotting_columns.dropna(axis=1,how='all') #Gets rid of all columns containing NaN
        col_to_plot = cols_dropped_NaN.columns #Extracts all the column names and saves it to a variable
        for i,j in group: #For loops through the grouped dataframe
            group2 = j.groupby('replicate') #Groups by the replicate (V1,V2,V3..)
            for l in col_to_plot: #Goes through the list of columns you want to print, lst is for testing, col_to_plot is the final list
                fig, ax = plt.subplots()
                for key,values in group2: #Goes through the keys (V1,V2,V3) and the corresponding values
                    values.plot('dilution', l, label = key,ax = ax, logy = True)
                plt.ylabel('Intensity',fontsize= 14,fontweight = 'bold') #Creates the ylabel
                plt.xlabel('Dilution',fontsize = 14,fontweight = 'bold') #Creates the xlabel
                if i != 'Standard': #If the sample is not a standard the title becomes the gender, age hospital and column, formatted
                    title = '{}({} {} {}) {}'.format(i,j.iloc[0]['Gender'],j.iloc[0]['Age'], j.iloc[0]['Hospital '],l )
                else: #else it just becomes the Standard and the column
                    title = '{} {}'.format('Standard',l)
                fig.suptitle(title,fontsize= 14,fontweight = 'bold')
    plt.show()




# graph_production(new_columns)

#step 5

def filefunc(filedata,coldata):
    '''decompose sample ID & fill in gap values'''
    # Read in Excel according tp filename & interested column name
    data = pd.read_excel(filedata, header=1, sheetname=None)
    # For the sheets in Excel
    for h in range(0, len(data)):
        # Empty lists to contain parse results & get Keys
        PIDl = []
        vl = []
        dill = []

        get_key = list(data.keys())[h]
        # Parse Sample ID
        for g in data[get_key].loc[:, coldata]:
            # Get Visit
            key1 = re.compile('[V][1-3]')
            key2 = key1.search(g)
            # Get Dilution
            key3 = re.compile('100*(?![1-9]|[ ][A-Z])')
            key4 = key3.search(g)
            # Get patient ID
            PIDf = re.compile(
                '\A(Standard[1-9]?|Healthy[ ][A-Z][A-Z].?|[0-9][0-9]+(?![ ][A-Z][A-Z]+)|.*(?=[ ][V][1-3]))')
            PID = PIDf.search(g)
            # Add matches to corresponding list if exists
            if key2 is not None:
                vl.append(key2.group())
            else:
                vl.append(np.nan)
            if key4 is not None:
                dill.append(key4.group())
            else:
                dill.append(np.nan)
            if PID is not None:
                PIDl.append(PID.group())
            else:
                PIDl.append(np.nan)
            # Purge cache
            re.purge()
        # Add parsed lists to dataframe
        data[get_key].insert(loc=1, column='PatientID', value=PIDl)
        data[get_key].insert(loc=2, column='Replicate/visit', value=vl)
        data[get_key].insert(loc=3, column='Dilution', value=dill)
        #fill in missing values in for hospital, Age & gender (plate 11 is missing all these data, so applied"try, except")
        try:
            data[get_key]['Hospital '] = data[get_key].groupby('PatientID')['Hospital '].ffill()
            data[get_key]['Age'] = data[get_key].groupby('PatientID')['Age'].ffill()
            data[get_key]['Gender'] = data[get_key].groupby('PatientID')['Gender'].ffill()
        except KeyError:
            pass
        #save each plate file as "plate *.txt"
        data[get_key].to_csv(get_key +'.txt',sep='\t')

# Step 5
filefunc('06222016 Staph Array Data.xlsx', 'Sample ID')
    
