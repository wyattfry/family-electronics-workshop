"""Crystal radio (Unit 2). Run: python crystal_radio.py -> crystal_radio.svg"""
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="crystal_radio.svg", show=False) as d:
    d.config(fontsize=13, unit=3)
    BOT, TOP = 0, 6
    XL, XC, XD, XR, XE = 0, 5, 7, 11, 14

    elm.Antenna().at((XL, TOP)).label("long wire\nantenna", loc="left")
    elm.Line().at((XL, TOP)).right().tox(XE)
    elm.Line().at((XL, BOT)).right().tox(XE)
    elm.Ground().at((XL, BOT)).label("ground\n(rod or pipe)", loc="left")

    elm.Inductor2(loops=5).at((XL, TOP)).down().toy(BOT)
    elm.Label().at((XL + 0.6, TOP / 2)).label("L1\n~85 turns on\n1.75\" tube\n~240 µH", halign="left")

    elm.Dot().at((XC, TOP))
    elm.CapacitorVar().at((XC, TOP)).down().toy(BOT)
    elm.Label().at((XC + 0.9, TOP / 2)).label("C1\n365 pF\nTUNING", halign="left")

    elm.Diode().at((XD, TOP)).right().length(2.5).label("D1  1N34A\n(germanium)")
    n = elm.Dot().at((XR, TOP))
    elm.Resistor().at((XR, TOP)).down().toy(BOT).label("47k", loc="bottom")

    sp = elm.Speaker().right().anchor("in1").at((XE, TOP - 2)).label("crystal\nearpiece", loc="right")
    elm.Line().at((XE, TOP)).down().to(sp.in1)
    elm.Wire("|-").at(sp.in2).to((XE, BOT))
