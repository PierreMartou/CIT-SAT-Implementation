# This is a sample Python script.
import time
import multiprocessing
import threading


class FeatureModel:
    # pre : A will initialize the "database" and closes it.
    # B and C both Optional.
    # If C or (B&C) is active, db = 2. If only B is active, db = 1. If none is active, db = 0.
    def __init__(self):
        self.database = None
        self.lock = threading.Lock()
        self.A = None
        self.B = None
        self.C = None

    def A_init(self):
        self.database = 0
        self.A = True
    def A_close(self):
        self.database = None
        self.A = False

    def B_init(self):
        self.lock.acquire()
        tempDb = self.database
        time.sleep(0.5)
        self.database = tempDb + 1
        self.lock.release()
        self.B = True
    def B_close(self):
        self.B = False

    def C_init(self):
        # Error : should lock before !
        # self.lock.acquire()
        tempDb = self.database
        time.sleep(1)
        self.database = tempDb + 1
        # self.lock.release()
        self.C = True
    def C_close(self):
        self.C = False

    def test_validity(self, expected):
        return self.database == expected


def print_error_msg(instance, mode, test, expected):
    if not instance.test_validity(expected):
        print(str(mode) + " detected an error at test " + str(test))
    return instance.test_validity(expected)

def threading_transitions(transitions):
    threads = []
    for transition in transitions:
        t = threading.Thread(target=transition)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def CIT():
    mode = "Interaction testing"
    system = FeatureModel()
    n = 1
    valid = True
    # First test, both False
    system.A_init()
    system.B_close()
    system.C_close()
    valid = valid and print_error_msg(system, mode, n, 0)

    # Second test, only B True
    n += 1
    system.B_init()
    valid = valid and print_error_msg(system, mode, n, 1)

    # Third test, both True
    n += 1
    system.C_init()
    valid = valid and print_error_msg(system, mode, n, 2)

    # Fourth test, only C True
    n += 1
    system.B_close()
    valid = valid and print_error_msg(system, mode, n, 2)

    if valid:
        print("Interaction testing, result: correct implementation (" + str(n) + " tests)")
    else:
        print("Interaction testing, result: incorrect implementation (" + str(n) + " tests)")

def CTT():
    mode = "Transition testing"
    system = FeatureModel()
    n = 1
    valid = True
    # First test, both False
    system.A_init()
    system.B_close()
    system.C_close()
    valid = valid and print_error_msg(system, mode, n, 0)

    # Second test, both True
    n += 1
    threading_transitions([system.B_init, system.C_init])
    valid = valid and print_error_msg(system, mode, n, 2)

    # Third test, both False
    n += 1
    threading_transitions([system.B_close, system.C_close])
    valid = valid and print_error_msg(system, mode, n, 2)

    # Fourth test, only C True
    n += 1
    t2 = threading.Thread(target=system.C_init)
    t2.start()
    valid = valid and print_error_msg(system, mode, n, 3)

    # Fifth test, only B True
    n += 1
    t1 = threading.Thread(target=system.B_init)
    t2 = threading.Thread(target=system.C_close)
    t2.start()
    t1.start()
    valid = valid and print_error_msg(system, mode, n, 4)

    # Sixth test, only C True
    n += 1
    t1 = threading.Thread(target=system.B_close)
    t2 = threading.Thread(target=system.C_init)
    t2.start()
    t1.start()
    valid = valid and print_error_msg(system, mode, n, 5)

    if valid:
        print("Transition testing, result: correct implementation (" + str(n) + " tests, or 5 transitions).")
    else:
        print("Transition testing, result: incorrect implementation (" + str(n) + " tests, or 5 transitions).")

CIT()
CTT()
