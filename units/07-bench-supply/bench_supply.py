"""LM317 CC/CV bench supply (Unit 7). Run: python bench_supply.py -> bench_supply.svg"""
import schemdraw
import schemdraw.elements as elm


def lm317(label):
    return elm.Ic(pins=[elm.IcPin(name="IN", side="left"),
                        elm.IcPin(name="OUT", side="right"),
                        elm.IcPin(name="ADJ", side="bottom")],
                  size=(2.2, 1.6), pinspacing=1.0, edgepadW=0.5).label(label, loc="top", fontsize=12)


with schemdraw.Drawing(file="bench_supply.svg", show=False) as d:
    d.config(fontsize=11, unit=2.0)
    BOT = -8.0
    Y = 0.0  # main power line height

    # ---- input ----
    elm.Dot(open=True).at((-4, Y)).label("laptop brick\n+19–24 V", loc="left")
    elm.Diode().right().length(2.2).label("1N5822\n(reverse\nprotection)", loc="top")
    vin = elm.Dot()
    elm.Capacitor(polar=True).at(vin.center).down().toy(BOT).label("1000µF\n35V", loc="bottom")
    elm.Line().at(vin.center).right().length(1.8)
    c100 = elm.Dot()
    elm.Capacitor().at(c100.center).down().toy(BOT).label("100nF", loc="bottom")
    elm.Line().at(c100.center).right().length(1.0)
    u1 = lm317("U1  LM317\n(current limit)").right().anchor("IN")

    # ---- CC stage: a 4-position switch picks R_set between U1 OUT and U1 ADJ ----
    elm.Line().at(u1.OUT).right().length(0.8)
    pole = elm.Dot()
    tx = pole.center[0] + 1.6
    rset = ["1.2Ω 3W  (1 A)", "2.4Ω 2W  (500 mA)", "12Ω  (100 mA)", "62Ω  (20 mA)"]
    bus_x = tx + 4.0
    for i, text in enumerate(rset):
        ty = Y + 1.4 * (i + 1)
        elm.Dot(open=True).at((tx, ty))
        elm.Resistor().at((tx, ty)).right().tox(bus_x).label(text, loc="top", fontsize=10)
    elm.Line().at(pole.center).to((tx - 0.12, Y + 1.4 * 3 - 0.1))  # switch blade, set to 100 mA
    elm.Label().at((pole.center[0] - 0.2, Y + 2.6)).label("CURRENT\nRANGE\nswitch", halign="right", fontsize=10)
    elm.Line().at((bus_x, Y + 1.4 * 4)).down().toy(-3.6)
    elm.Line().left().tox(u1.ADJ[0])
    elm.Line().up().to(u1.ADJ)
    cc = elm.Dot().at((bus_x, -3.6))
    elm.Label().at((bus_x - 0.3, -3.1)).label("I_lim = 1.25 V / R_set", halign="right", fontsize=10)

    # ---- CV stage ----
    elm.Line().at(cc.center).right().length(1.5)
    u2 = lm317("U2  LM317\n(voltage)").right().anchor("IN")
    elm.Line().at(u2.OUT).right().length(1.5)
    vo = elm.Dot()
    elm.Resistor().at(vo.center).down().length(2.2).label("240Ω", loc="bottom")
    adj = elm.Dot()
    elm.Wire("-|").at(adj.center).to(u2.ADJ)
    elm.Potentiometer().at(adj.center).down().toy(BOT).label("5k\nVOLTAGE", loc="bottom")
    elm.Line().at(adj.center).right().length(2.6)
    elm.Capacitor(polar=True).down().toy(BOT).label("10µF", loc="bottom")
    # protection diodes
    elm.Diode().at((adj.center[0] - 0.9, adj.center[1])).up().toy(vo.center[1]).label("1N4002", loc="top", fontsize=9)

    # output
    elm.Line().at(vo.center).right().length(4.2)
    out = elm.Dot()
    elm.Capacitor().at(out.center).down().toy(BOT).label("1µF", loc="bottom")
    elm.Line().at(out.center).right().length(1.6)
    led = elm.Dot()
    elm.Resistor().at(led.center).down().length(2.0).label("5.6k", loc="bottom")
    elm.LED().down().toy(BOT)
    elm.Line().at(led.center).right().length(1.4)
    elm.Dot(open=True).label("+ OUT\n(red post)", loc="right")

    # ground rail + note
    elm.Line().at((-4, BOT)).right().tox(led.center[0] + 1.4)
    elm.Dot(open=True).label("- OUT (black post)\nvia the meter's\ncurrent shunt", loc="right")
    elm.Ground().at((-4, BOT)).label("brick -", loc="left")
    elm.Label().at((u2.center[0], -1.9)).label("V_out = 1.25 V × (1 + R_pot / 240Ω)", fontsize=10)
    elm.Label().at((u1.center[0], BOT + 0.8)).label("Not drawn: a 1N4002 from OUT to IN on each LM317,\nand both LM317s on an insulated heatsink (the tab is OUT!)", fontsize=10)
