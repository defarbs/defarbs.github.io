---
layout: post
title:  "Hack The Box: 'Fortune' Writeup"
image: ''
date:   2019-08-05 00:09:53
tags:
- hackthebox
- pkcs12 certificate
- RCE
- nfs share
- pgadmin4
- sqlite3
- crypto

description: ''
categories:
- Hack The Box
---

<style>
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

<img src="/assets/img/writeups/HTB-FORTUNE/HTB-FORTUNE-BADGE.png" class="fortune-img" alt="Hack The Box - Fortune">

### Overview

The `Fortune` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/46317">AuxSarge</a>) is a retired 50 point OpenBSD machine with some interesting complexities to it. If you have completed all of the previous boxes on HackTheBox, then `Fortune` should be pretty simple, as there is nothing particularly new introduced. 

The box starts with simple web enumeration to locate RCE found in the site's `db` variable, which occurs when a semi colon (;) is appended to the end of the `db`. Next, some files are located via the RCE that can be used to create a PKCS12 cert which permits access to port 443. From there, an SSH key is located to access the `nfsuser` and escalate to the user `charlie` by mounting a newly found nfs share. SSH keys for `charlie` are then used to access the user via SSH and enumerate further.

Finally, there is a `pgadmin4` database running on the box which contains hashes for the root password. A file called `crypto.py` is utilized for `pgadmin4's` encoding/decoding process, and can be used here to decode the root password and ultimately grab the flag.

TL;DR, this box is a fun ride! Let's get started with our `Nmap` scan!

###Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>root@rattLR:~/HTB-FORTUNE# nmap -sC -sV -A -Pn 10.10.10.127

Starting Nmap 7.70 ( https://nmap.org ) at 2019-07-24 11:27 EST
Nmap scan report for 10.10.10.127
Host is up (0.21s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.9 (protocol 2.0)
| ssh-hostkey: 
|   2048 07:ca:21:f4:e0:d2:c6:9e:a8:f7:61:df:d7:ef:b1:f4 (RSA)
|   256 30:4b:25:47:17:84:af:60:e2:80:20:9d:fd:86:88:46 (ECDSA)
|_  256 93:56:4a:ee:87:9d:f6:5b:f9:d9:25:a6:d8:e0:08:7e (EdDSA)
80/tcp  open  http       syn-ack OpenBSD httpd
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: OpenBSD httpd
|_http-title: Fortune
443/tcp open  ssl/https? syn-ack
|_ssl-date: TLS randomness does not represent time
</code></pre></div></div>

So, it appears port `443` is HTTPS (as expected), but it requires an SSL certificate to access it. I'll leave it alone for now because of this. However, port `80` proves to be quite interesting. Here's what I discovered upon navigating to it:

<!--Include screenshot of web fortunes here-->

Hmm... 

Let's try capturing a request with `Burp Suite!`