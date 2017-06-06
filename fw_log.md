MM TP firmware log
==================

Emoji          | Run          | Notes
:-------------:| :------------: | -------
:zap: | **3517** | ** 10/3 - 14/3**
.     | :wrench: | Add roads (1 VMM per road)
.     | :wrench: | Include hits from neighboring roads
.     | :wrench: | Set slope equal to the strip
.     | :wrench: | Add offsets to strips: 64 (X), 71 (U), 58 (V)
.     | :wrench: | Assign BCID to hits as they arrive from ADDC
.     | :wrench: | Add GBT buffer which is 15 BC deep
.     | :wrench: | Overhaul output streams
.     | :wrench: | Overhaul synthesis/implementation approach
:zap: | **3518/19** | **21/4 - 01/5**
.     | :ant:    | GBT decoding fails timing: lots of strip data corruption
.     | :ant:    | Frequent slope corruption due to poorly aligned slope calculation
.     | :wrench: | Add clock cycle to decoding
.     | :wrench: | Change slope from daisy-chain adder to tree adder
:zap: | **3520** | **02/5 - 04/5**
.     | :ant:    | UV offsets flipped
.     | :ant:    | unpredictable strip corruption
.     | :wrench: | correct UV offsets
.     | :wrench: | set slope = strip*X a la ATLAS, except with X=1
.     | :wrench: | change strip collection strategy from "overwrite" to "no overwrite"
.     | :wrench: | add scintillator timestamp output stream (replaces finder)
:zap: | **3521** | **05/5 - 08/5**
:zap: | **3522/23** | **11/5 - 27/5**

