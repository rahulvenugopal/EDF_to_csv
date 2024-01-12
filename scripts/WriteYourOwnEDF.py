# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 20:45:46 2024
- Tutorial on creating edf files based on https://github.com/the-siesta-group/edfio

@author: Rahul Venugopal
"""
#%% Import libraries
import datetime
import numpy as np

# Do
# pip install edfio
# once

from edfio import Edf, EdfSignal, Patient, Recording, EdfAnnotation, read_edf

#%% Create one channel with
# sf = 25 Hz
# Channel name = Cz
# Physical dimension = uV
# Some meta info about patient name, sex, birthday yada yada yadaaa
# We also learn how to add one more channel which may or may not be EEG
# Even important with another sampling frequency

# Adding annotations as well

edf = Edf(
    [
        EdfSignal(
            np.random.randn(30 * 256),
            sampling_frequency=256,
            label="Cz",
            transducer_type="AgAgCl electrode",
            physical_dimension="uV",
            prefiltering="HP:0.1Hz LP:75Hz",
        ),
        EdfSignal(np.random.randn(30), sampling_frequency=1, label="Body Temp"),
    ],

    annotations=[
        EdfAnnotation(1, None, "Trial start"),
        EdfAnnotation(1.5, None, "Stimulus"),
        EdfAnnotation(2.5, 2, "Movement"),
        EdfAnnotation(10, None, "Trial end"),
    ],
    patient=Patient(
        code="MCH-0234567",
        sex="F",
        birthdate=datetime.date(1951, 5, 2),
        name="Haagse_Harry",
    ),
    starttime=datetime.time(11, 25)

)

# Remember Python starts reading from 0. So 1 is actually second channel
edf.signals[1].transducer_type = "Thermistor"
edf.signals[1].physical_dimension = "degC"
edf.recording = Recording(
    startdate=datetime.date(2002, 2, 2),
    hospital_administration_code="EMG561",
    investigator_technician_code="BK/JOP",
    equipment_code="Sony",
)

# Write it
edf.write("example.edf")

#%% Oops, I made a mistake and want to change the name of the channel

edf.get_signal("Body Temp").label = "Body Temperature"

# I want to throw away all movements annotations now
edf.drop_annotations("Movement")

#%% I want to remove some channels either by labels or index
# single signal by label
edf.drop_signals("Body Temperature")

# multiple signals by label
edf.drop_signals(["Cz", "C4"])

# multiple signals by index
edf.drop_signals([0, 1])

#%% I want to slice EDF based on time or events
# by seconds
edf.slice_between_seconds(5, 15)

# by annotation texts
edf.slice_between_annotations("Trial start", "Trial end")

#%% I am going to upload all EDFs to a repository (Yayyy, open source)

edf = read_edf("example.edf")
edf.anonymize()
edf.write("example_anonymized.edf")