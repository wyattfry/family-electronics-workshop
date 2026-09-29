"""Car power path: Qi receiver -> TP4056 charger + load sharing (Unit 16).
Run: python power_path.py -> power_path.svg"""
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file="power_path.svg", show=False) as d:
    d.config(fontsize=11, unit=2.0)
    Y5, Y0, SYS, GND = 2.0, 0.0, 5.0, -5.0
    XVIN, XCHG, XFET, XDIV = 4.0, 6.5, 15.5, 12.6

    # Qi receiver module
    qi = elm.Ic(pins=[elm.IcPin(name="GND", side="right"), elm.IcPin(name="5V", side="right")],
                size=(2.4, 3.0), pinspacing=2.0, edgepadW=0.5).anchor("5V").at((2.4, Y5))
    qi.label("Qi receiver\npatch", loc="top")

    # TP4056 + DW01 module: IN+/IN- left, OUT+/OUT- right, B+/B- bottom
    chg = elm.Ic(pins=[elm.IcPin(name="IN-", side="left"), elm.IcPin(name="IN+", side="left"),
                       elm.IcPin(name="OUT-", side="right"), elm.IcPin(name="OUT+", side="right"),
                       elm.IcPin(name="B+", side="bottom"), elm.IcPin(name="B-", side="bottom")],
                 size=(3.4, 3.6), pinspacing=2.0, edgepadW=0.5, edgepadH=0.8).anchor("IN+").at((XCHG, Y5))
    chg.label("TP4056 + DW01\ncharger + protection", loc="top")

    # 5 V from the Qi patch = VIN
    elm.Line().at(qi["5V"]).right().tox(XVIN)
    vin = elm.Dot()
    elm.Line().right().to(chg["IN+"])
    elm.Line().at(qi.GND).right().to(chg["IN-"])
    elm.Resistor().at(vin.center).down().to((XVIN, Y0)).label("100k", loc="bottom", fontsize=10)
    elm.Dot().at((XVIN, Y0))
    elm.Label().at((XVIN - 0.2, Y5 + 0.45)).label("VIN", halign="right")

    # battery on B+/B-
    elm.Line().at(chg["B+"]).down().length(0.8)
    elm.Battery().right().to((chg["B-"][0], chg["B+"][1] - 0.8)).label("1S LiPo\n500–1000 mAh", loc="bottom")
    elm.Line().up().to(chg["B-"])

    # SYS rail: VIN through a Schottky
    elm.Line().at(vin.center).up().toy(SYS)
    elm.Diode().right().tox(XFET).label("SS14 Schottky", loc="top")
    sysn = elm.Dot()

    # OUT+ through the P-MOSFET (drain at OUT+, source at SYS)
    elm.Line().at(chg["OUT+"]).right().tox(XFET)
    elm.Dot()
    q = elm.PFet(bulk=True).right().reverse().anchor("drain").at((XFET, Y5))
    q.label("AO3401\nP-MOSFET", loc="right", ofst=(0.6, 0))
    elm.Line().at(q.source).up().to(sysn.center)
    # gate follows VIN
    elm.Line().at(q.gate).left().tox(XFET - 1.6)
    elm.Line().up().toy(SYS - 1.2)
    elm.Line().left().tox(XVIN)
    elm.Dot()

    # SYS out through the power switch
    elm.Line().at(sysn.center).right().length(1.0)
    elm.Switch().right().label("POWER", loc="top")
    elm.Dot(open=True).label("SYS: XIAO 5V pin, DRV8833 VM,\nsteering servo, lights", loc="right")

    # battery-voltage divider off OUT+
    ob = elm.Dot().at((XDIV, Y5))
    elm.Line().down().toy(Y0 - 0.8)
    elm.Resistor().down().length(1.8).label("100k", loc="bottom", fontsize=10)
    vb = elm.Dot()
    elm.Line().right().length(1.0)
    elm.Dot(open=True).label("D8: battery voltage (ADC)", loc="right")
    elm.Resistor().at(vb.center).down().toy(GND).label("100k", loc="bottom", fontsize=10)

    # ground: system ground is OUT- (the protected side), never B-
    elm.Line().at(chg["OUT-"]).right().length(0.4)
    elm.Line().down().toy(GND)
    elm.Line().at((XVIN, Y0)).down().toy(GND)
    elm.Line().at((XVIN, GND)).right().tox(vb.center[0])
    elm.Ground().at((XVIN, GND)).label("GND = OUT- / IN-", loc="left")

    elm.Label().at((XVIN + 0.5, GND - 1.4)).label(
        "ON THE PAD: VIN (5 V) feeds SYS through the Schottky and turns the MOSFET off, so the charger sees only the cell.\n"
        "OFF THE PAD: the 100k pulls the gate low, the MOSFET turns on, and the cell powers SYS.\n"
        "Charge detect (not drawn): VIN through a 100k/100k divider to D9.",
        halign="left", fontsize=10)
