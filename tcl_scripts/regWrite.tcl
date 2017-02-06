# Attempting to open ADDC links via TCL

# A. Wang, last edited Feb 6, 2017

reset_hw_axi [get_hw_axis]

set txn_addr [lindex $argv 0]
set txn_data [lindex $argv 1]

puts "Writing $txn_data to $txn_addr"

create_hw_axi_txn addc_ena -type WRITE -address $txn_addr -data $txn_data -size 32 -len 11 -burst fixed [get_hw_axis hw_axi_1]

run_hw_axi -verbose [get_hw_axi_txns]
delete_hw_axi_txn [get_hw_axi_txns *]
