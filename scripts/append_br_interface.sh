if grep -q 'auto br-host' /etc/network/interfaces
then
  echo "br-host already in place"
else
  cat << EOF >> /etc/network/interfaces

auto br-host
iface br-host inet static
    address $1
    netmask $2
    gateway $3
    dns-nameservers $4
    bridge_ports $5
    bridge_stp off
    bridge_waitport 0
    bridge_fd 0
EOF
fi
