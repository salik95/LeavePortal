from app.controllers.settings import settings_to_dict
import base64

def encode(target):
	enc = []
	key = settings_to_dict()['company_name']

	for i in range(len(target)):
		key_c = key[i % len(key)]
		enc_c = chr((ord(target[i]) + ord(key_c)) % 256)
		enc.append(enc_c)
	return base64.b64encode("".join(enc).encode()).decode()

def decode(target):
	dec = []
	key = settings_to_dict()['company_name']
	enc = base64.b64decode(target).decode()
	for i in range(len(enc)):
		key_c = key[i % len(key)]
		dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
		dec.append(dec_c)
	return "".join(dec)