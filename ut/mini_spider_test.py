#coding:utf-8
###########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
##########################################################################
"""
This module provides unit test for mini_spider.

Authors: yuexiangrui01(yuexiangrui01@baidu.com)
Date:    2014/12/05 13:25:30
"""
import unittest
import urllib
import os
import sys
import shutil
import re
sys.path.append('../src')
import config_reader
import html_crawler


class ConfigReaderTest(unittest.TestCase):
	"""
	A class for tesing config_reader
	"""
	def setUp(self):
		self.conf = config_reader.ConfigReader("../conf/spider.conf")
		
	def tearDown(self):
		pass

	def testparam(self):
		conf_dic = self.conf.readConf()
		self.assertEqual(conf_dic["url_list_file"], "../conf/urls")
		self.assertEqual(conf_dic["output_directory"], "../output")
		self.assertEqual(conf_dic["max_depth"],5)
		self.assertEqual(conf_dic["thread_count"], 8)
		CONF = conf_dic


class OnePageParserTest(unittest.TestCase):
	"""
	A class for testing onepageParser. 
	"""
	def setUp(self):
		self.parser = html_crawler.OnePageParser()
	
	def tearDown(self):
		pass
	
	def testparse(self):
		url = "http://pycm.baidu.com:8081/"
		content = urllib.urlopen(url).read()
		self.parser.feed(content)
		self.assertEqual(len(self.parser.href_list), 5)
	
	def testwrongparse(self):
		url = "http://pycm.baidu.com:8081/1/"
		content = urllib.urlopen(url).read() 
		self.parser.feed(content)  
		self.assertEqual(len(self.parser.href_list),3)

class MultiCrawlerThreadTest(unittest.TestCase):
	"""
	A class for testing MultiCrawlerThread.
	"""
	def setUp(self):
		self.conf = config_reader.ConfigReader("../conf/spider.conf").readConf()
		self.url_list = ["http://pycm.baidu.com:8081/"]
		self.wrong_url_list = ["http://pycm.baidu.com:8081/1/page1_4"]
		self.thread_id = 12
		self.tmp_dir = "../tmp"
		os.makedirs(self.tmp_dir)
	
	def tearDown(self):
		shutil.rmtree("../tmp")

	def testcrawl_normal(self):
		crawler = html_crawler.MultiCrawlerThread(self.conf, self.url_list, self.thread_id, self.tmp_dir)
		crawler.run()
		file_list = os.listdir("../tmp")
		self.assertTrue(file_list is not None)
		file_content = open("../tmp/12.next","r").read()
		self.assertTrue(file_content is not None)

	def testcrawl_wrong(self):
		crawler = html_crawler.MultiCrawlerThread(self.conf, self.wrong_url_list, self.thread_id, self.tmp_dir)
		file_list = os.listdir("../tmp")
		self.assertTrue(file_list is not None)


if __name__ == '__main__':
	unittest.main()
