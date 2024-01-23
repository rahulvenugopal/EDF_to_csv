# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:49:24 2023
- Batch convert the scored EDF files to csv files for inter rater comparison
- At times there will be markers of Body movement which is marked as W here
- It will spit out a hypnogram image as well

@author: Rahul Venugopal
"""

#%% Loading libraries
import mne
import numpy as np
import os
import yasa
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilenames
from tkinter import Tk
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

# Opening a UI asking to select scored EDF files
scored_files = askopenfilenames(title = "Select Scored files",
                              filetypes = (("EDF file","*.edf"),
                              ('All files', '*.*')))

for files in range(len(scored_files)):
    hypno_data = mne.read_annotations(scored_files[files])
    
    # onset column is start of an epoch and duration tells us how long
    hypnogram_annot = hypno_data.to_data_frame()

    # change the duration column into epochs count
    hypnogram_annot.duration = hypnogram_annot.duration/30

    # convert the onset column to epoch number
    timestamps = hypnogram_annot.onset.dt.strftime("%m/%d/%Y, %H:%M:%S")

    only_time = []
    for entries in timestamps:
        times = entries.split()[1]
        only_time.append(times.split(':'))

    # converting hour month and seconds as epoch number
    epochs_start = []
    for entries in only_time:
        hh = int(entries[0]) * 120
        mm = int(entries[1]) * 2
        ss = int(entries[2])/ 30
        epochs_start.append(int(hh+mm+ss))

    # replacing the onset column with start of epoch
    hypnogram_annot['onset'] = epochs_start
    
    # keep the description column neat
    just_labels = []
    
    # Building a check for any other marker in hypnogram file
    # Spotted movement marker in some files
    # Checking  there are movement markers and converting them to W marker

    # In the below for and if loop block, we can add any other anomalous marker
    # Currently we have acccounted only for Movement time into W
    # Use elif to add more criteria
    for entries in hypnogram_annot.description:
        if entries == 'Movement time':
            just_labels.append('W')
        else:
            just_labels.append(entries.split()[2]) # Some sleep files had Sleep Stage W, hence picked 2nd entry (third)

    # replacing the description column with just_labels
    hypnogram_annot['description'] = just_labels

    # we need only the duration column and description column to recreate hypnogram
    # just reapeat duration times the label in description column
    hypno_30s = []
    for stages in range(len(hypnogram_annot)):
        for repetitions in range(int(hypnogram_annot.duration[stages])):
            hypno_30s.append(hypnogram_annot.description[stages])

    # converting list to numpy array
    hypno_30s = np.asarray(hypno_30s)

    # converting string array into int array using yasa
    # hypno_30s = yasa.hypno_str_to_int(hypno_30s)
    
    fname = os.path.basename(scored_files[files])[:-4] + '.csv'

    # spit out the sleep stage sequences as a text file
    np.savetxt(fname,
               hypno_30s,
               delimiter = ',',
               fmt='%s') # you may change this to s for string
    
    # converting W and R into 0 and 4 | In case any renaming is needed
    hypno_30s = [s.replace('W', '0') for s in hypno_30s]
    hypno_30s = [s.replace('R', '4') for s in hypno_30s]
    hypno_30s = [s.replace('N1', '1') for s in hypno_30s]
    hypno_30s = [s.replace('N2', '2') for s in hypno_30s]
    hypno_30s = [s.replace('N3', '3') for s in hypno_30s]
    
    # Plot the hypnogram and save as image
    # plot hypnogram
    yasa.plot_hypnogram(hypno_30s,
                        lw = 1,
                        figsize=(25, 2.5))
    plt.tight_layout()
    plt.savefig(os.path.basename(scored_files[files])[:-4] + '_hypno.png',
                dpi = 600)
    plt.close()
