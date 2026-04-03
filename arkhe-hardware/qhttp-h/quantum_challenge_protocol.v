// quantum_challenge_protocol.v
module quantum_challenge_protocol #(
    parameter CHALLENGE_TIMEOUT = 10000,  // 100ms @ 100MHz
    parameter NUM_CHALLENGE_ROUNDS = 5
)(
    input wire clk_100MHz,
    input wire rst_n,
    input wire start_challenge,

    // Interface com nó desafiado
    input wire [255:0] node_id,
    input wire node_coherent,              // Claim do nó

    // Interface com QD verificador
    output reg challenge_pulse,
    input wire [31:0] response_time,        // Ciclos até resposta
    input wire [1:0] response_state,        // 00=timeout, 01=incoherent, 10=coherent, 11=invalid

    // Estado do protocolo
    output reg [2:0] protocol_state,
    output reg challenge_failed,
    output reg [7:0] failed_rounds,
    output reg [31:0] avg_response_time
);

    // Estados
    localparam IDLE = 3'b000;
    localparam SEND_CHALLENGE = 3'b001;
    localparam AWAIT_RESPONSE = 3'b010;
    localparam VERIFY_RESPONSE = 3'b011;
    localparam NEXT_ROUND = 3'b100;
    localparam FINALIZE = 3'b101;

    reg [31:0] challenge_timer;
    reg [2:0] current_round;
    reg [63:0] response_accumulator;

    always @(posedge clk_100MHz or negedge rst_n) begin
        if (!rst_n) begin
            protocol_state <= IDLE;
            challenge_failed <= 0;
            failed_rounds <= 0;
            current_round <= 0;
            challenge_pulse <= 0;
            response_accumulator <= 0;
        end else begin
            case (protocol_state)
                IDLE: begin
                    if (start_challenge) begin
                        current_round <= 0;
                        failed_rounds <= 0;
                        response_accumulator <= 0;
                        protocol_state <= SEND_CHALLENGE;
                    end
                end

                SEND_CHALLENGE: begin
                    // Envia pulso de desafio (fase específica)
                    challenge_pulse <= 1'b1;
                    challenge_timer <= 0;
                    protocol_state <= AWAIT_RESPONSE;
                end

                AWAIT_RESPONSE: begin
                    challenge_pulse <= 1'b0;
                    challenge_timer <= challenge_timer + 1;

                    // Timeout?
                    if (challenge_timer >= CHALLENGE_TIMEOUT) begin
                        failed_rounds <= failed_rounds + 1;
                        protocol_state <= NEXT_ROUND;
                    end else if (response_state != 2'b00) begin
                        // Recebeu resposta
                        response_accumulator <= response_accumulator + response_time;
                        protocol_state <= VERIFY_RESPONSE;
                    end
                end

                VERIFY_RESPONSE: begin
                    // Verifica se resposta é válida e coerente
                    if (response_state == 2'b11) begin  // Resposta inválida
                        failed_rounds <= failed_rounds + 2;  // Penalidade dobrada
                    end else if (response_state == 2'b01) begin  // Incoerente honesto
                        failed_rounds <= failed_rounds + 1;
                    end else if (response_state == 2'b10) begin  // Coerente
                        // Passou nesta rodada
                    end
                    protocol_state <= NEXT_ROUND;
                end

                NEXT_ROUND: begin
                    current_round <= current_round + 1;
                    if (current_round >= NUM_CHALLENGE_ROUNDS) begin
                        protocol_state <= FINALIZE;
                    end else begin
                        protocol_state <= SEND_CHALLENGE;
                    end
                end

                FINALIZE: begin
                    // Falha se > 60% das rodadas falharam
                    if (failed_rounds > (NUM_CHALLENGE_ROUNDS * 3 / 5)) begin
                        challenge_failed <= 1'b1;
                    end else begin
                        challenge_failed <= 0;
                    end

                    // Calcula tempo médio de resposta
                    if (current_round > failed_rounds) begin
                      avg_response_time <= response_accumulator / (current_round - failed_rounds);
                    end else begin
                      avg_response_time <= 0;
                    end

                    protocol_state <= IDLE;
                end
                default: protocol_state <= IDLE;
            endcase
        end
    end
endmodule
