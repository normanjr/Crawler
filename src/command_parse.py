#coding:utf-8
###########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
##########################################################################
"""
This module provides command parsing for mini_spider .

Authors: yuexiangrui01(yuexiangrui01@baidu.com)
Date:    2014/11/05 13:25:30
"""

import argparse
import logger
import os


class CommandParse(object):
	"""
	A class parsing command args.
	"""
	def __init__(self):
		"""
		Set the info of help!
		"""
		self.SPIDER_VERSION = "MINI_SPIDER version : 1.0.0.0"
		self.ERROR_NONE_CONF = "Config file is requered!\
				Please specify the path of the config file!"
		self.ERROR_ERROR_CONF = "Can't find the config file!"
	
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument("-v", "--version ", help="show this \
				spider\'s version.", action="store_true", dest="show_ver")
		self.parser.add_argument("-c", "--conf", metavar="conf_file", \
				help="specify the path of the config file", dest="get_conf", default="../conf/spider.conf")


	def parse(self):
		"""
		Parse the args and get config file.
		"""
		args = self.parser.parse_args()
		
		#打印版本号
		if args.show_ver:
			print self.SPIDER_VERSION
			return "version"
		#没有conf参数的时候提示
		elif args.get_conf is None:
			print self.ERROR_NONE_CONF
			logger.error(self.ERROR_NONE_CONF)
			return None
		#找不到conf文件
		elif not os.path.isfile(args.get_conf):
			print self.ERROR_ERROR_CONF
			logger.error(self.ERROR_ERROR_CONF)
			return None
		else:
			return args.get_conf
		


