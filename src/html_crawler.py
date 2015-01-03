#coding:utf-8
###########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
##########################################################################
"""
This module provides html crawler for mini_spider .

Authors: yuexiangrui01(yuexiangrui01@baidu.com)
Date:    2014/12/15 13:25:30
"""
import HTMLParser
import os
import re
import threading
import time
import socket
import urllib
import chardet
import logger
import utils
import math
	
class OnePageParser(HTMLParser.HTMLParser):
	"""
	Paeser the urls of one page.
	"""
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.script_flag = False
		self.href_list = []

	def handle_starttag(self, tag, attrs):
		if tag == "a":
			for name, value in attrs:
				if name == "href":
					#去除空格
					if value.replace(" ", "").startswith("javascript:location.href="):
						value = value[len('javascript:location.href='):]
						value = value.replace('"',"")
					self.href_list.append(value)
		
		elif tag == "image":
			for name, value in attrs:
				#获取image的url
				if name == 'src':
					self.href_list.append(value)

		elif tag == "script":
			#对script需要单独处理
			self.script_flag = True
	
	def handle_data(self, data):
		"""
		Handle the script for href_list.
		"""
		if self.script_flag is True:
			lines = data.split(';')
			for line in lines:
				line = line.replace(" ", "")
				href_value = utils.get_str_between_s_and_e("document.\
						write('<a href=", ">", line)
				if href_value is not None:
					self.href_list.append(href_value)
				href_value = utils.get_str_between_s_and_e("setAttribute\
						('href','", "')", line)
				if href_value is not None:
					self.href_list.append(href_value)

	def handle_endtag(self, tag):
		if tag == "script" and self.script_flag is True:
			self.script_flag = False


class MultiCrawlerThread(threading.Thread):
	"""
	The thread class for multi-thread crawling.
		url_list : the url list this thread gone crawl.
		conf_dict: conf_dict of all conf.
		url_pattern: the re to show which kind of url should be get.
		thread_id: the num of this thread to sefecify the file for next urls.
		tmp_dir: the dir for tmp files of next urls.
	"""
	def __init__(self, conf, url_list, thread_id, tmp_dir):
		threading.Thread.__init__(self)
		self.url_list = url_list
		self.conf_dict = conf
		self.url_pattern = self.conf_dict["target_url"]
		self.thread_id = thread_id
		self.tmp_dir = tmp_dir

	def stop_in_crawl_interval(self):
		"""
		Set the crawl interval in the processing.
		"""
		interval = self.conf_dict["crawl_interval"]
		time.sleep(interval) 

	def parse_the_next(self, content, url):
		"""
		Get the next level url and put into the wait_queue.
		input: content, url
		output: next_level url list
		"""
		out_url_list = []
		try:
			parser = OnePageParser()
			parser.feed(content)
			for i in range(len(parser.href_list)):
				tmp_href = parser.href_list[i]
				real_url = utils.joint_url(url, tmp_href)
				#把解析出来的url放到list中
				out_url_list.append(real_url)
		except HTMLParser.HTMLParseError as error:
			logger.error("Parsing url: %s failed. Details: %s " % (url, error))
			return None
		return out_url_list

	def run(self):
		"""
		The thread function crawling html data and save into files.
		"""
		#创建一个文件，记录问线程提取的urllist
		filename = os.path.join(self.tmp_dir, "%d.next" % self.thread_id)
		next_level_file = open(filename, "w+")

		for url in self.url_list:
			#获取url的html
			content = utils.http_request(url)
			if content is None:
				logger.error("Get this url failed : %s "% url)
				continue
			
			#转码
			try:
				coding = chardet.detect(content)['encoding']
				content = content.decode(coding).encode('utf8')
			except UnicodeError as error:
				logger.error("Decoding this url's content failed: %s. Error detail is %s" % (url, error))
				continue

			#解析页面中的下一层的url
			next_url_list = self.parse_the_next(content, url)
			if next_url_list is not None:
				#写到文件里，用线程名来命名
				for next_url in next_url_list:
					next_level_file.write(next_url + '\n')				

			#检查url是否符合正则,符合就保存下来
			match = self.url_pattern.match(url)
			if self.url_pattern.match(url) is not None and content is not None:
				file_name = urllib.quote(url, '')
				file_path = os.path.join(self.conf_dict["output_directory"], file_name)
				file = open(file_path, "w+")
				file.write(content)

			#按照配置的暂停间隔暂停一段时间,j控制抓取时间
			self.stop_in_crawl_interval()
	

class Crawler(object):
	"""
	Processing the url.
		conf_dict: all items of config file.
		wait_list: urls which are waiting for parsing.
		parsed_set: urls which are already parsed.
		tmp_dir: tempt file dir for multi-thread write urls.
	"""
	def __init__(self, item_dict):
		self.conf_dict = item_dict
		self.wait_list = []
		self.parsed_set = set()
		self.tmp_dir = "../tmp_dir"

	def read_urls(self):
		"""
		Read all urls.
		"""
		try:
			urls = open(self.conf_dict["url_list_file"],'r') 
			for line in urls:
				self.wait_list.append(line.strip()) 
				#self.append_new_urls(line.strip(), 0)
		except IOError as error:
			logger.error("The url_list_file:" + str(self.conf_dict["url_list_file"]) + \
				"read IOError: %s" % str(error))


	def updata_new_urls(self):
		"""
		Add the new and unprocessing urls into the self.wait_list.
		"""	
		next_url_set = set()
		#从每个线程写的文件里提取出来需要抓取的url
		for file in os.listdir(self.tmp_dir):
			full_path = os.path.join(self.tmp_dir, file)
			if os.path.isfile(full_path) and file.endswith('next'):
				fhandle = open(full_path, "r")
				next_url_set.update([line.strip() for line in fhandle])
				#处理过的文件就删除掉
				os.remove(full_path)

		#去掉已经抓取过的url
		out_url_list = list(next_url_set - self.parsed_set)
		return out_url_list

	def crawling(self, url_list):
		"""
		Crawler the url_list and use multi-thread.
		input: url_list
		"""
		#获取线程数
		thread_num = self.conf_dict["thread_count"]

		#num是每个线程处理的url的数目
		num = int(math.ceil(float(len(url_list)) / thread_num))

		#把url_list切分成多份，分给不同的线程
		thread_url_list = []
		for i in range(0, len(url_list), num):
			thread_url_list.append(url_list[i:i+num])

		#开始多线程执行
		thread_list = []
		thread_id = 0 
		for one_url_list in thread_url_list:
			crawling_thread = MultiCrawlerThread(self.conf_dict, one_url_list, thread_id, self.tmp_dir)
			crawling_thread.start()
			thread_id += 1
			thread_list.append(crawling_thread)

		#等待全部结束
		for thread in thread_list:
			thread.join()

	def start(self):
		"""
		The root thread function.
		"""
		#先读取所有的url
		self.read_urls()

		#设置超时
		socket.setdefaulttimeout(self.conf_dict["crawl_timeout"])

		#创建一个临时目录保存过程文件
		if not os.path.isdir(self.tmp_dir):
			os.makedirs(self.tmp_dir)

		#按照顺序获取文件里的urls
		max_depth = self.conf_dict["max_depth"]
		for depth in range(max_depth+1):
			#开启主进程抓取数据
			self.crawling(self.wait_list)
			#wait_list里面的url处理完，就放到parsed_set里面
			self.parsed_set.update(self.wait_list)
			#更新等待抓取的list
			self.wait_list = self.updata_new_urls()

		#清理环境，删除临时文件
		utils.rm_all_dirs(self.tmp_dir)
