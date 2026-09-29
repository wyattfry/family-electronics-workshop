"""Atari Punk Console (Unit 4). Run: python punk_console.py -> punk_console.svg"""
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="punk_console.svg", show=False) as d:
    d.config(fontsize=12, unit=2.0)
    TOP, BOT = 9.0, -5.0
    vx = 22

    # ---------- IC1: astable ----------
    ic1 = elm.Ic555().right().at((0, 0)).label("IC1  555\nastable", loc="bottom", ofst=(1.6, -0.6))
    xL1 = ic1.DIS[0] - 2.5
    elm.Line().at((xL1 - 0.5, TOP)).right().tox(vx)  # +9V rail
    elm.Vdd().at((xL1 - 0.5, TOP)).label("+9 V")
    elm.Line().at((xL1 - 0.5, BOT)).right().tox(vx)  # ground rail
    elm.Ground().at((xL1 - 0.5, BOT))

    elm.Resistor().at((xL1, TOP)).down().toy(ic1.DIS[1]).label("1k", loc="bottom")
    dis = elm.Dot()
    elm.Line().right().to(ic1.DIS)
    elm.Potentiometer().at(dis.center).down().label("500k\n'PITCH'", loc="bottom")
    tr = elm.Dot()
    elm.Wire("-|").at(tr.center).to(ic1.THR)
    elm.Wire("-|").at(tr.center).to(ic1.TRG)
    elm.Capacitor().at(tr.center).down().toy(BOT).label("10nF", loc="bottom")
    elm.Line().at(ic1.Vcc).up().toy(TOP)
    elm.Wire("|-").at(ic1.RST).to((ic1.Vcc[0], TOP - 0.6))
    elm.Line().at(ic1.GND).down().toy(BOT)
    elm.Line().at(ic1.CTL).right().length(0.6)
    elm.Capacitor().down().toy(BOT).label("10nF", loc="bottom")

    # ---------- IC2: monostable ----------
    ic2 = elm.Ic555().right().at((10, 0)).label("IC2  555\nmonostable", loc="bottom", ofst=(1.6, -0.6))
    xL2 = ic2.DIS[0] - 2.0
    elm.Resistor().at((xL2, TOP)).down().length(2.2).label("1k", loc="bottom")
    elm.Potentiometer().down().toy(ic2.DIS[1]).label("500k\n'GRIT'", loc="bottom")
    n67 = elm.Dot()
    elm.Line().right().to(ic2.DIS)
    elm.Wire("-|").at(n67.center).to(ic2.THR)
    elm.Capacitor().at(n67.center).down().toy(BOT).label("100nF", loc="bottom")
    elm.Line().at(ic2.Vcc).up().toy(TOP)
    elm.Wire("|-").at(ic2.RST).to((ic2.Vcc[0], TOP - 0.6))
    elm.Line().at(ic2.GND).down().toy(BOT)
    elm.Line().at(ic2.CTL).right().length(0.6)
    elm.Capacitor().down().toy(BOT).label("10nF", loc="bottom")

    # IC1 OUT -> IC2 TRIG (the trigger wire)
    elm.Line().at(ic1.OUT).right().length(1.0)
    elm.Wire("|-").to(ic2.TRG)

    # ---------- output ----------
    elm.Line().at(ic2.OUT).right().length(0.8)
    elm.Capacitor(polar=True).right().label("10µF", loc="top")
    o = elm.Dot()
    vol = elm.Potentiometer().at(o.center).down().toy(BOT).reverse().label("10k\nVOLUME", loc="top")
    elm.Line().at(vol.tap).right().length(1.5)
    elm.Dot(open=True).label("jack tip: to amp / speaker", loc="right")
    elm.Dot(open=True).at((vol.tap[0] + 1.5, BOT + 0.9)).label("sleeve (GND)", loc="right")
    elm.Line().down().toy(BOT)
