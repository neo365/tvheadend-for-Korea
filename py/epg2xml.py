#!/usr/bin/python
# -*- coding: utf-8 -*-

#version 0.7.201608011410

import os
import sys
import urllib
import json
import datetime
import time
import codecs
import socket
import re
from xml.etree.ElementTree import Element, SubElement, dump
from xml.sax.saxutils import escape
import argparse

default_broadcast='all'
default_xml_filename='epg.xml'
default_xml_socket='xmltv.sock'

def getXml(ips='ALL'):
	url = ('http://epg.neo365.net/XMLTV/%s' % ( ips ) )
	response = urllib.urlopen(url)
	return response.read()

def writeXML(contents):
	if args.socket:
		xmlfp.send(contents.encode('utf-8'))
	else:
		xmlfp.write(contents)
		xmlfp.close()

parser = argparse.ArgumentParser()
cmds = parser.add_mutually_exclusive_group(required=True)
cmds.add_argument('-w', dest='outputfile', metavar=default_xml_filename, nargs='?', const=default_xml_filename, help=u'저장할 파일이름')
cmds.add_argument('-s', dest='socket', metavar=default_xml_socket, nargs='?', const=default_xml_socket, help=u'xmltv.sock(External: XMLTV)로 EPG정보 전송')
opts = parser.add_argument_group(u'추가옵션')
opts.add_argument('-i', dest='ips', help=u'사용하는 망 : SK, KT, LG, ALL', default='ALL')

args = parser.parse_args()


global xmlfp

if args.socket:
	xmlfp = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	xmlfp.connect(args.socket)
elif args.outputfile:
	xmlfp = open(args.outputfile, "w")
else:
	xmlfp = sys.stdout

html = getXml(args.ips)
writeXML(getXml(args.ips))
