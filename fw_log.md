MM TP firmware log
==================

Emoji          | Run          | Notes
:-------------:| :------------: | -------
:zap: | **3517** | **10 Mar - 14 Mar**
.     | :wrench: | Add roads (1 VMM per road)
.     | :wrench: | Include hits from neighboring roads
.     | :wrench: | Set slope equal to the strip
.     | :wrench: | Add offsets to strips: 64 (X), 71 (U), 58 (V)
.     | :wrench: | Assign BCID to hits as they arrive from ADDC
.     | :wrench: | Add GBT buffer which is 15 BC deep
.     | :wrench: | Overhaul output streams
.     | :wrench: | Overhaul synthesis/implementation approach
:zap: | **3518/19** | **21 Apr - 01 Apr**
.     | :ant:    | GBT decoding fails timing: lots of strip data corruption
.     | :ant:    | Frequent slope corruption due to poorly aligned slope calculation
.     | :wrench: | Add clock cycle to decoding
.     | :wrench: | Change slope from daisy-chain adder to tree adder
:zap: | **3520** | **02 May - 04 May**
.     | :ant:    | UV offsets flipped
.     | :ant:    | unpredictable strip corruption
.     | :wrench: | correct UV offsets
.     | :wrench: | set slope = strip*X a la ATLAS, except with X=1
.     | :wrench: | change strip collection strategy from "overwrite" to "no overwrite"
.     | :wrench: | add scintillator timestamp output stream (replaces finder)
:zap: | **3521** | **05 May - 08 May**
:zap: | **3522/23** | **11 May - 27 May**

