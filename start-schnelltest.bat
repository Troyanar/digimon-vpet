@echo off
title Digimon V-Pet (Schnelltest x60)
cd /d "%~dp0"
echo Schnelltest: Zeit laeuft 60x schneller (1 Sekunde = 1 Minute).
echo Benutzt einen eigenen Spielstand (testgame.db), dein echtes Digimon bleibt unberuehrt.
set VPET_SPEED=60
set VPET_DB=testgame.db
set VPET_PORT=8001
python server.py
pause
