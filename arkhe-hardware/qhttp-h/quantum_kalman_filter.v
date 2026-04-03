// quantum_kalman_filter.v - Módulo de discriminação de coerência
module quantum_kalman_filter #(
    parameter WINDOW_SIZE = 1024,
    parameter COHERENCE_THRESHOLD = 50000  // 50μs em ciclos de 100MHz
)(
    input wire clk_100MHz,
    input wire rst_n,
    input wire [31:0] raw_apd_count,
    input wire [63:0] timestamp,
    output reg quantum_coherent,
    output reg [31:0] coherence_metric,
    output reg [1:0] noise_classification  // 00=unknown, 01=classical, 10=quantum, 11=decohered
);

    // Filtro de média móvel exponencial para ruído térmico (lento)
    reg [63:0] thermal_accumulator;
    reg [31:0] thermal_baseline;

    // Janela deslizante para estatísticas de Poisson (fótons)
    reg [31:0] photon_window [0:WINDOW_SIZE-1];
    reg [9:0] window_index;
    reg [63:0] window_sum;

    // Máquina de estados de Kalman
    localparam INIT = 2'b00;
    localparam PREDICT = 2'b01;
    localparam UPDATE = 2'b10;
    localparam CLASSIFY = 2'b11;

    reg [1:0] kalman_state;
    reg [31:0] prediction_error;
    reg [63:0] last_timestamp;

    always @(posedge clk_100MHz or negedge rst_n) begin
        if (!rst_n) begin
            kalman_state <= INIT;
            window_index <= 0;
            window_sum <= 0;
            thermal_accumulator <= 0;
            quantum_coherent <= 0;
            coherence_metric <= 0;
            noise_classification <= 2'b00;
        end else begin
            case (kalman_state)
                INIT: begin
                    photon_window[window_index] <= raw_apd_count;
                    window_sum <= window_sum + raw_apd_count;
                    window_index <= window_index + 1;
                    if (window_index == WINDOW_SIZE-1) kalman_state <= PREDICT;
                end

                PREDICT: begin
                    thermal_baseline <= (thermal_accumulator >> 10);
                    prediction_error <= (raw_apd_count > thermal_baseline) ?
                                       (raw_apd_count - thermal_baseline) :
                                       (thermal_baseline - raw_apd_count);
                    kalman_state <= UPDATE;
                end

                UPDATE: begin
                    window_sum <= window_sum - photon_window[window_index] + raw_apd_count;
                    photon_window[window_index] <= raw_apd_count;
                    window_index <= (window_index == WINDOW_SIZE-1) ? 0 : window_index + 1;

                    if (prediction_error < (thermal_baseline >> 3)) begin
                        if ((timestamp - last_timestamp) > COHERENCE_THRESHOLD) begin
                            quantum_coherent <= 1;
                            noise_classification <= 2'b10;
                        end
                    end else if (raw_apd_count < (thermal_baseline >> 1)) begin
                        quantum_coherent <= 0;
                        noise_classification <= 2'b11;
                    end else begin
                        quantum_coherent <= 0;
                        noise_classification <= 2'b01;
                    end

                    thermal_accumulator <= (thermal_accumulator * 1023 + raw_apd_count) >> 10;
                    last_timestamp <= timestamp;
                    kalman_state <= CLASSIFY;
                end

                CLASSIFY: begin
                    coherence_metric <= quantum_coherent ?
                                       (COHERENCE_THRESHOLD - (timestamp - last_timestamp)[31:0]) :
                                       32'd0;
                    kalman_state <= PREDICT;
                end
            endcase
        end
    end
endmodule
