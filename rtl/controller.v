module controller (
    input clk,
    input reset,
    input [3:0] count,
    input full,
    input empty,
    output reg wr_en,
    output reg rd_en
);

always @(posedge clk or posedge reset) begin
    if (reset) begin
        wr_en <= 0;
        rd_en <= 0;
    end else begin
        if (!full)
            wr_en <= 1;
        else
            wr_en <= 0;

        if (!empty)
            rd_en <= 1;
        else
            rd_en <= 0;
    end
end

endmodule