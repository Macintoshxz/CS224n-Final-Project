def countSections():
	path = "SEC-Edgar-data"
	sectionCount = 0
	for subdir, dirs, files in os.walk(path):
	    for f in files:
	        if 'html_section' in f:
	            sectionCount += 1
	print sectionCount

if __name__ == '__main__':
    countSections()