module top (
    input clk,
    input reset,
    input wr_en,
    input rd_en,
    input [7:0] data_in,
    output [7:0] data_out,
    output full,
    output empty
);

wire [3:0] count;
wire [3:0] wr_ptr, rd_ptr;

fifo u_fifo (
    .clk(clk),
    .reset(reset),
    .wr_en(wr_en),
    .rd_en(rd_en),
    .data_in(data_in),
    .data_out(data_out),
    .full(full),
    .empty(empty),
    .count(count),
    .wr_ptr(wr_ptr),
    .rd_ptr(rd_ptr)
);

controller u_ctrl (
    .clk(clk),
    .reset(reset),
    .count(count),
    .full(full),
    .empty(empty),
    .wr_en(wr_en),
    .rd_en(rd_en)
);

endmodule