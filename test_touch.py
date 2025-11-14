#!/usr/bin/env python3
import time
from hardware.touch import Touch
from hardware.display import W, H  # если W, H определены там же
# или просто W=480; H=320 если нужно быстро

def main():
    t = Touch(W, H)
    print("Touch test: жми по экрану (Ctrl+C для выхода)")
    try:
        while True:
            pos = t.read(samples=5)
            if pos is not None:
                print("Touch:", pos)
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        t.close()

if __name__ == "__main__":
    main()
