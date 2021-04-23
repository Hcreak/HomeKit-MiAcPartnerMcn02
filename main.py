import logging
import signal

from miio_wrapper import *
from sqldata import *
from webshow import *

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap.const import CATEGORY_AIR_CONDITIONER

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")
import time

class XiaoMiAcPartnerMcn02(Accessory):

    category = CATEGORY_AIR_CONDITIONER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # https://github.com/ikalchev/HAP-python/blob/dev/pyhap/resources/services.json#L514
        serv_HC = self.add_preload_service(
            'Thermostat', ["CurrentHeatingCoolingState",
                             "TargetHeatingCoolingState",
                             "CurrentTemperature",
                             "TargetTemperature",
                             "TemperatureDisplayUnits"]
        )

        # https://github.com/ikalchev/HAP-python/blob/dev/pyhap/resources/characteristics.json#L319
        self.char_curmode = serv_HC.configure_char('CurrentHeatingCoolingState')

        # https://github.com/ikalchev/HAP-python/blob/dev/pyhap/resources/characteristics.json#L1401
        self.char_tarmode = serv_HC.configure_char(
            'TargetHeatingCoolingState',
            valid_values={"Cool": 2, "Heat": 1, "Off": 0},
            setter_callback=self._on_tarmode_changed
        )

        self.char_curtemp = serv_HC.configure_char('CurrentTemperature')

        self.char_tartemp = serv_HC.configure_char(
            'TargetTemperature', value=miio_get_temp(),
            setter_callback=self._on_tartemp_changed
        )

        serv_HC.configure_char('TemperatureDisplayUnits', value=0)


    def _on_tartemp_changed(self, value):
        miio_set_temp(value)
        print('[{}] TargetTemperature {}'.format(time.asctime(time.localtime()), value))

    def _on_tarmode_changed(self, value):
        # 让Siri开启空调会打到自动模式 强行更改目标模式为关机前状态 继续执行
        if value == 3:
            value = miio_get_mode()
            self.char_tarmode.set_value(value)
        
        if value == self.char_curmode.value:
            return

        if value == 0:
            miio_set_power(False)
            print('Turn off')
        else:
            if self.char_curmode.value == 0:
                miio_set_power(True)
                print('Turn on')
            if value != miio_get_mode():
                miio_set_mode(value)
        print('[{}] TargetHeatingCoolingState {}'.format(time.asctime(time.localtime()), value))
        self.char_curmode.set_value(value)


    @Accessory.run_at_interval(60)
    async def run(self):
        self.char_curmode.set_value(miio_get_mode_new())
        self.char_curtemp.set_value(miio_get_temp())

        load_power = miio_get_load()
        energy = compute_energy(load_power)

        put_load_power(load_power)
        put_energy_count_day(energy)
        put_energy_count_month(energy)


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return XiaoMiAcPartnerMcn02(driver, 'MyAcPartner')


def run_webshow():
    app.run(host='0.0.0.0', port=5000, debug=False) 

if __name__ == '__main__':
    # 先启动flask 防止线程阻塞
    import _thread
    _thread.start_new_thread(run_webshow,())

    # Start the accessory on port 51826
    driver = AccessoryDriver(port=51826)

    # Change `get_accessory` to `get_bridge` if you want to run a Bridge.
    driver.add_accessory(accessory=get_accessory(driver))

    # We want SIGTERM (terminate) to be handled by the driver itself,
    # so that it can gracefully stop the accessory, server and advertising.
    signal.signal(signal.SIGTERM, driver.signal_handler)

    # Start it!
    driver.start()
