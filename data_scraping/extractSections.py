import os


def test():
	path = "SEC-Edgar-data"
	targetPaths = []
	for subdir, dirs, files in os.walk(path):
		for f in files:
			if 'embedding' not in f:
				docPath = os.path.join(subdir, f)
				targetPaths.append(docPath)

	totalPaths = len(targetPaths)
	for targetPath in targetPaths:
		f = open(targetPath, 'r')
		lines = f.readlines()
		f.close()
		print lines[:20]
		break

if __name__ == '__main__':
	test()