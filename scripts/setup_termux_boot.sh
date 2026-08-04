#!/data/data/com.termux/files/usr/bin/bash
mkdir -p ~/.termux/boot/
cat > ~/.termux/boot/start_selix.sh << 'EOL'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/selix && ./start_selix.sh
EOL
chmod +x ~/.termux/boot/start_selix.sh
termux-wake-lock
