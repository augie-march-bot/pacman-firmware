#
# hardware.tcl  run synthesis,implementation,annd write bitstream, then export.
#

set proj_name "pacman-fw"

set origin_dir [file dirname [info script]]/..

open_project $origin_dir/$proj_name/$proj_name.xpr

open_bd_design [get_files pacman-fw/pacman-fw.srcs/sources_1/bd/zsys/zsys.bd]

# report the top-level address map:
set fp [open "../reports/address_map.txt" w]
foreach seg [get_bd_addr_segs -hierarchical] {
    set offset [get_property OFFSET $seg]
    set range  [get_property RANGE  $seg]
    puts $fp [format "%-60s offset=%-12s range=%-10s" $seg $offset $range]
}
close $fp




