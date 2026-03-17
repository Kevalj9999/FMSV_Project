module traffic_light (
    input clk,
    input reset,
    input sensor,
    output reg [1:0] highway_light,
    output reg [1:0] farm_light
);

parameter GREEN  = 2'b00;
parameter YELLOW = 2'b01;
parameter RED    = 2'b10;

reg [1:0] state;
reg [3:0] timer;

always @(posedge clk or posedge reset) begin
    if (reset) begin
        state <= GREEN;
        timer <= 0;
    end else begin
        case (state)

            GREEN: begin
                highway_light <= GREEN;
                farm_light <= RED;
                if (sensor) begin
                    if (timer == 5) begin
                        state <= YELLOW;
                        timer <= 0;
                    end else begin
                        timer <= timer + 1;
                    end
                end
            end

            YELLOW: begin
                highway_light <= YELLOW;
                farm_light <= RED;
                if (timer == 2) begin
                    state <= RED;
                    timer <= 0;
                end else begin
                    timer <= timer + 1;
                end
            end

            RED: begin
                highway_light <= RED;
                farm_light <= GREEN;
                if (timer == 5) begin
                    state <= GREEN;
                    timer <= 0;
                end else begin
                    timer <= timer + 1;
                end
            end

        endcase
    end
end

endmodule