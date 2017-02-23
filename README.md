# trigger_daq
DAQ scripts for MMTP

## Receiving UDP Packets from the TP ##
*To run udp receiving:

   `<cmdline> python udpRecDesp_32bit.py`

*This is equipped to write files for data coming from TP output FIFOs 20-23.  
*FIFO 21: GBT data stream from ADDC to TP  
*FIFO 20: HIT data packets after TP converts GBT data to strip data + some slopes - header A1  
*FIFO 23: FIND data after TP reorders hits to VVUU-XXXX and finds coincidences - header A2  
*FIFO 22: FIT data (currently not working)  
   
*This writes raw files in the form of mmtp_test_FIFO#.dat

## Writing commands to the TP registers ##

   `<cmdline> python regWrite.py -a <address> -m <message> [-r] [-u] [--fe] <0 or 1> [--jtag]`

*Various options for regWrite include:  
*[-r] Reset GBT transceiver connection  
*[-u] Turn on UDP output from FIFO 21  
*[--fe] Enable/Disable TP input FIFOs receiving GBT packets from ADDC, requires arg 0 or 1
*[--jtag] Use jtag commands instead (has not been tested, requires vivado), calls tcl scripts  

## TP Output Decoding ##

*Use decodeGBT_32bit.py (for raw GBT packets)

*Use decodeHIT_32bit.py (for HIT packets)

*Use decodeFIND_32bit.py (for FIND packets)


*To run:

   `<cmdline> python decodeGBT_32bit.py -i inputfile -o outputfile`
