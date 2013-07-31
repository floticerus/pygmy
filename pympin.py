#!/usr/bin/env python

import sys, os, mimetypes, re, glob, glib, hashlib, gi
from gi.repository import Gtk, Gst, Pango
gi.require_version( "Gst", "1.0" )

class Pympin( Gtk.Window ):
    directories = [
        "/home/kevin/player/songs",
        "/mnt/stuff/tunez"
    ]

    def __init__( self ):
        Gtk.Window.__init__( self, title = "pympin" )

        glib.threads_init()

        self.set_default_size( 800, 400 )

        self.playing = False

        self.artist_store = Gtk.ListStore( str )

        self.album_store = Gtk.ListStore( str )

        # full file path, track #, title, artist, album, year, time
        self.song_store = Gtk.ListStore( str, str, str, str, str, str, str, str )

        # full the stores with temporary data
        self.artist_store.append([ "test" ])
        self.artist_store.append(["test2"])
        self.artist_store.append(["test3"])
        self.artist_store.append(["test4"])
        self.artist_store.append(["test5"])
        self.artist_store.append(["test6"])
        self.artist_store.append(["test7"])
        self.artist_store.append(["test8"])
        self.artist_store.append(["test9"])
        self.artist_store.append(["test10"])
        self.artist_store.append(["test11"])
        self.artist_store.append(["test12"])
        self.artist_store.append(["test13"])
        self.artist_store.append(["test14"])
        self.artist_store.append(["test15"])
        self.artist_store.append(["test16"])
        self.artist_store.append(["test17"])
        self.artist_store.append(["test18"])
        self.artist_store.append(["test19"])
        self.artist_store.append(["test20"])
        self.artist_store.append(["test21"])
        self.artist_store.append(["test22"])

        self.album_store.append(["test"])
        self.album_store.append(["test2"])
        self.album_store.append(["test3"])
        self.album_store.append(["test4"])
        self.album_store.append(["test5"])
        self.album_store.append(["test6"])
        self.album_store.append(["test7"])
        self.album_store.append(["test8"])
        self.album_store.append(["test9"])
        self.album_store.append(["test10"])
        self.album_store.append(["test11"])
        self.album_store.append(["test12"])
        self.album_store.append(["test13"])
        self.album_store.append(["test14"])
        self.album_store.append(["test15"])
        self.album_store.append(["test16"])
        self.album_store.append(["test17"])
        self.album_store.append(["test18"])
        self.album_store.append(["test19"])
        self.album_store.append(["test20"])
        self.album_store.append(["test21"])
        self.album_store.append(["test22"])

        self.build_ui()

        glib.idle_add( self.find_songs )

    def build_ui( self ):
        grid = Gtk.Grid()
        self.add( grid )

        # toolbar stuff
        fixed = Gtk.Fixed()
        toolbar = Gtk.HBox()
        fixed.add( toolbar )

        # previous button
        self.button_previous = Gtk.Button( "" )
        self.button_previous.set_image( self.get_image( Gtk.STOCK_MEDIA_PREVIOUS ) )
        #self.button_previous.connect("clicked", self.on_button_previous_clicked)
        toolbar.pack_start( self.button_previous, True, True, 2 )

        # play/pause button
        self.button_play = Gtk.Button( "" )
        self.button_play.set_image( self.get_image( Gtk.STOCK_MEDIA_PLAY ) )
        self.button_play.connect( "clicked", self.play_pause )
        toolbar.pack_start( self.button_play, True, True, 2 )

        # stop button
        self.button_stop = Gtk.Button( "" )
        self.button_stop.set_sensitive( False )
        self.button_stop.set_image( self.get_image( Gtk.STOCK_MEDIA_STOP ) )
        self.button_stop.connect( "clicked", self.do_stop )
        toolbar.pack_start( self.button_stop, True, True, 2 )

        # next button
        self.button_next = Gtk.Button( "" )
        self.button_next.set_image( self.get_image( Gtk.STOCK_MEDIA_NEXT ) )
        #self.button_next.connect("clicked", self.on_button_play_clicked)
        toolbar.pack_start( self.button_next, True, True, 2 )

        #box.pack_start(fixed, True, True, 0)

        # add the fixed button bar to the grid
        grid.add( fixed )

        # browser stuff
        browser = Gtk.VPaned()
        #browser_paned = Gtk.VPaned()
        #browser.add(browser_paned)
        grid.attach_next_to( browser, fixed, Gtk.PositionType.BOTTOM, 1, 1 )

        # create columns for artist/album filters
        columns = Gtk.HBox()
        columns.set_size_request( 0, 150 )

        # define cell renderer
        cell_renderer = Gtk.CellRendererText()

        # add ellipsis with pango
        cell_renderer.props.ellipsize = Pango.EllipsizeMode.END

        # artist list
        artists_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.artists = Gtk.TreeView( self.artist_store )
        artist_column = Gtk.TreeViewColumn( "Artist", cell_renderer, text = 0 )
        self.artists.append_column( artist_column )
        artists_scroll.add( self.artists )
        # allow multiple selected items
        self.artists.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )

        #album list
        albums_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.albums = Gtk.TreeView( self.album_store )
        album_column = Gtk.TreeViewColumn( "Album", cell_renderer, text = 0 )
        self.albums.append_column( album_column )
        albums_scroll.add( self.albums )
        # allow multiple selected items
        self.albums.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )

        # add items to the columns
        columns.pack_start( artists_scroll, True, True, 0 )
        columns.pack_start( albums_scroll, True, True, 0 )
        #columns.add(self.artists)

        # song list
        songs_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.songs = Gtk.TreeView( self.song_store )
        songs_columns = {
            "playing": Gtk.TreeViewColumn( "", cell_renderer, text = 0 ),
            "track": Gtk.TreeViewColumn( "#", cell_renderer, text = 2 ),
            "title": Gtk.TreeViewColumn( "Title", cell_renderer, text = 3 ),
            "artist": Gtk.TreeViewColumn( "Artist", cell_renderer, text = 4 ),
            "album": Gtk.TreeViewColumn( "Album", cell_renderer, text = 5 ),
            "year": Gtk.TreeViewColumn( "Year", cell_renderer, text = 6 ),
            "time": Gtk.TreeViewColumn( "Time", cell_renderer, text = 7 )
        }

        # set all columns except playing as resizable
        for column in songs_columns:
            if column != "playing":
                songs_columns[column].set_resizable( True )

        # set title, artist, and album to expand
        songs_columns["title"].set_expand( True )
        songs_columns["artist"].set_expand( True )
        songs_columns["album"].set_expand( True )

        # make sure we add them in the proper order
        self.songs.append_column( songs_columns["playing"] )
        self.songs.append_column( songs_columns["track"] )
        self.songs.append_column( songs_columns["title"] )
        self.songs.append_column( songs_columns["artist"] )
        self.songs.append_column( songs_columns["album"] )
        self.songs.append_column( songs_columns["year"] )
        self.songs.append_column( songs_columns["time"] )

        songs_scroll.add( self.songs )
        self.songs.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )

        # put together the browser window
        browser.add( columns )
        browser.add( songs_scroll )

    #def get_file_sha256( self, fnamelst ):
    #    return [(fname, hashlib.sha256(open(fname, 'rb').read()).digest()) for fname in fnamelst]

    def add_song_to_store( self, root, filename ):
        # get tags, add to artist and album store if needed
        full_path = os.path.join( root, filename )
        file_tags = {}
        
        self.song_store.append([
            "", # blank playing field
            full_path, # full path
            "01", # track number
            filename, # song title
            "artist",
            "album",
            "year",
            "3:42"
        ])

    def find_songs( self ):
        # parse through every directory listed in the library
        for directory in self.directories:
            # parse through all sub-folders looking for audio audio files
            for r,d,f in os.walk( directory ):
                for filename in f:
                    mime = mimetypes.guess_type( filename )
                    # make sure mime-type is not None, otherwise the match will throw an error on some files
                    if not mime[0] == None and re.match( "^audio", mime[0] ):
                        # it's an audio file, add it to the library even though we're not sure gstreamer can play it
                        self.add_song_to_store( r, filename )

    def get_image( self, icon ):
        image = Gtk.Image()
        image.set_from_stock( icon, Gtk.IconSize.BUTTON )
        return image

    def play_pause( self, widget ):
        if self.playing == False:
            #filepath = self.entry.get_text()
            #if os.path.isfile(filepath):
            self.playing = True
            self.button_stop.set_sensitive( True )
            image = self.get_image( Gtk.STOCK_MEDIA_PAUSE )
            #self.player.set_property("uri", "file://" + filepath)
            #self.player.set_state(gst.STATE_PLAYING)
        else:
            self.playing = False
            image = self.get_image( Gtk.STOCK_MEDIA_PLAY )
        self.button_play.set_image( image )

    def do_stop( self, w ):
        self.button_play.set_image( self.get_image( Gtk.STOCK_MEDIA_PLAY ) )
        #self.player.set_state(gst.STATE_NULL)
        self.playing = False
        self.button_stop.set_sensitive( False )

pympin = Pympin()
pympin.connect( "delete-event", Gtk.main_quit )
pympin.show_all()
Gtk.main()
