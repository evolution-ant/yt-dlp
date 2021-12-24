#coding=utf-8
import os
import sys
from yt_dlp.extractor import gen_extractor_classes


#yt_dlp = 'D:/BIGWORK/yt-dlp/bin/yt-dlp'
yt_dlp = '/root/yt-dlp/bin/yt-dlp'


def exec(cmd):  
    r = os.popen(cmd)  
    text = r.read()  
    r.close()  
    return text
    

def write_file(filepath, s):
    with open(filepath, 'w') as f:
    	f.write(s)
    

def test_info():
	for c in gen_extractor_classes():
		name = c.IE_NAME
		
		if '_TESTS' in dir(c):
			for i in range(len(c._TESTS)):
				url = c._TESTS[i]['url']				
				cmd = r'python %s -J --skip-download %s' %(yt_dlp, url)
				res = exec(cmd)
				write_file('info/%s_%d.txt' % (name, i), res)
				if res.startswith('{'):
					pass
				else:
					print('【failed】 【%s】 %s' %(name, url))
					print('-'*60)


def test_download():
	print('-' * 100)
	for c in gen_extractor_classes():
		name = c.IE_NAME
		
		if '_TESTS' in dir(c):
			for i in range(len(c._TESTS)):
				url = c._TESTS[i]['url']
				filepath = 'audio/%s_%d.mp3' %(name, i)
				cmd = r'python %s -f "worst" -o %s %s' %(yt_dlp, filepath, url)
				res = exec(cmd)
				if os.path.exists(filepath):
					filesize = os.path.getsize(filepath)
					if filesize>256*1024:
						pass
					else:
						print('【failed】 【%s】 %s' %(name, url))
						print('-'*60)
				else:
						print('【failed】 【%s】 *%s' %(name, url))
						print('-'*60)


if __name__=='__main__':
	if '--info' in sys.argv:
		test_info()

	if '--download' in sys.argv:
		test_download()
