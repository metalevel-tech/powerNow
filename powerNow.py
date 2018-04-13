#!/usr/bin/env python3
import signal
import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread

class Indicator():
    def __init__(self):
        self.app = 'Current Power Consumption'
        iconpath = "/usr/share/unity/icons/launcher_bfb.png"

        self.indicator = AppIndicator3.Indicator.new(
            self.app, iconpath,
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.indicator.set_menu(self.create_menu())
        self.indicator.set_label("PowerNow", self.app)
        # the thread:
        self.update = Thread(target=self.show_seconds)
        # daemonize the thread to make the indicator stopable
        self.update.setDaemon(True)
        self.update.start()

    def create_menu(self):
        menu = Gtk.Menu()
        # menu item 1
        #item_1 = Gtk.MenuItem('Menu item')
        # item_about.connect('activate', self.about)
        #menu.append(item_1)
        # separator
        #menu_sep = Gtk.SeparatorMenuItem()
        #menu.append(menu_sep)
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def show_seconds(self):
        t = 0
        while True:
            power_path = '/sys/class/power_supply/BAT0/power_now'
            if os.path.exists(power_path):
                power_file = open(power_path,'r')
                power_value = int(power_file.readline())
                power_file.close()
                current_power = str(round(power_value / 1000000, 3))

            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                current_power + " W", self.app,
                priority=GObject.PRIORITY_DEFAULT
                )
            time.sleep(10)
            t += 10

    def stop(self, source):
        Gtk.main_quit()

Indicator()
# this is where we call GObject.threads_init()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
