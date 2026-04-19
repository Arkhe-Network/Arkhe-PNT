# synth_tau_soc.tcl – Síntese do TAU SoC Wrapper v1.2
# Target: AMD Versal AI Core (xcvc1902-vsva2197-2MP-e-S)

set project_name tau_soc
set top_module   tau_soc_wrapper_v1_2
set part_name    xcvc1902-vsva2197-2MP-e-S

create_project -force $project_name ./$project_name -part $part_name
set_property target_language Verilog [current_project]

# Adiciona fontes RTL
add_files -norecurse {
    ./tau_soc_wrapper_v1_2.sv
    ./voxel_rgb_parser_v1_1.sv
    ./o_core_top.sv
}
update_compile_order -fileset sources_1

# Adiciona constraints
add_files -fileset constrs_1 -norecurse ./tau_soc_wrapper.xdc

# Configura top
set_property top $top_module [current_fileset]

# Síntese
launch_runs synth_1 -jobs 8
wait_on_run synth_1

# Relatórios
open_run synth_1
report_utilization -file utilization_synth.rpt
report_timing_summary -file timing_synth.rpt

# Opcional: implementação e geração de PDI
# launch_runs impl_1 -to_step write_device_image -jobs 8
# wait_on_run impl_1
# open_run impl_1
# write_device_image -force tau_soc.pdi

puts "Síntese concluída. Relatórios salvos."
