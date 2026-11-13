from wave import bit, plot

V = "tx_backpressure_diagram_tb.vcd"
T = "tx_backpressure_diagram_tb."
U = T + "uut."

# packets for UART 1 flat out (from tvalid high to the third start bit):  the stream reader held full (tready low) until UART 1 takes the word waiting
# in the output buffer;  tready's high periods numbered (one packet each)
plot("tx_backpressure.pdf", V, [
    bit(T + "tvalid", "tvalid"),
    bit(T + "tready", "tready", count=True),
    bit(U + "valid[39:0]", "uvalid(1)", bits=(1, 1)),
    bit(U + "ready[39:0]", "uready(1)", bits=(1, 1)),
    bit(U + "posi_o[39:0]", "POSI(1)", bits=(1, 1)),
], 121, 14000, unit="us",
    arrows=[(7160, "POSI(1)", 1, "Stop", -22, 6), (7260, "POSI(1)", 0, "Start", 22, 9)])
