#!/usr/bin/env python

import sys, os, re, glib, gi, time
gi.require_version( "Gst", "1.0" )
from gi.repository import GObject, Gdk, Gtk, Gst, Pango
from gmusicapi import Webclient
#from mutagen.mp3 import MP3
#from mutagen.easyid3 import EasyID3

class Pygmy( Gtk.Window ):
    #directories = [
        #"/home/kevin/player/songs"# ,
        # "/mnt/stuff/tunez"
    #]

    artist_dictionary = {}

    def __init__( self ):
        Gtk.Window.__init__( self, title = "pygmy" )

        # set default window size
        self.set_default_size( 800, 400 )

        # initialize gobject threads
        GObject.threads_init()

        # initialize glib threads
        # glib.threads_init()

        # initialize gstreamer
        Gst.init( None )

        # need to switch from webclient eventually, because it's being deprecated
        # i don't think mobileclient works because of the android id thing
        self.api = Webclient()

        self.player = Gst.ElementFactory.make( "playbin", None )

        #self.bus = self.player.get_bus()
        #self.bus.connect("message", self.on_message)

        self.playing = False

        self.artist_store = Gtk.ListStore( str )

        self.artist_sorted = Gtk.TreeModelSort( model = self.artist_store )

        self.album_store = Gtk.ListStore( str )

        self.album_sorted = Gtk.TreeModelSort( model = self.album_store )

        # full file path, track #, title, artist, album, year, time
        self.song_store = Gtk.ListStore( str, str, int, str, str, str, str, str )

        self.song_sorted = Gtk.TreeModelSort( model = self.song_store )

        # self.album_store.append(["test"])

        self.build_login()

    def on_message( self, bus, message ):
        t = message.type
        print(message)
        if t == Gst.Message.EOS:
            self.player.set_state(Gst.State.NULL)
            self.playing = False
        elif t == Gst.Message.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            #print "Error: %s" % err, debug
            self.playing = False

    def build_login( self ):
        self.login_box = Gtk.Grid()

        self.login_box.set_halign( Gtk.Align.CENTER )
        self.login_box.set_valign( Gtk.Align.CENTER )

        login_label = Gtk.Label( label = "Login to Google Play" )

        self.entry_username = Gtk.Entry()
        self.entry_username.set_placeholder_text( "User" )

        self.entry_password = Gtk.Entry()
        self.entry_password.set_visibility( False )
        self.entry_password.set_placeholder_text( "Password" )

        login_button = Gtk.Button( label = "Login" )
        login_button.connect( "clicked", self.do_login )

        self.login_box.add( login_label )
        self.login_box.attach_next_to( self.entry_username, login_label, Gtk.PositionType.BOTTOM, 1, 1 )
        self.login_box.attach_next_to( self.entry_password, self.entry_username, Gtk.PositionType.BOTTOM, 1, 1 )
        self.login_box.attach_next_to( login_button, self.entry_password, Gtk.PositionType.BOTTOM, 1, 1 )

        self.add( self.login_box )

    def do_login( self, widget ):
        # add a loading bar up here
        if self.api.login( self.entry_username.get_text(), self.entry_password.get_text() ):
            self.login_box.destroy()
            self.build_ui()
        else:
            print( "Authentication with Google failed" )

    def build_ui( self ):
        grid = Gtk.Grid()
        self.add( grid )

        # toolbar stuff
        #fixed = Gtk.Fixed()
        # fixed.set_size_request( -1, 38 )
        toolbar_parent = Gtk.VBox()

        toolbar = Gtk.HBox()
        toolbar_parent.pack_start( toolbar, True, True, 3 )
        #fixed.add( toolbar )

        # previous button
        self.button_previous = Gtk.Button()
        self.button_previous.set_image( self.get_image( icon = Gtk.STOCK_MEDIA_PREVIOUS ) )
        #self.button_previous.connect("clicked", self.on_button_previous_clicked)
        toolbar.pack_start( self.button_previous, False, False, 1 )

        # play/pause button
        self.button_play = Gtk.Button()
        self.button_play.set_image( self.get_image( icon = Gtk.STOCK_MEDIA_PLAY ) )
        self.button_play.connect( "clicked", self.play_pause )
        toolbar.pack_start( self.button_play, False, False, 1 )

        # stop button
        self.button_stop = Gtk.Button()
        self.button_stop.set_sensitive( False )
        self.button_stop.set_image( self.get_image( icon = Gtk.STOCK_MEDIA_STOP ) )
        self.button_stop.connect( "clicked", self.do_stop )
        toolbar.pack_start( self.button_stop, False, False, 1 )

        # next button
        self.button_next = Gtk.Button()
        self.button_next.set_image( self.get_image( icon = Gtk.STOCK_MEDIA_NEXT ) )
        #self.button_next.connect("clicked", self.on_button_play_clicked)
        toolbar.pack_start( self.button_next, False, False, 1 )

        #box.pack_start(fixed, True, True, 0)

        # add the fixed button bar to the grid
        grid.add( toolbar_parent )

        # browser stuff
        browser = Gtk.VPaned()
        #browser_paned = Gtk.VPaned()
        #browser.add(browser_paned)
        grid.attach_next_to( browser, toolbar_parent, Gtk.PositionType.BOTTOM, 1, 1 )

        # create columns for artist/album filters
        columns = Gtk.HBox()
        columns.set_size_request( 0, 150 )

        # define cell renderer
        cell_renderer = Gtk.CellRendererText()

        # add ellipsis with pango
        cell_renderer.props.ellipsize = Pango.EllipsizeMode.END

        # artist list
        artists_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.artists = Gtk.TreeView( self.artist_sorted )
        artist_column = Gtk.TreeViewColumn( "Artist", cell_renderer, text = 0 )
        self.artists.append_column( artist_column )
        self.artists.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )
        self.artist_sorted.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        artists_scroll.add( self.artists )

        #album list
        albums_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.albums = Gtk.TreeView( self.album_sorted )
        album_column = Gtk.TreeViewColumn( "Album", cell_renderer, text = 0 )
        self.albums.append_column( album_column )
        self.albums.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )
        self.album_sorted.set_sort_column_id( 0, Gtk.SortType.ASCENDING )
        albums_scroll.add( self.albums )

        # add items to the columns
        columns.pack_start( artists_scroll, False, True, 0 )
        columns.pack_start( albums_scroll, False, True, 0 )
        #columns.add(self.artists)

        # song list
        songs_scroll = Gtk.ScrolledWindow( hexpand = True, vexpand = True )
        self.songs = Gtk.TreeView( self.song_sorted )

        self.songs.get_selection().set_mode( Gtk.SelectionMode.MULTIPLE )

        self.songs.connect( "row-activated", self.on_song_activate )

        songs_columns = {
            "playing": Gtk.TreeViewColumn(
                title = "",
                cell_renderer = cell_renderer,
                text = 0
            ),
            "track": Gtk.TreeViewColumn(
                title = "#",
                cell_renderer = cell_renderer,
                text = 2
            ),
            "title": Gtk.TreeViewColumn(
                title = "Title",
                cell_renderer = cell_renderer,
                text = 3
            ),
            "artist": Gtk.TreeViewColumn(
                title = "Artist",
                cell_renderer = cell_renderer,
                text = 4
            ),
            "album": Gtk.TreeViewColumn(
                title = "Album",
                cell_renderer = cell_renderer,
                text = 5
            ),
            "year": Gtk.TreeViewColumn(
                title = "Year",
                cell_renderer = cell_renderer,
                text = 6
            ),
            "time": Gtk.TreeViewColumn(
                title = "Time",
                cell_renderer = cell_renderer,
                text = 7
            )
        }

        # set all columns except playing as resizable
        for column in songs_columns:
            if column != "playing":
                songs_columns[column].set_sizing( Gtk.TreeViewColumnSizing.AUTOSIZE )
                songs_columns[column].set_resizable( True )
                songs_columns[column].set_reorderable( True )

        # songs_columns[ "track" ].set_sort_column_id( 2 )
        songs_columns[ "title" ].set_sort_column_id( 3 )
        songs_columns[ "artist" ].set_sort_column_id( 4 )
        songs_columns[ "album" ].set_sort_column_id( 5 )
        songs_columns[ "year" ].set_sort_column_id( 6 )
        songs_columns[ "time" ].set_sort_column_id( 7 )

        self.song_sorted.set_sort_column_id( 4, Gtk.SortType.ASCENDING )

        # self.song_sorted.set_sort_func( 2, self.compare, None )

        # set title, artist, and album to expand
        #songs_columns[ "title" ].set_expand( True )
        #songs_columns[ "artist" ].set_expand( True )
        #songs_columns[ "album" ].set_expand( True )

        # make sure we add them in the proper order
        self.songs.append_column( songs_columns[ "playing" ] )
        self.songs.append_column( songs_columns[ "track" ] )
        self.songs.append_column( songs_columns[ "title" ] )
        self.songs.append_column( songs_columns[ "artist" ] )
        self.songs.append_column( songs_columns[ "album" ] )
        self.songs.append_column( songs_columns[ "year" ] )
        self.songs.append_column( songs_columns[ "time" ] )

        songs_scroll.add( self.songs )

        # put together the browser window
        browser.add( columns )
        browser.add( songs_scroll )

        self.find_songs()

    # demo comparison for sorting treemodelsorted
    def compare( self, model, row1, row2, user_data ):
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        if value1 < value2:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1

    def on_song_activate( self, widget, path, col ):
        # set the player state to null
        self.player.set_state( Gst.State.NULL )
        # set the player uri to the activated song url
        # HEYYYYYY
        self.player.set_property( "uri", self.api.get_stream_urls( self.song_store[ path ][ 1 ] )[ 0 ] )
        # set the player state to playing
        self.player.set_state( Gst.State.PLAYING )

    def add_artist_to_store( self, artist ):
        if not artist in self.artist_dictionary:
            self.artist_dictionary[ artist ] = 0
            
        self.artist_dictionary[ artist ] += 1

    def add_song_to_store( self, track ):
        this_artist = track[ "artist" ] if not track[ "artist" ] == "" else "Unknown"

        self.add_artist_to_store( this_artist )

        # format the time to minutes:seconds and remove the leading 0
        time_string = re.sub(
            "^0", "",
            time.strftime( "%H:%M:%S", time.gmtime( int( track[ "durationMillis" ] ) / 1000 ) )
        )

        self.song_store.append([
            "",
            track["id"],
            track["track"],
            track["title"] if not track[ "title" ] == "" else "Unknown",
            this_artist,
            track["album"] if not track[ "album" ] == "" else "Unknown",
            str( track[ "year" ] if not track[ "year" ] == 0 else "" ),
            str( time_string )
        ])

    def find_songs( self ):
        if not self.api.is_authenticated() == True:
            return

        self.library = self.api.get_all_songs()

        for track in self.library:
            self.add_song_to_store( track )

        for artist in self.artist_dictionary:
            self.artist_store.append([
                artist + " (" + str( self.artist_dictionary[ artist ] ) + ")"
            ])

        self.artist_store.append([
            "All " + str( len( self.artist_dictionary ) ) + " artists (" + str( len( self.song_store ) ) + ")"
        ])

        self.show_all()

        # parse through every directory listed in the library
        #for directory in self.directories:
            # parse through all sub-folders looking for audio audio files
            #for r,d,f in os.walk( directory ):
                #for filename in f:
                    # mime = mimetypes.guess_type( filename )
                    #mime = magic.from_file( os.path.join( r, filename ), mime = True )
                    #print(mime)
                    # make sure mime-type is not None, otherwise the match will throw an error on some files
                    #if not mime == None:
                        #match = re.match( "^audio", mime )
                        #if match:
                            # it's an audio file, add it to the library even though we're not sure gstreamer can play it
                            #self.add_song_to_store( r, filename )

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

pygmy = Pygmy()
pygmy.connect( "delete-event", Gtk.main_quit )
pygmy.show_all()
Gtk.main()
