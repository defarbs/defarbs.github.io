---
layout: post
title:  "Hack The Box: 'Chainsaw' Writeup"
image: ''
date:   2019-11-23 00:11:43
tags:
- hackthebox
- blockchain
- smart-contracts
- linux
- python
- solidity
- web3
- manual-exploit

description: ''
categories:
- Hack The Box
---

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
	
	.fortune-img {
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

<!-- add the button style & script -->
<link rel="stylesheet" href="/assets/css/applause-button.css" />
<script src="/assets/js/applause-button.js"></script>

<img src="/assets/img/writeups/HTB-CHAINSAW/HTB-CHAINSAW-BADGE.PNG" class="chainsaw-img" alt="Hack The Box - Chainsaw">

### Overview

The `Chainsaw` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/41600">artikrh</a> and <a href="https://www.hackthebox.eu/home/users/profile/37317">absolutezero</a>) is a retired 40 point Linux machine. The initial steps require manual exploitation of smart contracts via a few files that can be found in an FTP share with `anonymous` login enabled. Once a shell has been obtained, there is a privilege escalation technique involving the InterPlanetary File System (`IPFS`) which leads to SSH key cracking (and eventually `user.txt`). For root, there is a `setuid elf` binary called `ChainsawClub` which can be exploited in a similar fashion to the first exploit.
<p><br></p>
With all of that being said... Time to get crackin'! 
<p><br></p>

### Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code> nmap -p- -sCV -A -Pn 10.10.10.142 > nmap_scan_full_chainsaw.nmap
Starting Nmap 7.80 ( https://nmap.org ) at 2019-11-23 13:36 EST
Nmap scan report for 10.10.10.142
Host is up (0.037s latency).

PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-r--r--    1 1001     1001        23828 Dec 05  2018 WeaponizedPing.json
| -rw-r--r--    1 1001     1001          243 Dec 12  2018 WeaponizedPing.sol
|_-rw-r--r--    1 1001     1001           44 Nov 23 17:17 address.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to ::ffff:10.10.14.34
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp   open  ssh     OpenSSH 7.7p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 02:dd:8a:5d:3c:78:d4:41:ff:bb:27:39:c1:a2:4f:eb (RSA)
|   256 3d:71:ff:d7:29:d5:d4:b2:a6:4f:9d:eb:91:1b:70:9f (ECDSA)
|_  256 7e:02:da:db:29:f9:d2:04:63:df:fc:91:fd:a2:5a:f2 (ED25519)
9810/tcp open  unknown
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.1 400 Bad Request
|     Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, User-Agent
|     Access-Control-Allow-Origin: *
|     Access-Control-Allow-Methods: *
|     Content-Type: text/plain
|     Date: Sat, 23 Nov 2019 18:37:25 GMT
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.1 400 Bad Request
|     Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, User-Agent
|     Access-Control-Allow-Origin: *
|     Access-Control-Allow-Methods: *
|     Content-Type: text/plain
|     Date: Sat, 23 Nov 2019 18:37:24 GMT
|     Connection: close
|     Request
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, User-Agent
|     Access-Control-Allow-Origin: *
|     Access-Control-Allow-Methods: *
|     Content-Type: text/plain
|     Date: Sat, 23 Nov 2019 18:37:24 GMT
|_    Connection: close
</code></pre></div></div>

I immediately notice there is an FTP server with `anonymous` login allowed, so I check that first using `ftp`:

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>+[root@rattLR: HTB-CHAINSAW]$ ftp 10.10.10.142
Connected to 10.10.10.142.
220 (vsFTPd 3.0.3)
Name (10.10.10.142:root): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
+ftp> mget *
+mget WeaponizedPing.json? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for WeaponizedPing.json (23828 bytes).
226 Transfer complete.
23828 bytes received in 0.04 secs (526.2219 kB/s)
+mget WeaponizedPing.sol? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for WeaponizedPing.sol (243 bytes).
226 Transfer complete.
243 bytes received in 0.00 secs (2.3891 MB/s)
+mget address.txt? 
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for address.txt (44 bytes).
226 Transfer complete.
44 bytes received in 0.00 secs (343.7500 kB/s)
</code></pre></div></div>

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