import os
import sys
import signal
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from time import sleep



def timeout_handler(signum, frame):
	raise Exception("Timeout")

run_time = 10

# ---------------------------------------------------
# ---- change localhost in url to server address ----
# ---------------------------------------------------
#          |
#          v
# url = 'http://localhost/' + 'myindex_' + abr_algo + '.html'

url = 'http://10.0.0.1:8000/index.html'

# timeout signal
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(run_time + 30)
	
try:
	# copy over the chrome user dir
	chrome_user_dir = '/tmp/chrome_user_dir_real_exp'
	os.system('rm -r ' + chrome_user_dir)
	os.system('mkdir ' + chrome_user_dir)
	
	## proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	sleep(2)
	
	# to not display the page in browser
	display = Display(visible=1, size=(800,600))
	display.start()
	
	# initialize chrome driver
	options=Options()
	chrome_driver = '/home/wifi/Downloads/chromedriver'
	options.add_argument('--user-data-dir=' + chrome_user_dir)
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument('--ignore-certificate-errors')
	driver=webdriver.Chrome(chrome_driver, chrome_options=options)
	
	# run chrome
	driver.set_page_load_timeout(10)
	driver.get(url)
	
	sleep(run_time)
	
	driver.quit()
	display.stop()
	
	proc.send_signal(signal.SIGINT)
	# proc.kill()
	
	print 'done'
	
except Exception as e:
	try: 
		display.stop()
	except:
		pass
	try:
		driver.quit()
	except:
		pass
	try:
		proc.send_signal(signal.SIGINT)
	except:
		pass
	
	print e	

