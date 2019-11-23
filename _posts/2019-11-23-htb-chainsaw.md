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

With all of that being said... Time to get crackin'! 



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