# trigger_daq
daq scripts for MMTP

## How to use ##
*To run udp receiving:

   `<cmdline> python udpRecDesp.py`

*To decode, use either decodeGBT.py or decodeGBT_32bit.py, depending on the format of your raw data file. The data collected by udpRecDesp.py should be decoded using decodeGBT.py.

*To run:

   `<cmdline> python decodeGBT.py -i inputfile -o outputfile`