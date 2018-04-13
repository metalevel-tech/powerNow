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
        item_1 = Gtk.MenuItem('htop')
        # item_about.connect('activate', self.about)
        menu.append(item_1)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # quit
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def show_seconds(self):
        t = 0
        power_path = '/sys/class/power_supply/BAT0/power_now'
        voltage_path = '/sys/class/power_supply/BAT0/voltage_now'
        current_path = '/sys/class/power_supply/BAT0/current_now'
            
        while True:
            if os.path.exists(power_path):
                power_file = open(power_path,'r')
                power_value = int(power_file.readline())
                power_file.close()
                power_watts = str(round(power_value / 1000000, 3))
            elif os.path.exists(voltage_path) and os.path.exists(current_path):
                voltage_file = open(voltage_path,'r')
                voltage_value = int(voltage_file.readline())
                voltage_file.close()
                current_file = open(current_path,'r')
                current_value = int(current_file.readline())
                current_file.close()
                power_value = int(voltage_value * current_value / 1000000)
                power_watts = str(round(power_value / 1000000, 3))
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                power_watts + " W", self.app,
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
