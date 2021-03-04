mystring = "Welcome"
mybytes = mystring.encode('utf-8')
myint = int.from_bytes(mybytes, 'little')
print(myint)
recoveredbytes = myint.to_bytes((myint.bit_length() + 7) // 8, 'little')
recoveredstring = recoveredbytes.decode('utf-8')
print(recoveredstring)
