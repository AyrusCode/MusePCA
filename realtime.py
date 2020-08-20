# -*- coding: utf-8 -*-
"""
Exercise 1b: A neurofeedback interface (multi-channel)
======================================================
Description:
In this exercise, we'll try and play around with a simple interface that
receives EEG from multiple electrodes, computes standard frequency band
powers and displays both the raw signals and the features.
"""
from eegnb
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop, StreamInfo, StreamOutlet  # Module to receive EEG data
import torch
from torch import nn
import pygame
from pandas import DataFrame
from psychopy import visual, core, event, sound

import bci_workshop_tools as BCIw  # Our own functions for the workshop

nntrace = torch.jit.load('musepcann_trace.pth')

class Band:
    Delta = 0
    Theta = 1
    Alpha = 2
    Beta = 3
    
if __name__ == "__main__":

    """ 1. CONNECT TO EEG STREAM """

    # Search for active LSL stream
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    # Set active EEG stream to inlet and apply time correction
    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    eeg_time_correction = inlet.time_correction()

    # Get the stream info, description, sampling frequency, number of channels
    info = inlet.info()
    description = info.desc()
    fs = int(info.nominal_srate())
    n_channels = info.channel_count()

    # Get names of all channels
    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]
    for i in range(1, n_channels):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))

    """ 2. SET EXPERIMENTAL PARAMETERS """

    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    buffer_length = 3

    # Length of the epochs used to compute the FFT (in seconds)
    epoch_length = 0.8

    # Amount of overlap between two consecutive epochs (in seconds)
    overlap_length = -0.2

    # Amount to 'shift' the start of each next consecutive epoch
    shift_length = epoch_length - overlap_length

    # Index of the channel (electrode) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    index_channel = [0, 1, 2, 3]
    # Name of our channel for plotting purposes
    ch_names = [ch_names[i] for i in index_channel]
    n_channels = len(index_channel)


    """3. INITIALIZE BUFFERS """

    # Initialize raw EEG data buffer (for plotting)
    eeg_buffer = np.zeros((int(fs * buffer_length), n_channels))
    filter_state = None  # for use with the notch filter

    # Compute the number of epochs in "buffer_length" (used for plotting)
    n_win_test = int(np.floor((buffer_length - epoch_length) /
                              shift_length + 1))

    # Initialize the feature data buffer (for plotting)
    # feat_buffer = np.zeros((n_win_test, len(feature_names)))

    # Initialize the plots
    # plotter_eeg = BCIw.DataPlotter(fs * buffer_length, ch_names, fs)
    # plotter_feat = BCIw.DataPlotter(n_win_test, feature_names,
    #                           1 / shift_length)
    
    # Initialize audio
    aud1 = sound.Sound(440,secs=0.07)#, octave=5, sampleRate=44100, secs=0.07)
    aud1.setVolume(0.8)
    

    """ 3. GET DATA """

    # The try/except structure allows to quit the while loop by aborting the
    # script with <Ctrl-C>
    print('Press Ctrl-C in the console to break the while loop.')

    try:
        # The following loop does what we see in the diagram of Exercise 1:
        # acquire data, compute features, visualize raw EEG and the features
        while True:

            """ 3.1 ACQUIRE DATA """
            # Beep
            aud1.stop()        
            aud1.play()
            
            # Obtain EEG data from the LSL stream
            eeg_data, timestamp = inlet.pull_chunk(
                    timeout=1, max_samples=int(shift_length * fs))

            # Only keep the channel we're interested in
            ch_data = np.array(eeg_data)[:, index_channel]

            # Update EEG buffer
            eeg_buffer, filter_state = BCIw.update_buffer(
                    eeg_buffer, ch_data, notch=True,
                    filter_state=filter_state)

            """ 3.2 COMPUTE FEATURES """
            # Get newest samples from the buffer
            data_epoch = utils.get_last_data(eeg_buffer,
                                             epoch_length * fs)

            # Classify Epoch
            example = np.expand_dims(data_epoch, axis=0)
            example = torch.from_numpy(example)
            example = example.type(torch.FloatTensor)
            output = nntrace(example)
            
            if output[0,1] > output[0,0]:
                label = "Up"
            else:
                label = "Nothing"
                
            print(label)

    except KeyboardInterrupt:

        print('Closing!')