import requests
from hashlib import md5
from urllib.parse import urlsplit, urlencode, unquote_plus, quote_plus
import urllib.request
import re
import numpy as np
import PIL
from PIL import Image

headers = {"User-Agent": "Wolfram Android App"}
APPID = "3H4296-5YPAGQUJK7" # Mobile app AppId
SERVER = "api.wolframalpha.com"
SIG_SALT = "vFdeaRwBTVqdc5CL" # Mobile app salt

s = requests.Session()
s.headers.update(headers)

def calc_sig(query):
	params = list(filter(lambda x: len(x) > 1, list(map(lambda x: x.split("="), query.split("&"))))) # split string by & and = and remove empty strings
	params.sort(key = lambda x: x[0]) # sort by the key

	s = SIG_SALT
	# Concatenate query together
	for key, val in params:
		s += key + val
	s = s.encode("utf-8")
	return md5(s).hexdigest().upper()

def craft_signed_url(url):
	(scheme,	 netloc, path, query, _) = urlsplit(url)
	_query = {"appid": APPID}

	_query.update(dict(list(filter(lambda x: len(x) > 1, list(map(lambda x: list(map(lambda y: unquote_plus(y), x.split("="))), query.split("&")))))))
	query = urlencode(_query)
	_query.update({"sig": calc_sig(query)}) # Calculate signature of all query before we set "sig" up.
	return f"{scheme}://{netloc}{path}?{urlencode(_query)}"

def basic_test(query_part):
	"""
		https://products.wolframalpha.com/api/documentation/#formatting-input
	"""
	print(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
	r = s.get(craft_signed_url(f"https://{SERVER}/v2/query.jsp?{query_part}"))
	if r.status_code == 200:
		return r.text
	else:
		raise Exception(f"Error({r.status_code}) happened!\n{r.text}")

if __name__ == "__main__":
	obama = str(input("What would you like to know, you filthy pirate? "))
	bruh=urllib.parse.quote_plus(obama)
	txt = basic_test("input=" + bruh + "&podstate=Result__Step-by-step%20solution&format=image")
	print(txt)
	reg = re.findall("https[^';]+[^']+",txt)
	q = 6547777776
	for i in reg:
		if "=" in (i[-3],i[-2]) and i[-1].isdigit():
			q+=1
			print(i)
			urllib.request.urlretrieve(i.replace("amp;",""), str(q)+".jpg")
	list_im = [str(i)+".jpg" for i in range(6547777777,q+1)]
	imgs = [PIL.Image.open(i) for i in list_im]
	print(sorted([(np.sum(i.size), i.size) for i in imgs]))
	wideboy = sorted([i.size[0] for i in imgs])[-1]
	#get width of widest image
	#resize all images so they match that width
	imgs2 = []
	for img in imgs:
		wpercent = (wideboy/float(img.size[0]))
		hsize = int((float(img.size[1])*float(wpercent)))
		img = img.resize((wideboy,hsize), Image.ANTIALIAS)
		imgs2.append(img)
	#stack images
	print(sorted([(np.sum(i.size), i.size) for i in imgs2]))
	#delete images
	#save resultx
	imgs_comb = np.vstack((i for i in imgs2))
	imgs_comb = Image.fromarray(imgs_comb)
	imgs_comb.save('filth.jpg')
###&format=plaintext&output=json