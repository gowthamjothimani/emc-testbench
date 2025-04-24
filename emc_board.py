import Adafruit_BBIO.GPIO as GPIO
from smbus2 import SMBus

class EMC_Board:
    def __init__(self):
        # Initialize the byte with all bits set to 0
        reset_max7320 = "P8_11"
        GPIO.setup(reset_max7320, GPIO.OUT)
        GPIO.output(reset_max7320,GPIO.HIGH)
        # Define constants
        self.I2C_BUS = 2              # I      C bus (e.g., /dev/i2c-1)
        self.SLAVE_ADDR = 0x58
        self.bits = 0b10000000
        self.write_max7320_zero(self.bits)
        self.efuse_badge_unit_fault_pin = "P8_8"
        self.efuse_alarm_unit_fault_pin = "P8_12"
        self.efuse_gas_unit_fault_pin = "P9_23"
        self.gas_power_in_pin = "P9_27"

        GPIO.setup(self.efuse_badge_unit_fault_pin, GPIO.IN)
        GPIO.setup(self.efuse_alarm_unit_fault_pin, GPIO.IN)
        GPIO.setup(self.efuse_gas_unit_fault_pin, GPIO.IN)
        GPIO.setup(self.gas_power_in_pin, GPIO.IN)

    def read_gas_efuse(self):
        return "Good" if GPIO.input(self.efuse_gas_unit_fault_pin) == 1 else "Error"

    def read_badge_efuse(self):
        return "Good" if GPIO.input(self.efuse_badge_unit_fault_pin) == 1 else "Error"

    def read_alarm_efuse(self):
        return "Good" if GPIO.input(self.efuse_alarm_unit_fault_pin) == 1 else "Error"

    def read_gas_power_in(self):
        return "12V" if GPIO.input(self.gas_power_in_pin) == 1 else "0V"

    def reset(self):
            self.bits = 0b10000000
            self.write_max7320_zero(self.bits)

    def write_max7320_zero(self,bits):
        print(bin(bits))
        try:
            # Write 0x00 to set all outputs to LOW
            with SMBus(self.I2C_BUS) as bus:
                bus.write_byte(self.SLAVE_ADDR, bits)
            print("Successfully wrote",bits)
        except OSError as e:
            print(f"I      C Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def _turn_on_bit(self, bit_position):
        """Turn on a specific bit (0 to 7) while retaining the other bits."""
        if 0 <= bit_position <= 7:
            self.bits |= (1 << bit_position)
            self.write_max7320_zero(self.bits)
        else:
            raise ValueError("Bit position must be between 0 and 7.")

    def _turn_off_bit(self, bit_position):
        """Turn off a specific bit (0 to 7) while retaining the other bits."""
        if 0 <= bit_position <= 7:
            self.bits &= ~(1 << bit_position)
            self.write_max7320_zero(self.bits)
        else:
            raise ValueError("Bit position must be between 0 and 7.")

    # Define methods for each bit (0-7) for both turning on and off
    def turn_on_efuse_gas(self):
        self._turn_on_bit(4)

    def turn_off_efuse_gas(self):
        self._turn_off_bit(4)

    def turn_on_efuse_alarm(self):
        self._turn_on_bit(6)

    def turn_off_efuse_alarm(self):
        self._turn_off_bit(6)

    def turn_on_efuse_badge(self):
        self._turn_on_bit(5)

    def turn_off_efuse_badge(self):
        self._turn_off_bit(5)

    def turn_on_alarm_red_lamp(self):
        self._turn_on_bit(2)

    def turn_off_alarm_red_lamp(self):
        self._turn_off_bit(2)

    def turn_on_alarm_green_lamp(self):
        self._turn_on_bit(1)

    def turn_off_alarm_green_lamp(self):
        self._turn_off_bit(1)

    def turn_on_alarm_sound(self):
        self._turn_on_bit(3)

    def turn_off_alarm_sound(self):
        self._turn_off_bit(3)

    def turn_on_badge_lamp(self):
        self._turn_on_bit(0)

    def turn_off_badge_lamp(self):
        self._turn_off_bit(0)