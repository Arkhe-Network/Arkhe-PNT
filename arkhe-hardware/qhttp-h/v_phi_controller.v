/*
 * v_phi_controller.v - Controlador de Fase qhttp
 * Otimizado para mitigação de drift magnético de 4ppm
 * Inclui implementação do MELT-PROTOCOL
 */

module v_phi_controller #(
    parameter CLK_FREQ = 100000000, // 100MHz
    parameter BER_THRESHOLD = 32'h0000028F, // 0.01 in Q16.16 (10^-2)
    parameter PHASE_INSTABILITY_LIMIT = 32'h00008000, // ~0.5 rad em Q16.16
    parameter DRIFT_LIMIT_PPM = 10
)(
    input wire clk,
    input wire rst_n,

    // Telemetria do Filtro de Kalman
    input wire [31:0] current_phase,      // Phi (Q16.16)
    input wire [31:0] phase_innovation,   // Erro de predição (Q16.16)
    input wire [31:0] frequency_drift,    // Omega (ppm)
    input wire [31:0] measured_ber,       // BER atual

    // Controle de Saída
    output reg [31:0] v_phi_out,          // Tensão de controle de fase
    output reg shutdown_n,                // Ativo baixo para desligamento
    output reg thermal_dump_en,           // Ativar dissipadores Graphene-TPU
    output reg entropy_injection_en,      // Injetar ruído branco

    // Status
    output reg melt_active
);

    reg [15:0] ber_error_counter;
    reg [31:0] reset_timer;

    // Estados do Melt-Protocol
    localparam NORMAL = 2'b00;
    localparam MELT_TRIGGERED = 2'b01;
    localparam COOLING = 2'b10;
    localparam RESET = 2'b11;

    reg [1:0] state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            v_phi_out <= 0;
            shutdown_n <= 1;
            thermal_dump_en <= 0;
            entropy_injection_en <= 0;
            melt_active <= 0;
            ber_error_counter <= 0;
            reset_timer <= 0;
            state <= NORMAL;
        end else begin
            case (state)
                NORMAL: begin
                    v_phi_out <= current_phase; // Feedback direto do Kalman
                    shutdown_n <= 1;
                    thermal_dump_en <= 0;
                    entropy_injection_en <= 0;
                    melt_active <= 0;

                    // Monitoramento de Gatilhos
                    if (measured_ber > BER_THRESHOLD) begin
                        if (ber_error_counter >= 1000)
                            state <= MELT_TRIGGERED;
                        else
                            ber_error_counter <= ber_error_counter + 1;
                    end else begin
                        ber_error_counter <= 0;
                    end

                    if (phase_innovation > PHASE_INSTABILITY_LIMIT || frequency_drift > DRIFT_LIMIT_PPM) begin
                        state <= MELT_TRIGGERED;
                    end
                end

                MELT_TRIGGERED: begin
                    v_phi_out <= 0;
                    shutdown_n <= 0; // SHUTDOWN_PHASE
                    thermal_dump_en <= 1; // THERMAL_DUMP
                    entropy_injection_en <= 1; // ENTROPY_INJECTION
                    melt_active <= 1;
                    reset_timer <= 0;
                    state <= COOLING;
                end

                COOLING: begin
                    if (reset_timer < 50000000) begin // 500ms @ 100MHz
                        reset_timer <= reset_timer + 1;
                    end else begin
                        state <= RESET;
                    end
                end

                RESET: begin
                    // HARD_RESET sequence
                    v_phi_out <= 0;
                    shutdown_n <= 1;
                    thermal_dump_en <= 0;
                    entropy_injection_en <= 0;
                    melt_active <= 0;
                    ber_error_counter <= 0;
                    state <= NORMAL;
                end
            endcase
        end
    end

endmodule
