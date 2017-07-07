# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gtk
import logging

from simple_player import (
    AboutSimplePlayerDialog, PreferencesSimplePlayerDialog, BuilderGlue)
import simple_player.helpers as helpers
from simple_player.preferences import preferences

import gettext
from gettext import gettext as _
gettext.textdomain('simple-player')


# This class is meant to be subclassed by SimplePlayerWindow.  It provides
# common functions and some boilerplate.
class BaseSimplePlayerWindow(gtk.Window):
    __gtype_name__ = "BaseSimplePlayerWindow"

    # To construct a new instance of this method, the following notable 
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing
    
    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated BaseSimplePlayerWindow object.
        """
        builder = helpers.get_builder('SimplePlayerWindow')
        new_object = builder.get_object("simple_player_window")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a SimplePlayerWindow object with it in order to finish
        initializing the start of the new SimplePlayerWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = BuilderGlue.BuilderGlue(builder, self)
        self.preferences_dialog = None

        # Optional Launchpad integration
        # This shouldn't crash if not found as it is simply used for bug reporting.
        # See https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding
        # for more information about Launchpad integration.
        try:
            import LaunchpadIntegration
            LaunchpadIntegration.add_items(self.ui.helpMenu, 1, False, True)
            LaunchpadIntegration.set_sourcepackagename('simple-player')
        except:
            pass

        # Optional application indicator support
        # Run 'quickly add indicator' to get started.
        # More information:
        #  http://owaislone.org/quickly-add-indicator/
        #  https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
        try:
            from simple_player import indicator
            # self is passed so methods of this class can be called from indicator.py
            # Comment this next line out to disable appindicator
            self.indicator = indicator.new_application_indicator(self)
        except:
            pass

    def contentsMenuItem_activate_event(self, widget, data=None):
        helpers.show_uri(self, "ghelp:%s" % helpers.get_help_uri())

    def aboutMenuItem_activate_event(self, widget, data=None):
        """Display the about box for simple-player."""
        about = AboutSimplePlayerDialog.AboutSimplePlayerDialog()
        response = about.run()
        about.destroy()

    def preferencesMenuItem_activate_event(self, widget, data=None):
        """Display the preferences window for simple-player."""

        """ From the PyGTK Reference manual
           Say for example the preferences dialog is currently open,
           and the user chooses Preferences from the menu a second time;
           use the present() method to move the already-open dialog
           where the user can see it."""
        if self.preferences_dialog is not None:
            logging.debug('show existing preferences_dialog')
            self.preferences_dialog.present()
        else:
            logging.debug('create new preferences_dialog')
            self.preferences_dialog = PreferencesSimplePlayerDialog.PreferencesSimplePlayerDialog()
            self.preferences_dialog.connect('destroy', self.on_preferences_dialog_destroyed)
            self.preferences_dialog.show()
        # destroy command moved into dialog to allow for a help button

    def quitMenuItem_activate_event(self, widget, data=None):
        """Signal handler for closing the SimplePlayerWindow."""
        self.destroy()

    def destroy_event(self, widget, data=None):
        """Called when the SimplePlayerWindow is closed."""
        # Clean up code for saving application state should be added here.
        gtk.main_quit()

    def on_preferences_dialog_destroyed(self, widget, data=None):
        '''only affects gui
        
        logically there is no difference between the user closing,
        minimising or ignoring the preferences dialog'''
        logging.debug('on_preferences_dialog_destroyed')
        # to determine whether to create or present preferences_dialog
        self.preferences_dialog = None

if __name__ == "__main__":
    window = BaseSimplePlayerWindow()
    window.show()
    gtk.main()
