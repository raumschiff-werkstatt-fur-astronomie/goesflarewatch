# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

# Uncomment the lines below to enable auto-start on boot
import solar_flare_alert
if solar_flare_alert.RUN:
    solar_flare_alert._main()
