#coding:utf-8
###########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
##########################################################################
"""
This module provides config file reade and check for mini_spider .

Authors: yuexiangrui01(yuexiangrui01@baidu.com)
Date:    2014/11/05 13:25:30
"""

import ConfigParser
import logger
import re
import os

class ConfigReader(object):
	"""
	A class load and read config file.
	"""
	def __init__(self, file):
		self.option_list = [
                'url_list_file',
                'output_directory', 
                'max_depth',
                'crawl_interval', 
                'crawl_timeout', 
                'target_url', 
                'thread_count']
		self.config_file = file
		self.conf = ConfigParser.ConfigParser()  


	def readConf(self):
		"""
		read config file
		return: a dict of all config iterms
		"""
		try:
			#读取配置文件
			self.conf.read(self.config_file)
		except ConfigParser.Error as error:
			logger.error("Read config_file error.\n%s" % str(error))
			return None
		
		try:
            #获取每一项
			section = self.conf.sections() 
			item_dict = dict(self.conf.items(section[0]))
		except ConfigParser.Error as error:
			logger.error("Read config_file error. \n%s" % str(error))
			return None    

        #检查配置文件的项是否全面
		for option in self.option_list:
			if option not in item_dict:
				logger.error("Config file is lack of option: %s " % str(option))
				return None
        

        #检查种子文件是否存在
		if not os.path.isfile(item_dict["url_list_file"]):
			logger.error("Cant find the url_list_file in %s" % str(item_dict["url_list_file"]))
			return None

		#检查输出目录是否有效
		if not os.path.exists(item_dict["output_directory"]):
			logger.error("The output_directory %s is not exits!" % str(item_dict["output_directory"]))
			return None

		
		try:
			#检查每个参数是否合法
			item_dict["max_depth"] = int(item_dict["max_depth"])
			item_dict["crawl_interval"] = int(item_dict["crawl_interval"])
			item_dict["crawl_timeout"] = int(item_dict["crawl_timeout"])
			item_dict["thread_count"] = int(item_dict["thread_count"])
			if item_dict["max_depth"] < 1 or item_dict["crawl_interval"] < 1 or \
					item_dict["crawl_timeout"] <1 or item_dict["thread_count"] < 1 :
				logger.error("The items of the config are illegal." )
				return None
		except ValueError as error:
			logger.error("Some items of the config are illegal. \n%s" % str(error))


		try:
			#print item_dict['target_url']
			item_dict['target_url'] = re.compile(item_dict['target_url'])
		except re.error as error:
			logger.error('The target url of the config is illegal. \n%s' % str(error))
			return None

	
		return item_dict
            
