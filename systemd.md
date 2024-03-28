
sudo nano /etc/systemd/system/questions_to_yourself_bot.service

questions_to_yourself_bot

[Unit]
Description=questions_to_yourself_bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/game/questions_to_yourself_bot
ExecStart=/usr/bin/python3 /root/game/questions_to_yourself_bot/questions_to_yourself_bot.py
Restart=always

[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reload
sudo systemctl start questions_to_yourself_bot
