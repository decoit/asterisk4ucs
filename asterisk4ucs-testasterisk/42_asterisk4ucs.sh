#!/bin/sh

# allow tcp port 5060
/sbin/iptables -A INPUT -p "tcp" --dport 5060 -j ACCEPT
/sbin/ip6tables -A INPUT -p "tcp" --dport 5060 -j ACCEPT

# allow udp highports
/sbin/iptables -A INPUT -p "udp" --dport 1024:65535 -j ACCEPT
/sbin/ip6tables -A INPUT -p "udp" --dport 1024:65535 -j ACCEPT

