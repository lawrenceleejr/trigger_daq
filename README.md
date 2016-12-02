# trigger_daq
daq scripts for MMTP

## How to use ##
*To run udp receiving:

   `<cmdline> python udpRecDesp_32bit.py`

*To write to the TP register:

   `<cmdline> python regWrite.py -a <address> -m <message>`

*To decode your files, use:

-decodeGBT_32bit.py (for raw GBT packets)

-decodeHIT_32bit.py (for decoded GBT packets)

-decodeFIND_32bit.py (for finder packets)


*To run:

   `<cmdline> python decodeGBT_32bit.py -i inputfile -o outputfile`