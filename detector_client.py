import sys


if __name__ == '__main__':
    name = sys.argv[1]
    address = sys.argv[2]
    port = int(sys.argv[3])

    if name == "Dexela":
        from detectors import Dexela
        det = Dexela()
    elif name == "XRD1611":
        from detectors import XRD1611
        det = XRD1611()
    elif name == "XRD1622":
        from detectors import XRD1622
        det = XRD1622()
    elif name == "WidePIX":
        from detectors import WidePIX
        det = WidePIX()
    else:
        from detectors import Dummy
        det = Dummy()

    det.init_client(address, port)
    det.work()
