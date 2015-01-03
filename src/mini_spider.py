#coding:utf-8
###########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
###########################################################################

"""
This file provide mini_spider main function .

Authors: yuexiangrui01(yuexiangrui01@baidu.com)
Date:    2014/11/05 11:38:09
"""
import command_parse
import config_reader
import html_crawler
import logger
import sys


if __name__ == "__main__":
	"""
	This is the main of mini_spider:
	IN: 
		The config file 
	OUT: 
		htmls
	"""
	#初始化日志
	logger.log_init("../log/", 8)
	logger.info("The urls is all fininshed.")

	command = command_parse.CommandParse()
	config_file = command.parse()
	if config_file == "version":
		print "just show version!"
		sys.exit(1)
	elif config_file is None:
		sys.exit(1)   

    #读取配置文件
	config = config_reader.ConfigReader(config_file)   
	conf_dict = config.readConf()
	if conf_dict is None:
		sys.exit(1)

    #抓取内容
	crawler = html_crawler.Crawler(conf_dict)
	crawler.start()
	logger.info("The urls is all fininshed.")


