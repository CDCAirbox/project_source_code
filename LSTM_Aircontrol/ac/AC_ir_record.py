'''
import os
#import commands
import subprocess
ri
subprocess.run(["mode2", "-m -d", "/dev/lirc1"], capture_output=True)
'''

import io
import sys
import os
import subprocess

while True:


	first_space = True
	n = 0
	pulse = False
	space = False
	f = open("../../../../etc/lirc/lircd.conf.d/tv2.lircd.conf","w")
	f.write("begin remote\n")
	f.write("  name  tv2\n")
	f.write("  flags RAW_CODES\n")
	f.write("  eps            30\n")
	f.write("  aeps          100\n")
	f.write("\n")
	f.write("  gap          132350\n")
	f.write("\n")
	f.write("      begin raw_codes\n")
	f.write("\n")
	f.write("          name KEY_POWER\n")
	for line in os.popen('timeout 5s mode2 -m -d /dev/lirc1').read().split('\n'):
		words = line.split()
		if len(words) < 2:
			continue
		for w in words:
			if "pulse" in w :
				pulse = True
			if "space" in w :
				space = True
		if pulse == False and space == False :
			f.write(line)
			f.write('\n')
			print(line)         
		else :
			for w in words:
				if "pulse" not in w and "space" not in w:
					f.write(w)
					f.write('\n')
					print(w)
		pulse = False
		space = False
	f.write("\n")
	f.write("      end raw_codes")
	f.write("\n")
	f.write("end remote ")
	print()
	print()
	f.close()
	break


subprocess.call('sudo service lircd restart', shell=True)
