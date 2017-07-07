# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

"""Provides a shared preferences dictionary"""
import os

# TODO: replace defaults with your own values
defaults = {
'example_entry': 'I remember stuff',
 }

from desktopcouch.records.server import CouchDatabase
from desktopcouch.records.record import Record
import gtk
import gobject
from UserDict import IterableUserDict

class User_dict(IterableUserDict):
    ''' a dictionary with extra methods:

    persistence: load, save and db_connect
    gobject signals: connect and emit.
    
    Don't use this directly. Please use the preferences instance.'''
    
    def __init__(self):
        IterableUserDict.__init__(self)
        # Set up couchdb.
        self._db_name = "simple-player"
        self._key = None

        self._record_type = (
            "http://wiki.ubuntu.com/Quickly/RecordTypes/SimplePlayer/"
            "Preferences")
        
        # set up signals in a separate class
        # because IterableUserDict uses self.data (documented)
        # and gtk.Invisible appears to use self.data.
        class Publisher(gtk.Invisible):
            __gsignals__ = {'changed' : (gobject.SIGNAL_RUN_LAST,
                 gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
                 'loaded' : (gobject.SIGNAL_RUN_LAST,
                 gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
        
        publisher = Publisher()
        self.emit  = publisher.emit
        self.connect  = publisher.connect

    def db_connect(self):
        # logging.basicConfig will be called now
        self._database = CouchDatabase(self._db_name, create=True)

    def save(self):
        # couchdb
        self._database.update_fields(self._key, self.data)

 
    def load(self):
        # couchdb
        self.update({"record_type": self._record_type})

        results = self._database.get_records(
            record_type=self._record_type, create_view=True)

        if len(results.rows) == 0:
            # No preferences have ever been saved
            # save them before returning.
            self._key = self._database.put_record(Record(self.data))
        else:
            self.update(results.rows[0].value)
            del self['_rev']
            self._key = results.rows[0].value["_id"]
        self.emit('loaded', None)

    def update(self, new_data):
        """ interface for dictionary 
        
        send changed signal when appropriate """
        changed_keys = []
        for key in new_data.keys():
            if new_data.get(key) != self.data.get(key):
                changed_keys.append(key)
        self.data.update(new_data)
        if changed_keys:
            self.emit('changed', tuple(changed_keys))

    def __setitem__(self, key, value):
        """ interface for dictionary
        
        send changed signal when appropriate """
        if value != self.data.get(key):
            self.data[key] =  value
            self.emit('changed', (key,))

preferences = User_dict()
preferences.update(defaults)
