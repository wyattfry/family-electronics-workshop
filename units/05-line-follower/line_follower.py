"""Line follower, one side (Unit 5). Run: python line_follower.py -> line_follower.svg"""
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="line_follower.svg", show=False) as d:
    d.config(fontsize=12, unit=2.2)
    TOP, BOT, XR = 9, 0, 20
    elm.Line().at((0, TOP)).right().tox(XR)
    elm.Vdd().at((0, TOP)).label("V+ (4×AA, ~6 V)")
    elm.Line().at((0, BOT)).right().tox(XR)
    elm.Ground().at((0, BOT))

    # --- SENSOR: TCRT5000 IR LED + phototransistor ---
    elm.Resistor().at((0, TOP)).down().label("330Ω", loc="bottom")
    elm.LED().down().toy(BOT).label("IR LED", loc="bottom")
    elm.Resistor().at((3, TOP)).down().length(3).label("10k", loc="bottom")
    s = elm.Dot().label("S", loc="right", ofst=(0.1, 0.25))
    q = elm.NpnPhoto().right().anchor("collector").at(s.center).label("photo-\ntransistor", loc="left", ofst=(-0.3, 0))
    elm.Line().at(q.emitter).down().toy(BOT)

    # --- THRESHOLD pot ---
    pot = elm.Potentiometer().at((6, TOP)).down().toy(BOT).label("10k\nTHRESHOLD", loc="bottom")

    # --- COMPARATOR: S to (−), threshold to (+) ---
    op = elm.Opamp(leads=True).right().anchor("in1").at((8.5, s.center[1])).label("½ LM393", loc="center", ofst=(-0.2, 0), fontsize=11)
    elm.Line().at(s.center).right().to(op.in1)
    elm.Wire("-|").at(pot.tap).to(op.in2)
    o = elm.Dot().at(op.out)
    elm.Resistor().at(o.center).up().toy(TOP).label("10k\npull-up", loc="bottom")
    elm.Resistor().at(o.center).right().length(2.2).label("100Ω", loc="top")
    g = elm.Dot()

    # --- MOTOR SWITCH: logic-level MOSFET on the low side ---
    m = elm.NFet(bulk=False).right().anchor("gate").at(g.center).reverse().label("IRLZ44N", loc="right", ofst=(0.5, 0))
    elm.Line().at(m.source).down().toy(BOT)
    elm.Line().at(m.drain).up().length(0.5)
    md = elm.Dot()
    elm.Motor().up().length(2.2).label("motor", loc="top")
    mt = elm.Dot()
    elm.Line().up().toy(TOP)
    # flyback diode (band to V+) and noise cap, both across the motor
    elm.Line().at(md.center).right().length(1.3)
    elm.Diode().up().to((md.center[0] + 1.3, mt.center[1])).label("1N5819", loc="bottom")
    elm.Line().left().to(mt.center)
    elm.Line().at((md.center[0] + 1.3, md.center[1])).right().length(2.6)
    elm.Capacitor().up().toy(mt.center[1]).label("100nF", loc="bottom")
    elm.Line().left().length(2.6)
