from wave import bit, bus, strobe, plot

V = "tx_backpressure_diagram_tb.vcd"
T = "tx_backpressure_diagram_tb."
U = T + "uut."
B = U + "b0."

STATES = {0: "IDLE", 1: "START_TX", 2: "TX"}


def beat(v):
    if v >> 16 == 0:
        return "M"
    return "%d" % (v & 0xFF)


def first_last(v):
    return v != 0 and (v >> 16 == 0 or (v & 0xFF) in (0, 1, 39))


# four packets for UART 0:  the stream reader held full (tready low) until UART 0 takes the word waiting
# in the output buffer
plot("tx_backpressure.pdf", V, [
    bit(T + "tvalid", "tvalid"),
    bit(T + "tready", "tready"),
    bus(T + "pkt", "offered", fmt=lambda v: "%d" % v, show=lambda v: v > 0),
    bit(B + "packet_valid", "pvalid"),
    strobe(B + "packet_ready", "pready"),
    bus(B + "status[31:0]", "state", bits=(9, 8), fmt=lambda v: STATES.get(v, "?"),
        show=lambda v: v == 2),
    bit(U + "valid[39:0]", "uvalid(0)", bits=(0, 0)),
    strobe(U + "ready[39:0]", "uready(0)", bits=(0, 0)),
    bit(U + "posi_o[39:0]", "POSI(0)", bits=(0, 0)),
], 0, 15000, unit="us")

# the release:  UART 0 takes packet 2's word, the output buffer takes packet 3, the stream reader is free
plot("tx_release.pdf", V, [
    bit(T + "clk", "clk"),
    bit(T + "tvalid", "tvalid"),
    bit(T + "tready", "tready"),
    bus(T + "tdata[63:0]", "tdata", fmt=beat, show=first_last, size=7),
    bit(B + "packet_valid", "pvalid"),
    bit(B + "packet_ready", "pready"),
    bus(B + "status[31:0]", "state", bits=(9, 8), fmt=lambda v: STATES.get(v, "?"), size=7),
    bit(U + "valid[39:0]", "uvalid(0)", bits=(0, 0)),
    bit(U + "ready[39:0]", "uready(0)", bits=(0, 0)),
    bit(U + "posi_o[39:0]", "POSI(0)", bits=(0, 0)),
], 7300, 7500)
