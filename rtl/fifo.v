module fifo (
    input clk,
    input reset,
    input wr_en,
    input rd_en,
    input [7:0] data_in,
    output reg [7:0] data_out,
    output reg full,
    output reg empty,
    output reg [3:0] count,
    output reg [3:0] wr_ptr,
    output reg [3:0] rd_ptr
);

reg [7:0] mem [0:15];

always @(posedge clk or posedge reset) begin
    if (reset) begin
        wr_ptr <= 0;
    end else if (wr_en && !full) begin
        mem[wr_ptr] <= data_in;
        wr_ptr <= wr_ptr + 1;
    end
end

always @(posedge clk or posedge reset) begin
    if (reset) begin
        rd_ptr <= 0;
        data_out <= 0;
    end else if (rd_en && !empty) begin
        data_out <= mem[rd_ptr];
        rd_ptr <= rd_ptr + 1;
    end
end

always @(posedge clk or posedge reset) begin
    if (reset) begin
        count <= 0;
    end else begin
        case ({wr_en && !full, rd_en && !empty})
            2'b10: count <= count + 1;
            2'b01: count <= count - 1;
            default: count <= count;
        endcase
    end
end

always @(posedge clk or posedge reset) begin
    if (reset) begin
        full <= 0;
        empty <= 1;
    end else begin
        full  <= (count == 15);
        empty <= (count == 0);
    end
end

endmodule