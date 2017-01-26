#taken from nsw elx svn 


    set filename "outFifo_21_8.txt"
    set outFifo_21_8 [open $filename "w"]

    set filename "outFifo_22_12.txt"
    set outFifo_22_12 [open $filename "w"]

    create_hw_axi_txn fifoFlags -address 0x04 -type read  [get_hw_axis hw_axi_1]
    run_hw_axi  [get_hw_axi_txns]
    set fifo_report [report_hw_axi_txn fifoFlags ]
    set lst [regexp -all -inline {\S+} $fifo_report]
    set flags [lindex $lst 1]
    delete_hw_axi_txn [get_hw_axi_txns *]
    create_hw_axi_txn read_22_12 -address 0x88 -type read  -size 32 -len 12 -burst fixed  [get_hw_axis hw_axi_1]
    create_hw_axi_txn read_21_8 -address 0x84 -type read  -size 32 -len 8 -burst fixed  [get_hw_axis hw_axi_1]
    create_hw_axi_txn fifoFlags -address 0x04 -type read  [get_hw_axis hw_axi_1]




while  {[expr 0x$flags & 0x14] != 0x14} {
if {[expr 0x$flags & 0x4] == 0x0} {
    run_hw_axi  [get_hw_axi_txns read_21_8]
    set rd_report [report_hw_axi_txn read_21_8 -w 128]
    set rd_report_lst [regexp -all -inline {\S+} $rd_report]
    puts  $outFifo_21_8 [lrange $rd_report  1 end]
}

if {[expr 0x$flags & 0x10] == 0x0} {
    run_hw_axi -verbose  [get_hw_axi_txns read_22_12]
    set rd_report [report_hw_axi_txn read_22_12 -w 384]
    puts $rd_report
    set rd_report_lst [regexp -all -inline {\S+} $rd_report]
    puts  $outFifo_22_12 [lrange $rd_report  1 end]
}

    run_hw_axi  [get_hw_axi_txns fifoFlags]
    set fifo_report [report_hw_axi_txn fifoFlags ]
    set lst [regexp -all -inline {\S+} $fifo_report]
    set flags [lindex $lst 1]
puts $flags
}
delete_hw_axi_txn [get_hw_axi_txns *]

close $outFifo_21_8
close $outFifo_22_12
