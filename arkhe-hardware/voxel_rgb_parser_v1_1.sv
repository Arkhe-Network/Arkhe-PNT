// ============================================================================
// voxel_rgb_parser_v1_1.sv (STUB)
// Placeholder for the VRP v1.1 module
// ============================================================================

module voxel_rgb_parser_v1_1 #(
    parameter VOXEL_DATA_WIDTH = 128,
    parameter HASH_TABLE_DEPTH = 2048,
    parameter ROI_FIFO_DEPTH   = 256,
    parameter ROI_PACKET_WIDTH = 64
) (
    input  logic                     clk,
    input  logic                     rst_n,

    // AXI4-Stream Slave (Picasso Lidar)
    input  logic                     s_axis_tvalid,
    output logic                     s_axis_tready,
    input  logic [VOXEL_DATA_WIDTH-1:0] s_axis_tdata,
    input  logic                     s_axis_tlast,

    // AXI4-Stream Master (Versal NOC)
    output logic                     m_axis_tvalid,
    input  logic                     m_axis_tready,
    output logic [ROI_PACKET_WIDTH-1:0] m_axis_tdata,
    output logic                     m_axis_tlast,
    output logic [0:0]               m_axis_tid,

    // IRQ: Generated when tlast handshake completes
    output logic                     o_irq_frame_done,

    // Configuration
    input  logic [3:0]               i_cfg_grid_shift,
    input  logic [15:0]              i_cfg_red_threshold,
    input  logic [15:0]              i_cfg_green_threshold,
    input  logic [15:0]              i_cfg_blue_threshold,

    // Status
    output logic [31:0]              o_status_frame_count,
    output logic [31:0]              o_status_voxel_count,
    output logic                     o_fifo_overflow
);

    // Basic logic to allow testbench progression
    assign s_axis_tready = m_axis_tready; // Simple pass-through ready

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            o_status_frame_count <= 0;
            o_status_voxel_count <= 0;
            o_irq_frame_done     <= 0;
            m_axis_tvalid        <= 0;
            m_axis_tlast         <= 0;
            o_fifo_overflow      <= 0;
        end else begin
            if (s_axis_tvalid && s_axis_tready) begin
                o_status_voxel_count <= o_status_voxel_count + 1;

                // Stub ROI detection logic:
                // [intensity(16), b(8), g(8), r(8), z(16), y(16), x(16)]
                // Red > threshold OR Green > threshold -> ROI
                if (s_axis_tdata[95:88] > i_cfg_red_threshold[7:0] ||
                    s_axis_tdata[103:96] > i_cfg_green_threshold[7:0]) begin
                    m_axis_tvalid <= 1;
                    m_axis_tdata  <= s_axis_tdata[63:0]; // Simplified ROI packet
                    m_axis_tlast  <= s_axis_tlast;
                    m_axis_tid    <= 0;
                end else begin
                    m_axis_tvalid <= 0;
                end

                if (s_axis_tlast) begin
                    o_status_frame_count <= o_status_frame_count + 1;
                    o_irq_frame_done     <= 1;
                end else begin
                    o_irq_frame_done     <= 0;
                end
            end else begin
                if (m_axis_tready) m_axis_tvalid <= 0;
                o_irq_frame_done <= 0;
            end

            // Simulate overflow if stalled
            if (s_axis_tvalid && !s_axis_tready && o_status_voxel_count > 200) begin
                 o_fifo_overflow <= 1;
            end
        end
    end

endmodule
