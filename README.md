# trigger_daq
daq scripts for MMTP

## How to use ##
*To run udp receiving:

   `<cmdline> python udpRecDesp_32bit.py`

*To decode your files, use:

-decodeGBT_32bit.py (for raw GBT packets)

-decodeHIT_32bit.py (for decoded GBT packets)

-decodeFIND_32bit.py (for finder packets)

Notice that there are 32bit versions and regular versions, depending on the format of your raw data file. Only the 32bit versions are up to date right now.

*To run:

   `<cmdline> python decodeGBT_32bit.py -i inputfile -o outputfile`