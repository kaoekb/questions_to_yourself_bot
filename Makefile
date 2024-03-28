.PHONY: install start enable status

install:
	sudo cp questions_to_yourself_bot.service /etc/systemd/system/
	sudo systemctl daemon-reload

nano:
	nano .env
start:
	sudo systemctl start questions_to_yourself_bot

enable:
	sudo systemctl enable questions_to_yourself_bot

status:
	sudo systemctl status questions_to_yourself_bot
