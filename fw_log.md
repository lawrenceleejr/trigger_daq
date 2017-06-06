MM TP firmware log
==================

Emoji          | Event         | Dates
:-------------:| :------------ |:-------:
:zap:    | **Run 3517**  | 10 March - 14 March
:wrench: | Add roads (1 VMM per road)
:wrench: | Include hits from neighboring roads
:wrench: | Set slope equal to the strip
:wrench: | Add offsets to strips: 64 (X), 71 (U), 58 (V)
:wrench: | Assign BCID to hits as they arrive from ADDC
:wrench: | Add GBT buffer which is 15 BC deep
:wrench: | Overhaul output streams
:wrench: | Overhaul synthesis/implementation approach
:zap:   | Run 3518-3519 | 21 April - 25 April - 01 May
:ant: :wrench: | - GBT decoding fails timing: lots of strip data corruption <br>- Add clock cycle to decoding to fix this <br>- Frequent slope corruption due to unaligned slope calculation <br>- Change slope from daisy-chain adder to tree adder | 
:zap:    | Run 3520      | 02 May - 04 May
:ant:    | UV offsets flipped | 
:ant:    | occasional strip corruption |
:wrench: | correct UV offsets |
:wrench: | set slope = strip*X a la ATLAS, except with X=1 |
:wrench: | change strip collection strategy from "overwrite" to "no overwrite" |
:wrench: | add scintillator timestamp output stream (replaces finder) | 
-------- | ---- | ----
:zap: | Run 3521      | 05 May - 08 May
:zap: | Run 3522-3523 | 11 May - 18 May - 27 May

