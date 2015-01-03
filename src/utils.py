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
import urlparse
import posixpath
import urllib
import logger
import os
import shutil

RETRY_TIME = 3

def http_request(url):
	'''
	http request retry when IOError happan.
	'''
	for i in range(RETRY_TIME+1):
		try:
			resp = urllib.urlopen(url)
			if resp.getcode() == 200:
				result = resp.read()
				return result
		except IOError:
			continue
	logger.error('http request socket timeout', url)
	return None

def joint_url(url, href):
    """
    Jiont the url and href to an absolute url.
    """
    if not href.startswith("http"):
        href = urlparse.urljoin(url, href)
        parse_out = urlparse.urlparse(href)
        path = posixpath.normpath(parse_out[2])
        href = urlparse.urlunparse((parse_out.scheme, parse_out.netloc, path, parse_out.params,
            parse_out.query, parse_out.fragment))
    return href


def get_str_between_s_and_e(start_str, end_str, line):
	"""
	Get the str between the start_str and end_str.
	"""
	start = line.find(start_str)
	if start >= 0:
		start = start + len(start_str)
		end = line.find(end_str, start)
		if end >= 0:
			return line[start:end].strip()
	else:
		return None
	
def rm_all_dirs(dir):
	"""
	Remove all files in the dir, and.
	"""
	file_list = os.listdir(dir)
	for f in file_list:
		try:
			file_path = os.path.join(dir, f)
			if os.path.isfile(file_path):
				os.remove(file_path)
			if os.path.isdir(file_path):
				shutil.rmtree(file_path,True)  
		except OSError as error:
			logger.error("Remove tmp_dir %s failed! Details: %s" % (f, error))

	try:
		shutil.rmtree(dir)
	except OSError as error:
		logger.error("Remove tmp_dir %s failed! Details: %s" % (dir, error))
