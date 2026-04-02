/*
 * 🜏 FPGA Control Logic for QD Laser and Detectors
 * Part of the Q-SAT HIL Simulation Suite
 */

module fpga_hil_controller (
    input wire clk,          // 100MHz clock
    input wire reset_n,      // Active-low reset

    // Command Interface (from OrbVM)
    input wire [15:0] cmd_trigger,
    input wire [31:0] laser_duration_ns,

    // Physical Control Lines
    output reg laser_en,     // 532nm Laser Enable
    output reg microwave_en, // Microwave Spin-Pulse Enable
    input wire detector_in,  // Fluorescent Feedback (Digital Pulse)

    // Telemetry
    output reg [31:0] detector_count,
    output reg coherence_lock
);

    reg [31:0] timer;
    reg state;

    localparam IDLE = 1'b0;
    localparam BUSY = 1'b1;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            laser_en <= 0;
            microwave_en <= 0;
            detector_count <= 0;
            coherence_lock <= 0;
            timer <= 0;
            state <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    if (cmd_trigger != 16'h0) begin
                        laser_en <= 1;
                        microwave_en <= 1;
                        timer <= 0;
                        state <= BUSY;
                    end
                end

                BUSY: begin
                    if (timer < laser_duration_ns / 10) begin // 100MHz clock = 10ns per cycle
                        timer <= timer + 1;
                        if (detector_in) begin
                            detector_count <= detector_count + 1;
                        end
                    end else begin
                        laser_en <= 0;
                        microwave_en <= 0;
                        state <= IDLE;

                        // Coherence logic (simplified)
                        if (detector_count > 100) begin
                            coherence_lock <= 1;
                        end else begin
                            coherence_lock <= 0;
                        end
                    end
                end
            endcase
        end
    end
endmodule
