#!/usr/bin/env python3
import signal
import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, AppIndicator3, GObject
import time
from threading import Thread

def htop(self):
    return os.system("gnome-terminal -x bash -c 'if [[ -f /usr/bin/htop ]]; then htop; else echo sudo apt install htop ? && sudo apt install htop && htop; fi; exec bash'")

def sudohtop(self):
    return os.system("gnome-terminal -x bash -c 'if [[ -f /usr/bin/htop ]]; then sudo htop; else echo sudo apt install htop ? && sudo apt install htop && sudo htop; fi; exec bash'")

def sudopowertop(self):
    return os.system("gnome-terminal -x bash -c 'if [[ -f /usr/sbin/powertop ]]; then sudo powertop; else echo sudo apt install powertop ? && sudo apt install powertop && sudo powertop; fi; exec bash'")

def sudotlpstat(self):
    return os.system("gnome-terminal -x bash -c 'if [[ -f /usr/sbin/tlp ]]; then sudo tlp-stat | less; else echo sudo apt install tlp ? && sudo apt install tlp && sudo tlp-stat | less; fi; exec bash'")

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
        item_1.connect('activate', htop)
        menu.append(item_1)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # menu item 2
        item_2 = Gtk.MenuItem('sudo htop')
        item_2.connect('activate', sudohtop)
        menu.append(item_2)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # menu item 3
        item_3 = Gtk.MenuItem('sudo powertop')
        item_3.connect('activate', sudopowertop)
        menu.append(item_3)
        # separator
        menu_sep = Gtk.SeparatorMenuItem()
        menu.append(menu_sep)
        # menu item 4
        item_4 = Gtk.MenuItem('sudo tlp-stat')
        item_4.connect('activate', sudotlpstat)
        menu.append(item_4)
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
                power_watts = power_watts + " W"
            elif os.path.exists(voltage_path) and os.path.exists(current_path):
                voltage_file = open(voltage_path,'r')
                voltage_value = int(voltage_file.readline())
                voltage_file.close()
                current_file = open(current_path,'r')
                current_value = int(current_file.readline())
                current_file.close()
                power_value = int(voltage_value * current_value / 1000000)
                power_watts = str(round(power_value / 1000000, 3))
                power_watts = power_watts + " W"
            else :
                power_watts = "PowerNow"
            # apply the interface update using  GObject.idle_add()
            GObject.idle_add(
                self.indicator.set_label,
                power_watts, self.app,
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
