#!/usr/bin/env python

#import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
	packages = [
		"gi",
		"pkg_resources",
		"gmusicapi"
	],
	include_files = [
		"cacert.pem"
	],
	excludes = []
)

executables = [
    Executable("pympin.py" )
]

setup(
	name='pympin',
    version = '0.1',
    description = 'a google play music library utilizing gtk3, and gstreamer1.0',
    options = dict( build_exe = buildOptions ),
    executables = executables
)
