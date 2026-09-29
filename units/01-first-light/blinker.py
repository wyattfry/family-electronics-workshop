"""Two-transistor astable LED blinker (Unit 1). Run: python blinker.py -> blinker.svg"""
import schemdraw
import schemdraw.elements as elm

TOP, YC, YQ = 9.0, 3.2, 1.6  # supply rail, cap row, transistor collector height
XL, XA, XB, XR = 0.0, 3.5, 6.5, 10.0  # columns: Q1 collector, R3/C1 node, R4/C2 node, Q2 collector

with schemdraw.Drawing(file="blinker.svg", show=False) as d:
    d.config(fontsize=13, unit=2.0)
    Q1 = elm.BjtNpn(circle=True).reverse().anchor("collector").at((XL, YQ)).label("Q1\n2N3904", loc="left")
    Q2 = elm.BjtNpn(circle=True).anchor("collector").at((XR, YQ)).label("Q2\n2N3904", loc="right")

    # supply rail
    elm.Line().at((XL, TOP)).right().tox(XR)
    elm.Vdd().at(((XL + XR) / 2, TOP)).label("+4.5 V (3×AA)")

    # collector columns: rail -> resistor -> LED (anode up) -> collector
    for x, r, led, side in ((XL, "R1\n330Ω", "LED1", "bottom"), (XR, "R2\n330Ω", "LED2", "top")):
        elm.Resistor().down().at((x, TOP)).label(r, loc=side)
        elm.LED().down().label(led, loc=side)
        elm.Line().down().toy(YC)
        elm.Dot()
        elm.Line().down().toy(YQ)

    # base resistors down to the cap nodes
    elm.Resistor().down().at((XA, TOP)).toy(YC).label("R3\n47k", loc="bottom")
    nA = elm.Dot()
    elm.Resistor().down().at((XB, TOP)).toy(YC).label("R4\n47k")
    nB = elm.Dot()

    # cross-coupling capacitors (+ toward the collectors)
    elm.Capacitor(polar=True).at((XL, YC)).right().tox(XA).label("C1\n10µF", loc="top")
    elm.Capacitor(polar=True).at((XR, YC)).left().tox(XB).label("C2\n10µF", loc="top")

    # the "X": each cap node drives the OTHER transistor's base
    elm.Line().at(nA.center).to(Q2.base)
    elm.Line().at(nB.center).to(Q1.base)

    # ground rail
    elm.Line().at(Q1.emitter).down().length(0.7)
    g = elm.Line().right().tox(XR)
    elm.Line().up().toy(Q2.emitter[1])
    elm.Ground().at(((XL + XR) / 2, g.end[1]))
