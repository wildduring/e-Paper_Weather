PREFIX=/usr
BINDIR=$(PREFIX)/bin

test=$(shell if [ -d $(DESTDIR)$(BINDIR)/e-Paper_weather/ ]; then echo "exist"; else echo "noexist"; fi)

all:
	@echo "Run 'make install' for installation."
	@echo "Run 'make uninstall' for uninstallation."

install:
ifeq ("$(test)", "noexist")
	@echo "Directory dosn't exist, make direction."
	$(shell mkdir $(DESTDIR)$(BINDIR)/e-Paper_weather/)
endif
	cp -r program/* $(DESTDIR)$(BINDIR)/e-Paper_weather/
	cp e-Paper_weather.service $(DESTDIR)$(PREFIX)/lib/systemd/system/e-Paper_weather.service
	systemctl daemon-reload

uninstall:
	systemctl stop e-Paper_weather.service
	systemctl disable e-Paper_weather.service
	rm -r $(DESTDIR)$(BINDIR)/e-Paper_weather/
	rm $(DESTDIR)$(PREFIX)/lib/systemd/system/e-Paper_weather.service
	systemctl daemon-reload
