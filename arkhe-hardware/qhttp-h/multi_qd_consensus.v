// multi_qd_consensus.v - Consenso quântico distribuído
module multi_qd_consensus #(
    parameter NUM_QD_NODES = 4,
    parameter THRESHOLD_T2 = 40000,      // 40μs em ciclos de 100MHz
    parameter CONSENSUS_RATIO = 3,         // 3/4 = 75%
    parameter WEIGHT_DECAY_C = 100000      // Constante de decaimento espacial
)(
    input wire clk_100MHz,
    input wire rst_n,

    // Interfaces com cada nó QD
    input wire [NUM_QD_NODES-1:0] qd_coherent,
    input wire [31:0] qd_t2_star [0:NUM_QD_NODES-1],
    input wire [63:0] qd_distances [0:NUM_QD_NODES-1],  // Distâncias ao evento

    // Coordenadas do evento (para cálculo de pesos)
    input wire [31:0] event_lat, event_lon,

    // Saída de consenso
    output reg consensus_valid,
    output reg [31:0] weighted_t2_star,
    output reg [7:0] consensus_count,
    output reg [1:0] consensus_state
);

    // Estados
    localparam COLLECT = 2'b00;
    localparam WEIGHT = 2'b01;
    localparam VERIFY = 2'b10;
    localparam FINALIZE = 2'b11;

    reg [1:0] state;
    reg [NUM_QD_NODES-1:0] valid_nodes;
    reg [63:0] weight_accumulator;
    reg [95:0] weighted_sum;  // Para precisão em cálculo ponderado

    // Generic combinatorial bit counting using a generate loop or reduction sum
    integer j;
    reg [7:0] current_valid_count;
    always @(*) begin
        current_valid_count = 0;
        for (j = 0; j < NUM_QD_NODES; j = j + 1) begin
            if (valid_nodes[j]) current_valid_count = current_valid_count + 1;
        end
    end

    // Cálculo de pesos geodésicos: w = exp(-d/c)
    function [31:0] calculate_weight;
        input [63:0] distance;
        reg [63:0] scaled;
        begin
            // Aproximação: w ≈ 1 - d/c para d << c, saturando em 0
            scaled = distance / WEIGHT_DECAY_C;
            if (scaled >= 1)
                calculate_weight = 0;
            else
                calculate_weight = 32'hFFFFFFFF - (scaled[31:0] * 32'hFFFFFFFF);
        end
    endfunction

    integer i;
    reg [31:0] weights [0:NUM_QD_NODES-1];

    always @(posedge clk_100MHz or negedge rst_n) begin
        if (!rst_n) begin
            state <= COLLECT;
            consensus_valid <= 0;
            consensus_count <= 0;
            weighted_t2_star <= 0;
            weight_accumulator <= 0;
            weighted_sum <= 0;
            valid_nodes <= 0;
        end else begin
            case (state)
                COLLECT: begin
                    // Coleta estados de coerência de todos os nós
                    valid_nodes <= 0;
                    for (i = 0; i < NUM_QD_NODES; i = i + 1) begin
                        if (qd_coherent[i] && qd_t2_star[i] > THRESHOLD_T2) begin
                            valid_nodes[i] <= 1'b1;
                            weights[i] <= calculate_weight(qd_distances[i]);
                        end
                    end
                    state <= WEIGHT;
                end

                WEIGHT: begin
                    // Calcula T₂* médio ponderado
                    weight_accumulator <= 0;
                    weighted_sum <= 0;
                    for (i = 0; i < NUM_QD_NODES; i = i + 1) begin
                        if (valid_nodes[i]) begin
                            weight_accumulator <= weight_accumulator + weights[i];
                            weighted_sum <= weighted_sum + (qd_t2_star[i] * weights[i]);
                        end
                    end
                    state <= VERIFY;
                end

                VERIFY: begin
                    consensus_count <= current_valid_count;
                    // Verifica se atingimos o ratio de consenso parametrizado
                    if (current_valid_count >= (NUM_QD_NODES * CONSENSUS_RATIO / 4)) begin
                        if (weight_accumulator > 0) begin
                          weighted_t2_star <= weighted_sum / weight_accumulator;
                          consensus_valid <= (weighted_t2_star > THRESHOLD_T2);
                        end else begin
                          consensus_valid <= 0;
                        end
                    end else begin
                        consensus_valid <= 0;
                    end
                    state <= FINALIZE;
                end

                FINALIZE: begin
                    // Estado final: aguarda próximo ciclo
                    state <= COLLECT;
                end
                default: state <= COLLECT;
            endcase
        end
    end
endmodule
