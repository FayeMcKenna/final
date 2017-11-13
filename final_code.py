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

# step 5 function

data = pd.ExcelFile('06222016 Staph Array Data.xlsx')

VISIT_ID_REGEX = re.compile('[V][1-3]') #compile visits
PID_REGEX = re.compile('\A(Standard[1-9]?|Healthy[ ][A-Z][A-Z].?|[0-9][0-9]+(?![ ][A-Z][A-Z]+)|.*(?=[ ][V][1-3]))') #compile PID
DILUTION_REGEX = re.compile('100*(?![1-9]|[A-Z][ ])') #compile dilusion

def populate_empty_cells(sheet_data): #populate empty cells
    try:
        sheet_data['Hospital '] = sheet_data.groupby('PatientID')['Hospital '].ffill() 
        sheet_data['Age'] = sheet_data.groupby('PatientID')['Age'].ffill()
        sheet_data['Gender'] = sheet_data.groupby('PatientID')['Gender'].ffill()
    except KeyError:
        pass

def parse_visit(visit, PIDs, visit_ids, dilutions): #parse by visits
    visit_id = VISIT_ID_REGEX.search(visit)
    visit_result = visit_id.group() if visit_id else np.nan
    visit_ids.append(visit_result)

    PID = PID_REGEX.search(visit) #check matches PID
    PID_result = PID.group() if PID else np.nan
    PIDs.append(PID_result)

    dilution = DILUTION_REGEX.search(visit) #check matches dilusion
    dilution_result = dilution.group() if dilution else np.nan
    dilutions.append(dilution_result)

    re.purge() # purge function 

def update_sheet(sheet_name, sheet_data, column_header): #update sheet
    PIDs = []
    visit_ids = []
    dilutions = [] 

    for visit in sheet_data.loc[:, column_header]: # Get Visit
        parse_visit(visit, PIDs, visit_ids, dilutions)

    sheet_data.insert(loc=1, column='PatientID', value=PIDs) #insert each
    sheet_data.insert(loc=2, column='Replicate/visit', value=visit_ids)
    sheet_data.insert(loc=3, column='Dilution', value=dilutions)

    populate_empty_cells(sheet_data)
    sheet_data.to_csv(sheet_name +'.txt',sep='\t')


def update_spreadsheet(file_name, column_header): #update spreadsheet
    sheets = pd.read_excel(file_name, header=1, sheet_name=None)
    for sheet_name, sheet_data in sheets.items(): # iterate over keys/values at the same time
        update_sheet(sheet_name, sheet_data, column_header)

def main():
    file_name = '06222016 Staph Array Data.xlsx'
    column_to_parse = 'Sample ID'
    update_spreadsheet(file_name, column_to_parse)
    print(file_name + " updated succesfully")

    
