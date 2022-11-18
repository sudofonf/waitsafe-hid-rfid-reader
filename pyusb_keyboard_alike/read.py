from keyboard_alike import reader
def start_reading(VendorID, ProductID):

	cursor = reader.Reader(VendorID, ProductID, 8, 16, should_reset=False)
	cursor.initialize()
	while True:
		print(cursor.read().strip())
		
	cursor.disconnect()

start_reading(65535, 53)
