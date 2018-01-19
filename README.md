# trigger_daq
DAQ scripts for MMTP

## Receiving UDP Packets from the TP ##
* To run udp receiving:

   `<cmdline> python udpRecDesp_32bit.py`

* This is equipped to write files for data coming from TP output FIFOs 20-23.

  1. FIFO 21: GBT data stream from ADDC to TP
  2. FIFO 20: HIT data packets after TP converts GBT data to strip data + some slopes - header A1
  3. FIFO 23: TIME data from received external scintillator trigger
  4. FIFO 22: FIT data packets after TP reorders hit to VVUU-XXXX, finds coincidences in slope roads, and fits - header A3

(FIFO 23: FIND data after TP reorders hits to VVUU-XXXX and finds coincidences - header A2) - deprecated in TP FW as of 2017-05-10

* This writes raw files in the form of mmtp_test_FIFO#.dat

## Writing commands to the TP registers ##

   `<cmdline> python regWrite.py -a <address> -m <message> [-r] [-u] [--fe] <0 or 1> [--jtag] [--df] <"xxxx">`

* Various options for regWrite include:
  * [-r] Reset GBT transceiver connection  
  * [-u] Turn on GBT input to FIFOs  
  * [--fe] Enable/Disable TP output FIFOs, requires arg 0 or 1
  * [--jtag] Use jtag commands instead (has not been tested, requires vivado), calls tcl scripts  
  * [--df] Enables select TP output FIFOs, specified by four bits, e.g. "1111"

## TP Output Decoding ##

* Use decodeGBT_32bit.py (for raw GBT packets)
   
   `<cmdline> python decodeGBT_32bit.py [-h] [--ifile IFILE] [--ofile OFILE]`

* Use decodeHIT_32bit.py (for HIT packets)

   `<cmdline> python decodeHIT_32bit.py -i <inputfile> -o <outputfile> -r <run> [-f]`

* Use decodeFIND_32bit.py (for FIND packets)

   `<cmdline> python decodeFIND_32bit.py -i <inputfile> -o <outputfile> -r <run> [-f]`

* Use decodeTIME_32bit.py (for TIME packets)

   `<cmdline> python decodeTIME_32bit.py [-h] [--ifile IFILE] [--ofile OFILE]`
  
* Use decodeFIT_uvr.py (for FIT packets with new uvr road data format)

   `<cmdline> python decodeFIT_uvr.py -i <inputfile> -o <outputfile> -r <run> [-f] [--st] [--sl]`

* Various flags include:
  * [-i] Input file
  * [-o] Output file
  * [-f] Offsets (decode using assumed offsets in the TP firmware)
  * [--st] Include strip information in output
  * [--sl] Include slope information in output
  * [-r] Run number
  

* Use decodeFIT_32bit.py (for FIT packets, deprecated)

   `<cmdline> python decodeFIT_32bit.py -i <inputfile> -o <outputfile> -r <run> [-f] [-s]`

* Various flags include:
  * [-i] Input file
  * [-o] Output file
  * [-f] Offsets (decode using assumed offsets in the TP firmware)
  * [-s] Include extra slope information in output
  * [-r] Run number
  
