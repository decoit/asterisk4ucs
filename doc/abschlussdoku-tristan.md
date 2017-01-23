

Releasen
========

**Nachfolgend werden $-Platzhalter verwendet. Dabei steht `$repo` für das Hauptverzeichnis des Asterisk4UCS-Repo-Clones, und `$version` für die zu releasende Version.**

Sicherstellen, dass man alle geänderten Pakete per ChangeLog mit neuer Versionsnummer versehen hat. Dazu am besten auf einem Debian mit installiertem `devscripts`:

	cd $repo/asterisk4ucs-foo/
	dch -i

Aufpassen, dass man nichts am Whitespace ändert, sonst wollen die Packaging-Tools von Debian das Paket nicht mehr bauen.

Nun alle Pakete neubauen. Dies muss eigentlich je einmal auf einem i386- und einem x86_64-System erfolgen, aber im Moment sind noch alle Asterisk4UCS-Pakete architekturunabhängig. Für das Kopieren später ist es erforderlich, zunächst alle deb-Files aus dem Hauptverzeichnis des Repos zu löschen:

	cd $repo/
	rm *.deb
	./buildall

Ordner für Release anlegen und Asterisk4UCS-debs hineinlegen:

	cd $repo/release/
	mkdir asterisk4ucs-$version
	cp ../*.deb asterisk4ucs-$version/

Nun müssen noch die Abhängigkeiten, die im unmaintained-Teil des Univention-Repos liegen, dazugepackt werden. Dazu verwendet man zwei frische UCS-Installationen, eine 32-bittige und eine 64-bittige. Auf den beiden Systemen sollte außer der UCS-Installation noch nichts passiert sein. Die Systeme müssen die UCS-Version haben, für die man das Release durchführen will. VM-Snapshots sind hier seehr hilfreich (man kann dann nämlich diese Systeme auch als Test-VMs verwenden und danach zurückrollen).

Auf beiden Systemen ausführen:

	ucr set repository/online/unmaintained=yes
	apt-get update
	apt-get --print-uris -y install asterisk asterisk-modules asterisk-config asterisk-voicemail-odbcstorage sox libsox-fmt-base libsox-fmt-mp3 > dependency-uris

Die ausgegebenen URI-Listen werden dann auf der Entwicklungs-VM in beliebiger Reihenfolge nacheinander in die Datei `$repo/release/dependency-uris` kopiert (alten Inhalt löschen).

Nun kann auf der Entwicklungs-VM das Release-Script aufgerufen werden:

	./release $version

Das erzeugte Archiv `asterisk4ucs-$version.tar` kann nun an den Univention-Support gesendet werden, damit es ins AppCenter getan wird.

Release testen
==============

Dazu geht man auf ein frisches UCS und entpackt dort das Archiv (vorher z.B. mit `scp` hinkopieren):

	tar -xf asterisk4ucs-1.42.tar
	cd asterisk4ucs-1.42/

Nun muss man herausfinden, welche Architektur die VM hat (i386 oder x86_64). Das weiß man entweder auswändig, oder man guckt nach mit `uname -a`. Nun tut man auf einem `i386`:

	dpkg -i *_i386.deb *_all.deb

Oder auf einem `x86_64`:

	dpkg --force-depends -i *_amd64.deb *_all.deb

Nun sollte die Installation ohne Fehler durchlaufen. Danach kann man die App dann testen.

