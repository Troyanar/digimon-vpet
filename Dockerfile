# Digimon V-Pet als Container – nur Python, keine Zusatzpakete fürs Spiel.
FROM python:3.12-slim
# Markierung, damit deploy.bat beim Aufräumen nur alte V-Pet-Images löscht
LABEL app=vpet

# Zeitzonen-Daten (für Tag/Nacht im Spiel); der Rest kommt aus der Standardbibliothek
RUN pip install --no-cache-dir tzdata

WORKDIR /app
COPY server.py ./
COPY game ./game
COPY static ./static
COPY data ./data
COPY tools ./tools

# Spielstand und Backups liegen außerhalb des Containers (siehe docker-compose.yml)
ENV VPET_HOST=0.0.0.0 \
    VPET_PORT=8000 \
    VPET_DB=/app/state/savegame.db \
    VPET_NO_BROWSER=1 \
    VPET_TZ=Europe/Berlin \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "server.py"]
