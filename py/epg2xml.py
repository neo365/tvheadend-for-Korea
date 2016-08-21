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

def channelList(ips='ALL'):
	global channels
	ch_channels=[]

	url = ('http://epg.neo365.net/Api/EPG/ChannelList/%s' % ( ips ) )
	u = urllib.urlopen(url)
	data = u.read()
	j = json.loads(data)

	channels = j["Channels"]
	
	for channel in channels:
		ch_Id = channel["ChannelId"]
		ch_name = channel["Name"]
		ch_channelNo = channel["ChannelNo"]
		ch_channelName = channel["ChannelName"]	

		ch_channels.append('\t<channel id="%s">\n' % ( ch_Id))
		ch_channels.append('\t\t<display-name>%s</display-name>\n' % ( escape(ch_name)) )

		if ch_name != ch_channelName:
			ch_channels.append('\t\t<display-name>%s</display-name>\n' % ( escape(ch_channelName)) )

		ch_channels.append('\t\t<display-name>[%s] %s</display-name>\n' % (ch_channelNo, escape(ch_channelName)) )
		ch_channels.append('\t\t<icon src="http://epg.neo365.net/Images/Channels/%s.png"/>\n' % (ch_Id) )
		ch_channels.append('\t</channel>\n')

	for channel in channels:
		for prog in channelDetail(channel["ChannelId"]):
			ch_channels.append(prog)
			
	return ch_channels

def channelDetail(channelId):
	global channel
	prog=[]
	url = ('http://epg.neo365.net/Api/EPG/channel/%s' % ( channelId ))
	u = urllib.urlopen(url)
	data = u.read()
	j = json.loads(data)
	channel = j["Channel"]
	
	for program in channel["Programs"]:
		pr_programName = program["ProgramName"]
		pr_title = program["Title"]
		pr_mainTitle = program["MainTitle"]
		pr_subTitle = program["SubTitle"]
		#pr_episode = program["Episod"]
		pr_episode = program["EPGEpisod"]
		pr_startTime = ("%s +0900" % ( program["EPGStart"]) )
		pr_endTime = ("%s +0900" % ( program["EPGEnd"]) )
		pr_genre = program["Genre"]
		pr_actor = program["Actor"]
		pr_director = program["Director"]
		pr_description = program["Description"]
		pr_extenddescription = program["ExtendDescription"]
		pr_ratingCd = program["Rating"]
		pr_extrainfo = program["ExtraInfo"]

		
		if isinstance(pr_programName, unicode):
			pr_programName = escape(pr_programName)	
		if isinstance(pr_title, unicode):
			pr_mainTitle = escape(pr_title)		
		if isinstance(pr_mainTitle, unicode):
			pr_mainTitle = escape(pr_mainTitle)
		if isinstance(pr_subTitle, unicode):
			pr_subTitle = escape(pr_subTitle)
		if isinstance(pr_genre, unicode):
			pr_genre = escape(pr_genre)	
		if isinstance(pr_extrainfo, unicode):
			pr_extrainfo = escape(pr_extrainfo)	

		prog.append('\t<programme start="%s" stop="%s" channel="%s">\n' % ( pr_startTime, pr_endTime ,channelId))

		#prog.append('\t\t<title lang="kr">%s</title>\n' %(stripString(pr_programName)))
		#prog.append('\t\t<title lang="kr">%s</title>\n' %(stripString(pr_title)))

		prog.append('\t\t<title lang="kr">%s' %(stripString(pr_title)))
		if pr_extrainfo:
			prog.append('(%s)' %(stripString(pr_extrainfo)))

		prog.append('</title>\n')

		#prog.append('\t\t<title lang="kr">%s</title>\n' %(stripString(pr_mainTitle)))
		#if pr_subTitle:
		#	prog.append('\t\t<sub-title lang="kr">%s</sub-title>\n' %(stripString(pr_subTitle)))

		#prog.append('\t\t<desc lang="kr">%s</desc>\n' %(stripString(pr_description)))
		prog.append('\t\t<desc lang="kr">%s</desc>\n' %(stripString(pr_extenddescription)))
		
		if pr_genre:
			prog.append('\t\t<category lang="ko">%s</category>\n' %(pr_genre))
		
		if pr_episode:
			prog.append('\t\t<episode-num system="xmltv_ns">.%s.</episode-num>\n' % pr_episode)

		if pr_ratingCd > '0':
			prog.append('\t\t<rating system="VCHIP">\n\t\t\t<value>%s</value>\n\t\t</rating>\n' % pr_ratingCd)
			
		prog.append('\t</programme>\n')
	return prog

def stripString(str):
	return str.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def writeXML(data):
	if args.socket:
		xmlfp.send(data.encode('utf-8'))
	else:
		xmlfp.write(data)

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
	xmlfp = codecs.open(args.outputfile, "w+", encoding="utf8")
else:
	xmlfp = sys.stdout

channels = []
channels = channelList(args.ips)

writeXML('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
writeXML('<tv source-info-url="epg.neo365.net" source-info-name="epgi" generator-info-name="epgMaker">\n')

for channel in channels:
	writeXML(channel)

writeXML('</tv>\n')
