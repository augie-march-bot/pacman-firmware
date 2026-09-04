#! /bin/bash

cp ghdl/*/*.vhd ./vivado/src/hdl
cp -r ghdl/hardware/* ./vivado/src/hdl

#include the ASIC digital core stub by defaul:
cp ghdl/asic_emu/stub/*.vhd ./vivado/src/hdl
