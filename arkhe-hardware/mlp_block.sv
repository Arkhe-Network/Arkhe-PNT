
// ============================================================================
// mlp_block.sv
// Multi-Layer Perceptron block for Mythos Core with GELU Activation.
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

    // Sinais para a ativação GELU
    logic [IN_DIM-1:0] gelu_out_valid;
    logic signed [IN_DIM-1:0][DATA_WIDTH-1:0] gelu_out_data;

    // Instanciação paralela da GELU para cada elemento do vetor
    generate
        genvar i;
        for (i = 0; i < IN_DIM; i++) begin : gen_gelu
            gelu_pwl #(
                .DATA_WIDTH(DATA_WIDTH),
                .FRAC_WIDTH(8) // Q8.8
            ) u_gelu (
                .clk(clk),
                .rst_n(rst_n),
                .in_valid(in_valid),
                .in_data(in_data[i]),
                .out_valid(gelu_out_valid[i]),
                .out_data(gelu_out_data[i])
            );
        end
    endgenerate

    // No MVP, a saída da MLP é apenas a saída da GELU (bypass das camadas lineares)
    // Em produção, haveria W1*x + b1 -> GELU -> W2*x + b2

    assign out_data = gelu_out_data;
    assign out_valid = gelu_out_valid[0];

endmodule
