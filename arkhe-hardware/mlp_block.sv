
// ============================================================================
// mlp_block.sv
// Functional stub for MLP Stage in Mythos Core.
// ============================================================================

`timescale 1ns / 1ps

module mlp_block #(
    parameter IN_DIM = 256,
    parameter HIDDEN_DIM = 1024,
    parameter OUT_DIM = 256,
    parameter DATA_WIDTH = 16
) (
    input  logic                            clk,
    input  logic                            rst_n,
    input  logic                            in_valid,
    input  logic signed [IN_DIM-1:0][DATA_WIDTH-1:0] in_data,
    output logic                            out_valid,
    output logic signed [OUT_DIM-1:0][DATA_WIDTH-1:0] out_data
);

    // Simplificação extrema para o MVP: Apenas um registro de bypass.
    // Em produção, isso seria um acelerador de multiplicação matriz-vetor.

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            out_data <= '0;
            out_valid <= 0;
        end else begin
            out_data <= in_data; // Bypass funcional
            out_valid <= in_valid;
        end
    end

endmodule
