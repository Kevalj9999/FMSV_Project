module fifo #(
    parameter DEPTH = 16,
    parameter WIDTH = 8
)(
    input clk,
    input reset,
    input wr_en,
    input rd_en,
    input [WIDTH-1:0] data_in,
    output reg [WIDTH-1:0] data_out,
    output reg full,
    output reg empty
);

// -------- INTERNAL --------
reg [WIDTH-1:0] mem [0:DEPTH-1];
reg [3:0] wr_ptr;
reg [3:0] rd_ptr;
reg [4:0] count;

// -------- WRITE LOGIC --------
always @(posedge clk or posedge reset) begin
    if (reset) begin
        wr_ptr <= 0;
    end else begin
        if (wr_en && !full) begin
            mem[wr_ptr] <= data_in;
            wr_ptr <= wr_ptr + 1;
        end
    end
end

// -------- READ LOGIC --------
always @(posedge clk or posedge reset) begin
    if (reset) begin
        rd_ptr <= 0;
        data_out <= 0;
    end else begin
        if (rd_en && !empty) begin
            data_out <= mem[rd_ptr];
            rd_ptr <= rd_ptr + 1;
        end
    end
end

// -------- COUNT LOGIC --------
always @(posedge clk or posedge reset) begin
    if (reset) begin
        count <= 0;
    end else begin
        case ({wr_en && !full, rd_en && !empty})

            2'b10: count <= count + 1; // write only
            2'b01: count <= count - 1; // read only
            default: count <= count;   // no change

        endcase
    end
end

// -------- STATUS FLAGS --------
always @(posedge clk or posedge reset) begin
    if (reset) begin
        full <= 0;
        empty <= 1;
    end else begin
        full  <= (count == DEPTH);
        empty <= (count == 0);
    end
end

endmodule