# Displays EEG Tracings for Channel 1, Channel 2 and the Difference Channel (Ch2 - Ch1)

## **Update the CSV filename and recording start time**

In `main()`, update the filename to match the .csv file and set the recording start time (HH, MM, SS) of the .csv file:

```
filename = 'record-[YYYY.MM.DD-HH.MM.SS].csv'
hour, minute, second = HH, MM, SS
```

## **Update the bandpass filter settings**

The EEG bandpass filter is set in `plot_time_slice_raw()`. Typical filter_bandpass_max=15 or 30

```
plot_time_slice_raw(
    time_raw,
    channel1_raw,
    channel2_raw,
    starting_time=starting_time,
    filter_bandpass_min=1,
    filter_bandpass_max=15
)
```

