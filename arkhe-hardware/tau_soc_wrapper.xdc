# ============================================================================
# tau_soc_wrapper.xdc
# Constraints for AMD Versal AI Core Series (XCVC1902)
# ============================================================================

# ----------------------------------------------------------------------------
# Primary Clock (100MHz Differential)
# ----------------------------------------------------------------------------
create_clock -period 10.000 -name clk_100mhz [get_ports clk_100mhz_p]

# ----------------------------------------------------------------------------
# AXI4-Stream Input (Picasso Lidar) — s_axis_lidar_*
# ----------------------------------------------------------------------------
set_input_delay -clock clk_100mhz -max 3.0 [get_ports {s_axis_lidar_tdata[*]}]
set_input_delay -clock clk_100mhz -min 0.5 [get_ports {s_axis_lidar_tdata[*]}]
set_input_delay -clock clk_100mhz -max 3.0 [get_ports {s_axis_lidar_tvalid s_axis_lidar_tlast}]
set_input_delay -clock clk_100mhz -min 0.5 [get_ports {s_axis_lidar_tvalid s_axis_lidar_tlast}]

# ----------------------------------------------------------------------------
# AXI4-Stream Output (to NOC/DDR) — m_axis_roi_*
# ----------------------------------------------------------------------------
set_output_delay -clock clk_100mhz -max 3.0 [get_ports {m_axis_roi_tdata[*]}]
set_output_delay -clock clk_100mhz -min 0.0 [get_ports {m_axis_roi_tdata[*]}]
set_output_delay -clock clk_100mhz -max 3.0 [get_ports {m_axis_roi_tvalid m_axis_roi_tlast m_axis_roi_tid}]
set_output_delay -clock clk_100mhz -min 0.0 [get_ports {m_axis_roi_tvalid m_axis_roi_tlast m_axis_roi_tid}]

# Output delay for backpressure signal (VRP -> Lidar)
set_output_delay -clock clk_100mhz -max 3.0 [get_ports s_axis_lidar_tready]

# ----------------------------------------------------------------------------
# Asynchronous Reset
# ----------------------------------------------------------------------------
set_false_path -from [get_ports rst_n_btn]

# ----------------------------------------------------------------------------
# Quasi-Static Configuration Inputs
# ----------------------------------------------------------------------------
set_input_delay -clock clk_100mhz -max 5.0 [get_ports {i_cfg_*}]

# ----------------------------------------------------------------------------
# CDC Comments (Informative)
# ----------------------------------------------------------------------------
# Clock Domain Crossing occurs at:
#   - VRP (100MHz) → AXI4-Stream NOC bridge (internal CDC handled by Versal)
#   - O-Core internal 8MHz domain (MMCM generated)
#   - Reset synchronizers are implemented in RTL (3-stage)
# No additional constraints required for these paths.

# ----------------------------------------------------------------------------
# Synthesis Properties
# ----------------------------------------------------------------------------
set_property IOSTANDARD LVDS [get_ports {clk_100mhz_p clk_100mhz_n}]
set_property DIFF_TERM TRUE [get_ports {clk_100mhz_p clk_100mhz_n}]
