# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
class FeatureModel:
    # pre : A will initialize the "database" and closes it.
    # B and C both Optional.
    # If C or (B&C) is active, db = 2. If only B is active, db = 1. If none is active, db = 0.
    def __init__(self):
        self.database = None
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
        if self.database < 1:
            self.database = 1
        self.B = True
    def B_close(self):
        if self.database == 1:
            self.database = 0
        self.B = False

    def C_init(self):
        if self.database < 2:
            self.database = 2
        self.C = True
    def C_close(self):
        if self.database == 2:
            self.database = 0  # Error, should check whether B is still active. So from BC True to B True, error.
        self.C = False

    def test_validity(self):
        if self.C and self.database == 2:
            return True
        if self.B and self.database == 1:
            return True
        if not self.C and not self.B and self.database == 0:
            return True
        return False

def print_error_msg(instance, mode, test):
    if not instance.test_validity():
        print(str(mode) + " detected an error at test " + str(test))
    return instance.test_validity()

def CIT():
    mode = "Interaction testing"
    system = FeatureModel()
    n = 1
    valid = True
    # First test, both False
    system.A_init()
    system.B_close()
    system.C_close()
    valid = valid and print_error_msg(system, mode, n)

    # Second test, only B True
    n += 1
    system.B_init()
    valid = valid and print_error_msg(system, mode, n)

    # Third test, both True
    n += 1
    system.C_init()
    valid = valid and print_error_msg(system, mode, n)

    # Fourth test, only C True
    n += 1
    system.B_close()
    valid = valid and print_error_msg(system, mode, n)

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
    valid = valid and print_error_msg(system, mode, n)

    # Second test, both True
    n += 1
    system.B_init()
    system.C_init()
    valid = valid and print_error_msg(system, mode, n)

    # Third test, both False
    n += 1
    system.B_close()
    system.C_close()
    valid = valid and print_error_msg(system, mode, n)

    # Fourth test, only C True
    n += 1
    system.C_init()
    valid = valid and print_error_msg(system, mode, n)

    # Fifth test, only B True
    n += 1
    system.B_init()
    system.C_close()
    valid = valid and print_error_msg(system, mode, n)

    # Sixth test, only C True
    n += 1
    system.C_init()
    system.B_close()
    valid = valid and print_error_msg(system, mode, n)

    if valid:
        print("Transition testing, result: correct implementation (" + str(n) + " tests, or 5 transitions).")
    else:
        print("Transition testing, result: incorrect implementation (" + str(n) + " tests, or 5 transitions).")

CIT()
CTT()
