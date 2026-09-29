"""555 servo tester (Unit 10A). Run: python servo_tester.py -> servo_tester.svg"""
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="servo_tester.svg", show=False) as d:
    d.config(fontsize=12, unit=2.0)
    TOP, BOT = 9.0, -5.0
    ic = elm.Ic555().right().at((0, 0)).label("NE555", loc="bottom", ofst=(1.4, -0.6))
    x = ic.DIS[0] - 4.0
    elm.Line().at((x - 2.0, TOP)).right().tox(8)
    elm.Vdd().at((x - 2.0, TOP)).label("+5–6 V")
    elm.Line().at((x - 2.0, BOT)).right().tox(8)
    elm.Ground().at((x - 2.0, BOT))

    elm.Resistor().at((x, TOP)).down().length(2.2).label("R_A\n10k", loc="bottom")
    elm.Potentiometer().down().toy(ic.DIS[1]).label("22k\nPOSITION", loc="bottom")
    dis = elm.Dot()
    elm.Line().right().to(ic.DIS)
    # diode steering: charge through D1, discharge through R_B
    elm.Line().at(dis.center).down().length(0.6)
    j1 = elm.Dot()
    elm.Line().left().length(1.0)
    elm.Diode().down().label("D1\n1N4148", loc="bottom")
    j2a = elm.Line().right().length(1.0)
    j2 = elm.Dot()
    elm.Line().at(j1.center).right().length(1.0)
    elm.Resistor().down().toy(j2.center[1]).label("R_B\n270k", loc="bottom")
    elm.Line().left().to(j2.center)
    elm.Wire("-|").at(j2.center).to(ic.THR)
    elm.Wire("-|").at(j2.center).to(ic.TRG)
    elm.Capacitor().at(j2.center).down().toy(BOT).label("100nF", loc="bottom")
    elm.Line().at(ic.Vcc).up().toy(TOP)
    elm.Wire("|-").at(ic.RST).to((ic.Vcc[0], TOP - 0.6))
    elm.Line().at(ic.GND).down().toy(BOT)
    elm.Line().at(ic.CTL).right().length(0.6)
    elm.Capacitor().down().toy(BOT).label("10nF", loc="bottom")
    elm.Line().at(ic.OUT).right().tox(7.5)
    elm.Dot(open=True).label("to servo SIGNAL (orange)\nservo + and GND go to the rails", loc="top", ofst=(0, 0.2))
    elm.Capacitor(polar=True).at((x - 2.0, TOP)).down().toy(BOT).label("100µF", loc="top")
