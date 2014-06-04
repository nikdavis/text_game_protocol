
import socket
import json
from time import sleep


UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 20014
UDP_IP = "127.0.0.1"
UDP_PORT = 20015

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind( (UDP_IP, UDP_PORT) )
s.settimeout(0.5)
#s.listen(1)

# Convert unicode to UTF-8 string
# Courtesy:
# http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

while True:
	ret = s.sendto("<start>\r\nStats: Please\r\n<end>\r\n", (UDP_SERVER_IP, UDP_SERVER_PORT))
	print "Sent %d bytes to %s:%s" % (ret, UDP_SERVER_IP, UDP_SERVER_PORT)
	try:
		ret = s.recvfrom(1024)
		cls = [ int(s_uni) for s_uni in json.loads(ret[0]) ]
		cls.sort()
		print "Clients: " + str(cls)
	except socket.timeout:
		print "No response from server."
	#sleep(1)
	break