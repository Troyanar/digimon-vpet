"""Englische Übersetzungen für game/i18n.py: deutsche Vorlage -> englische Vorlage.

Platzhalter ({name} …) müssen in beiden Fassungen gleich heißen.
Begriffe (Glossar): Digitation = Digivolution, Pflegefehler = care mistake,
Ruf = call, Kraft = strength (Training: Power/Speed/Defense), Sammlung = collection,
Kühlschrank = fridge, Erkunden = explore, Rucksack = backpack, Merkliste = wishlist,
Rangliste = leaderboard, Ultra = Ultimate, Serum = Vaccine, Daten = Data.

Prüfen: python check_i18n.py (findet fehlende Einträge und falsche Platzhalter).
"""

EN = {
    # ------------------------------------------------------------ Stufen & Attribute
    "Ei": "Egg",
    "Baby I": "Baby I",
    "Baby II": "Baby II",
    "Rookie": "Rookie",
    "Champion": "Champion",
    "Armor": "Armor",
    "Ultra": "Ultimate",
    "Mega": "Mega",
    "Digi-Ei": "Digi-Egg",
    "Digi-Ei {name}": "Digi-Egg {name}",
    "Serum": "Vaccine",
    "Daten": "Data",
    "Virus": "Virus",
    "Frei": "Free",
    "ohne Attribut": "without attribute",
    "Kraft": "Power",
    "Tempo": "Speed",
    "Verteidigung": "Defense",
    "Krafttraining": "Power training",
    "Tempotraining": "Speed training",
    "Verteidigungstraining": "Defense training",

    # ------------------------------------------------------------ pet.py – Pflege
    "Ein Ei bekommt seinen Namen erst, wenn es geschlüpft ist.": "An egg gets its name once it has hatched.",
    "Dein Digimon lebt nicht mehr.": "Your Digimon is no longer alive.",
    "{species} heißt jetzt {name}.": "{species} is now called {name}.",
    "{species} heißt jetzt {name}!": "{species} is now called {name}!",
    "{species} hat keinen Spitznamen mehr.": "{species} no longer has a nickname.",
    "Digimon Nr. {n}": "Digimon No. {n}",
    " oder ": " or ",
    "ein {attrs}-Digimon": "a {attrs} Digimon",
    "{name} ist nicht fit genug für eine Fusion.": "{name} isn't fit enough for a fusion.",
    "Diese Fusion passt gerade nicht.": "This fusion doesn't work right now.",
    "{partner} von {owner}": "{owner}'s {partner}",
    "Jogress! {old} + {who} = {new}!": "Jogress! {old} + {who} = {new}!",
    "Jogress! {old} und {who} verschmelzen zu {new}!": "Jogress! {old} and {who} fuse into {new}!",
    "Das Ei ist geschlüpft: {name}!": "The egg has hatched: {name}!",
    "{old} hat sich zu {new} entwickelt!": "{old} digivolved into {new}!",
    "{name} ist gestorben ({cause}).": "{name} has died ({cause}).",
    "Das Schutz-Totem hat {name} vor dem Tod gerettet ({cause})! {name} wartet im Kühlschrank auf dich.":
        "The Guardian Totem saved {name} from death ({cause})! {name} is waiting for you in the fridge.",
    "Pflegefehler: {what}": "Care mistake: {what}",
    "Hunger ignoriert": "hunger ignored",
    "Kraft leer ignoriert": "empty strength ignored",
    "Licht beim Schlafen angelassen": "light left on while sleeping",
    "verhungert": "starved",
    "Krankheit nicht behandelt": "sickness not treated",
    "Verletzung nicht behandelt": "injury not treated",
    "zu viele Pflegefehler": "too many care mistakes",
    "{name} ist eingeschlafen. Licht aus!": "{name} fell asleep. Lights out!",
    "{name} ist aufgewacht.": "{name} woke up.",
    "Guten Morgen! {name} döst im Dunkeln weiter – Licht an weckt es.":
        "Good morning! {name} keeps dozing in the dark – turning on the light wakes it.",
    "{name} ist vom Dreck krank geworden!": "{name} got sick from all the poop!",
    "{name} ist vom Erkunden zurück.": "{name} is back from exploring.",
    "{name} hat den Kampf liegen lassen – zählt als Niederlage.": "{name} abandoned the battle – counts as a loss.",
    "{name} ist gerade unterwegs – zurück um {end} Uhr.": "{name} is out exploring – back at {end}.",
    "{name} ist im Kühlschrank. Erst auftauen!": "{name} is in the fridge. Thaw it first!",
    "Erst den Kampf beenden (oder fliehen).": "Finish the battle first (or flee).",
    "{name} ist im Kühlschrank.": "{name} is in the fridge.",
    "{name} ist aufgetaut.": "{name} has thawed.",
    "{name} ist im Kühlschrank. Die Zeit steht still, bis du es auftaust.":
        "{name} is in the fridge. Time stands still until you thaw it.",
    "{name} ist aufgetaut und freut sich auf dich!": "{name} has thawed and is happy to see you!",
    "Das Ei schlüpft gleich ...": "The egg is about to hatch ...",
    "{name} macht ein Nickerchen. Licht an weckt es.": "{name} is taking a nap. Turning on the light wakes it.",
    "{name} schläft gerade. Psst!": "{name} is sleeping. Shh!",
    "{name} riecht Futter und wacht aus dem Nickerchen auf.": "{name} smells food and wakes up from its nap.",
    "{name} will nichts mehr essen.": "{name} doesn't want to eat anymore.",
    "{name} hat sich überfressen! (+1 g)": "{name} is overfed! (+1 g)",
    "{name} isst Fleisch. Hunger +1": "{name} eats meat. Hunger +1",
    "{name} schluckt Protein. Kraft +1 (+2 g)": "{name} gulps down protein. Strength +1 (+2 g)",
    "Unbekanntes Futter.": "Unknown food.",
    "Diese Trainingsart gibt es nicht.": "That kind of training doesn't exist.",
    "{name} ist nicht fit genug zum Trainieren.": "{name} isn't fit enough to train.",
    "Super {training}! Kraft-Herz +1, {skill} {points} (-2 g)":
        "Great {training}! Strength heart +1, {skill} {points} (-2 g)",
    "{training} daneben ... (-2 g)": "{training} missed ... (-2 g)",
    "Hier ist schon alles sauber.": "Everything is already clean.",
    "Alles sauber geputzt!": "All cleaned up!",
    "Licht aus. Gute Nacht!": "Lights out. Good night!",
    "Licht aus.": "Lights out.",
    "{name} macht ein Nickerchen.": "{name} is taking a nap.",
    "Licht aus – {name} macht ein Nickerchen. Licht an weckt es wieder.":
        "Lights out – {name} is taking a nap. Turning the light on wakes it up again.",
    "{name} ist vom Nickerchen aufgewacht.": "{name} woke up from its nap.",
    "Licht an – {name} ist ausgeschlafen!": "Lights on – {name} is well rested!",
    "Licht an – aber {name} muss jetzt schlafen. Mach das Licht wieder aus!":
        "Lights on – but {name} needs to sleep now. Turn the light off again!",
    "Licht an.": "Lights on.",
    "{name} ist gesund und braucht keine Medizin.": "{name} is healthy and doesn't need medicine.",
    "{name} ist wieder gesund!": "{name} is healthy again!",

    "{name} hat jetzt kein Ziel mehr.": "{name} no longer has a goal.",
    "Neues Ziel für {name}: {goal}.": "New goal for {name}: {goal}.",
    "Dafür brauchst du ein geschlüpftes Digimon.": "You need a hatched Digimon for that.",
    "Dein Digimon ist gerade nicht vom Erkunden zurückgekommen.": "Your Digimon hasn't just come back from exploring.",
    "Willkommen zurück, {name}!": "Welcome back, {name}!",
    "Ein wildes {name} ist mitgekommen – kämpfen oder fliehen?": "A wild {name} came along – fight or flee?",
    "{name} ist vom Erkunden zurück – bestätige erst die Rückkehr (OK).":
        "{name} is back from exploring – confirm the return first (OK).",

    # ------------------------------------------------------------ battle.py – wilde Digimon
    "{name} ist noch zu klein zum Kämpfen – ab Rookie geht's los.":
        "{name} is still too small to battle – battles start at Rookie.",
    "{name} schläft gerade.": "{name} is sleeping.",
    "{name} ist nicht fit genug zum Kämpfen. Erst Medizin!": "{name} isn't fit enough to battle. Medicine first!",
    "{name} ist zu hungrig oder zu schlapp zum Kämpfen.": "{name} is too hungry or too weak to battle.",
    "viel stärker als deins": "much stronger than yours",
    "etwas stärker als deins": "a bit stronger than yours",
    "viel schwächer als deins": "much weaker than yours",
    "etwas schwächer als deins": "a bit weaker than yours",
    "ungefähr gleich stark": "about as strong as yours",
    "Du bist schon in einem Kampf.": "You're already in a battle.",
    "Ein wildes {name} ({attr}) taucht auf! Es wirkt {hint}.": "A wild {name} ({attr}) appears! It looks {hint}.",
    "Dein Attribut hat Vorteil!": "Your attribute has the advantage!",
    "Achtung, Attribut-Nachteil!": "Careful, attribute disadvantage!",
    "Mitten im Kampf kannst du nicht mehr fliehen!": "You can't flee in the middle of a battle!",
    "Du bist geflohen.": "You fled.",
    "Der Gegner ist weg. Such einen neuen.": "The opponent is gone. Look for a new one.",
    "Kampf gegen {name}! Lade deinen Schuss!": "Battle against {name}! Charge your shot!",
    "Gerade läuft kein Kampf.": "There's no battle going on right now.",
    "Der Kampf ist vorbei.": "The battle is over.",
    "Der Gegner ist abgehauen – du warst zu lange weg.": "The opponent ran off – you were away too long.",
    "{name} hat {opp} besiegt!": "{name} defeated {opp}!",
    "{opp} hat ein Digi-Ei fallen lassen!": "{opp} dropped a Digi-Egg!",
    "{name} hat gegen {opp} verloren.": "{name} lost against {opp}.",
    # Ende nach der letzten Runde (die Leben entscheiden)
    "Nach {n} Runden ist Schluss:": "Time's up after {n} rounds:",
    "{name} hat mehr Leben übrig und gewinnt gegen {opp}!": "{name} has more lives left and wins against {opp}!",
    "{opp} hat mehr Leben übrig – {name} verliert.": "{opp} has more lives left – {name} loses.",
    "{name} und {opp} haben gleich viele Leben – unentschieden! {opp} zieht sich zurück.":
        "{name} and {opp} have the same number of lives – it's a draw! {opp} retreats.",
    "Es ist verletzt – gib ihm Medizin!": "It's injured – give it medicine!",
    # Persönlichkeiten wilder Digimon ("ruhig" steht weiter unten), Spezialattacke, Ausweichen
    "aggressiv": "aggressive",
    "gepanzert": "armored",
    "flink": "nimble",
    "listig": "sly",
    "Es wirkt ruhig.": "It seems calm.",
    "Es wirkt aggressiv – oft greift es zweimal an!": "It seems aggressive – it often attacks twice!",
    "Es wirkt gepanzert – es hält 4 Treffer aus.": "It seems armored – it can take 4 hits.",
    "Es wirkt flink – schwer zu treffen, nicht zu lange laden!": "It seems nimble – hard to hit, don't charge too long!",
    "Es wirkt listig – es merkt sich, wo du angreifst.": "It seems sly – it remembers where you attack.",
    "Spezialattacke": "Special Attack",
    "Deine Spezial-Leiste ist noch nicht voll.": "Your special gauge isn't full yet.",
    "Gerade fliegt kein Angriff auf dich zu.": "No attack is coming at you right now.",

    # ------------------------------------------------------------ duel.py – Kämpfe gegen Freunde
    "{whose} hat gerade kein Digimon.": "{whose} has no Digimon right now.",
    "{whose} kämpft gerade schon gegen ein wildes Digimon.": "{whose} is already fighting a wild Digimon.",
    "{whose}: {reason}": "{whose}: {reason}",
    "Dein Digimon": "Your Digimon",
    "Das Digimon von {name}": "{name}'s Digimon",
    "Du kannst dich nicht selbst herausfordern.": "You can't challenge yourself.",
    "{name} ist schon in einem Kampf.": "{name} is already in a battle.",
    "Diese Herausforderung gilt nicht mehr.": "This challenge is no longer valid.",
    "{name} hat abgelehnt.": "{name} declined.",
    "Herausforderung abgelehnt.": "Challenge declined.",
    "Der Kampf beginnt!": "The battle begins!",
    "Du hast schon geschossen – warte auf deinen Gegner.": "You've already shot – wait for your opponent.",
    "Jetzt heißt es ausweichen!": "Time to dodge!",
    "Du hast schon reagiert – warte auf deinen Gegner.": "You've already reacted – wait for your opponent.",
    "Die Herausforderung ist abgelaufen.": "The challenge has expired.",
    "Zu spät – der Kampf hat schon begonnen!": "Too late – the battle has already started!",
    "Die Herausforderung wurde zurückgezogen.": "The challenge was withdrawn.",
    "Herausforderung zurückgezogen.": "Challenge withdrawn.",
    "Du hast aufgegeben.": "You gave up.",
    "Kampf abgebrochen – ein Digimon wurde getauscht.": "Battle cancelled – a Digimon was switched.",
    "{name} hat gegen {opp} gewonnen!": "{name} won against {opp}!",
    "Unentschieden gegen {opp}.": "Draw against {opp}.",
    "Es ist verletzt!": "It's injured!",
    "{loser} hat aufgegeben – {winner} gewinnt!": "{loser} gave up – {winner} wins!",
    "{winner} gewinnt den Kampf!": "{winner} wins the battle!",
    "Unentschieden!": "It's a draw!",

    # ------------------------------------------------------------ explore.py – Gebiete
    "Urwald": "Jungle",
    "Küste": "Coast",
    "Wolkenberge": "Cloud Peaks",
    "Metallstadt": "Metal City",
    "Drachenvulkan": "Dragon Volcano",
    "Dunkle Zone": "Dark Zone",

    # ------------------------------------------------------------ explore.py – Items (Rucksack)
    "Leckerbissen": "Treat",
    "Hunger und Kraft voll (+2 g)": "Hunger and Strength full (+2 g)",
    "Trainingsgewicht": "Training Weight",
    "+2 Trainings in dieser Stufe": "+2 trainings in this stage",
    "Glücksbringer": "Lucky Charm",
    "Nächster Kampf: deutlich stärker": "Next battle: much stronger",
    "Schutz-Totem": "Guardian Totem",
    "Rettet einmal vor dem Tod – ab in den Kühlschrank": "Saves from death once – off into the fridge",
    # Armor-Eier (Namen und Beschreibungen kommen aus data/digimon.json)
    "Armor-Ei des Mutes": "Armor Egg of Courage",
    "Armor-Ei der Freundschaft": "Armor Egg of Friendship",
    "Armor-Ei der Liebe": "Armor Egg of Love",
    "Armor-Ei der Aufrichtigkeit": "Armor Egg of Sincerity",
    "Armor-Ei des Wissens": "Armor Egg of Knowledge",
    "Armor-Ei der Zuverlässigkeit": "Armor Egg of Reliability",
    "Armor-Ei der Hoffnung": "Armor Egg of Hope",
    "Armor-Ei des Lichts": "Armor Egg of Light",
    "Goldenes Armor-Ei der Wunder": "Golden Armor Egg of Miracles",
    "Armor-Digitation für Veemon": "Armor Digivolution for Veemon",
    "Armor-Digitation für Hawkmon": "Armor Digivolution for Hawkmon",
    "Armor-Digitation für Armadillomon": "Armor Digivolution for Armadillomon",
    "Armor-Digitation für Patamon": "Armor Digivolution for Patamon",
    "Armor-Digitation für Salamon oder Gatomon": "Armor Digivolution for Salamon or Gatomon",

    # ------------------------------------------------------------ explore.py – Expeditionen
    "Dieses Ziel gibt es nicht.": "That destination doesn't exist.",
    "In {area} ist es zu gefährlich – erst ab {stage}.": "{area} is too dangerous – {stage} or higher only.",
    "{name} ist nicht fit genug. Erst Medizin!": "{name} isn't fit enough. Medicine first!",
    "{name} braucht Proviant – erst füttern.": "{name} needs supplies – feed it first.",
    "Erst den Kampf beenden.": "Finish the battle first.",
    "{name} erkundet {area}.": "{name} is exploring {area}.",
    "{name} zieht los in {area}! Zurück in {duration}.": "{name} sets off for {area}! Back in {duration}.",
    "Dein Digimon ist gar nicht unterwegs.": "Your Digimon isn't out exploring.",
    "{name} wurde zurückgerufen.": "{name} was called back.",
    "{name} ist zurück – leider mit leeren Händen.": "{name} is back – empty-handed, sadly.",
    "{n} Min": "{n} min",
    "{n} Std": "{n} h",
    "ein {egg}": "a {egg}",
    "ein {egg} (Sammlung voll – liegen gelassen)": "a {egg} (collection full – left behind)",
    "{name} ist zurück aus {area}!": "{name} is back from {area}!",
    "Gefunden: {things}.": "Found: {things}.",
    "Diesmal nichts gefunden.": "Nothing found this time.",
    "Ein wildes {name} ist ihm gefolgt!": "A wild {name} followed it home!",

    # ------------------------------------------------------------ explore.py – Items benutzen
    "{name} verputzt den Leckerbissen. Hunger und Kraft voll!": "{name} gobbles up the Treat. Hunger and Strength full!",
    "{name} stemmt das Trainingsgewicht. +2 Trainings!": "{name} lifts the Training Weight. +2 trainings!",
    "{name} trägt schon einen Glücksbringer.": "{name} is already wearing a Lucky Charm.",
    "{name} trägt jetzt den Glücksbringer – der nächste Kampf wird leichter!":
        "{name} is now wearing the Lucky Charm – the next battle will be easier!",
    "{name} hält schon ein Schutz-Totem.": "{name} is already holding a Guardian Totem.",
    "{name} hält jetzt das Schutz-Totem. Stirbt es, rettet das Totem es einmal – es landet dann im Kühlschrank.":
        "{name} is now holding the Guardian Totem. If it dies, the totem saves it once – it then ends up in the fridge.",
    "Dieses Item gibt es nicht.": "That item doesn't exist.",
    "„{egg}“ passt nicht zu {name} – {desc}.": "“{egg}” doesn't fit {name} – {desc}.",
    "{name} ist nicht fit genug für eine Digitation. Erst Medizin!": "{name} isn't fit enough to digivolve. Medicine first!",
    "Armor-Digitation mit „{egg}“: {new}!": "Armor Digivolution with “{egg}”: {new}!",
    "{name}, Armor-Digitation! Mit „{egg}“ wird es zu {new}!":
        "{name}, Armor Digivolve! With “{egg}” it becomes {new}!",

    # ------------------------------------------------------------ collection.py – Sammlung & Boxen
    "Box {n}": "Box {n}",
    "Diese Box gibt es nicht.": "That box doesn't exist.",
    "Die Box heißt jetzt „{name}“.": "The box is now called “{name}”.",
    "Dieses Digimon ist nicht in deiner Sammlung.": "That Digimon isn't in your collection.",
    "{name} ist schon in dieser Box.": "{name} is already in this box.",
    "{box} ist voll ({n} Plätze).": "{box} is full ({n} spots).",
    "{name} liegt jetzt in {box}.": "{name} is now in {box}.",
    "Die Sammlung ist voll ({n} Plätze). Lass erst eins frei.":
        "The collection is full ({n} spots). Release one first.",
    "{name} ruht jetzt in der Sammlung.": "{name} is now resting in the collection.",
    "{name} ist wieder dein Partner!": "{name} is your partner again!",
    "{name} ist jetzt aktiv.": "{name} is now active.",
    "{name} erkundet gerade {area} – zurück um {end} Uhr.": "{name} is exploring {area} – back at {end}.",
    "Eier können nicht erkunden.": "Eggs can't explore.",
    "In {area} ist es für {name} zu gefährlich – erst ab {stage}.":
        "{area} is too dangerous for {name} – {stage} or higher only.",
    "{name} ist nicht fit genug. Erst Medizin – dafür muss es aktiv sein.":
        "{name} isn't fit enough. Medicine first – it has to be active for that.",
    "Es sind schon {n} Digimon aus deiner Sammlung unterwegs.":
        "{n} Digimon from your collection are already out exploring.",
    "Dieses Digimon ist gar nicht unterwegs.": "That Digimon isn't out exploring.",
    "{name} wurde freigelassen. Mach's gut!": "{name} was released. Take care!",

    # ------------------------------------------------------------ social.py – Tauschen & Jogress
    "Mit wem willst du tauschen?": "Who do you want to trade with?",
    "Tauschen kannst du nur Eier und Digimon aus deiner Sammlung.":
        "You can only trade eggs and Digimon from your collection.",
    "Das steckt schon in einem anderen Tauschangebot.": "That's already part of another trade offer.",
    "{pet} an {name} verschenkt. {name} sieht es in der Sammlung.":
        "{pet} given to {name} as a gift. {name} will see it in the collection.",
    "{pet} an {name} zum Tausch angeboten. {name} sieht es in der Sammlung.":
        "{pet} offered to {name} for a trade. {name} will see it in the collection.",
    "Dieses Angebot gibt es nicht.": "That offer doesn't exist.",
    "Das ist kein Geschenk an dich.": "That's not a gift for you.",
    "Das Geschenk ist leider nicht mehr da.": "Sorry, the gift is no longer there.",
    "Deine Sammlung ist voll. Lass erst eins frei.": "Your collection is full. Release one first.",
    "{pet} ist jetzt in deiner Sammlung. Danke, {name}!": "{pet} is now in your collection. Thanks, {name}!",
    "Auf dieses Angebot kannst du nicht mehr antworten.": "You can no longer reply to this offer.",
    "Anbieten kannst du nur Eier und Digimon aus deiner Sammlung.":
        "You can only offer eggs and Digimon from your collection.",
    "Gegenangebot {pet} geschickt. {name} muss noch bestätigen.":
        "Counter-offer {pet} sent. {name} still has to confirm.",
    "Hier gibt es nichts zu bestätigen.": "There's nothing to confirm here.",
    "Der Tausch klappt nicht mehr – eins davon ist nicht mehr in der Sammlung.":
        "The trade doesn't work anymore – one of them is no longer in the collection.",
    "Getauscht! {pet} ist jetzt in deiner Sammlung.": "Traded! {pet} is now in your collection.",
    "Dieses Angebot ist schon erledigt.": "This offer is already closed.",
    "Angebot zurückgezogen.": "Offer withdrawn.",
    "Angebot abgelehnt.": "Offer declined.",
    "Mit wem willst du fusionieren?": "Who do you want to fuse with?",
    "Das Digimon von {name} passt nicht zu dieser Fusion.": "{name}'s Digimon doesn't fit this fusion.",
    "Es läuft schon eine Jogress-Anfrage.": "There's already a Jogress request going on.",
    "Anfrage an {name} geschickt. Warte auf Zustimmung ...": "Request sent to {name}. Waiting for approval ...",
    "Die Anfrage ist schon abgelaufen.": "The request has already expired.",
    "Jogress abgelehnt.": "Jogress declined.",
    "Die Fusion klappt nicht mehr – ein Digimon wurde getauscht.":
        "The fusion doesn't work anymore – a Digimon was switched.",
    "{name} hat {friend} bei einer Jogress geholfen!": "{name} helped {friend} with a Jogress!",
    "Geschafft! {message}": "Done! {message}",

    # ------------------------------------------------------------ accounts.py – Anmelden & Registrieren
    "Name: 3–20 Zeichen, nur Buchstaben, Zahlen, - und _.": "Name: 3–20 characters, only letters, numbers, - and _.",
    "Passwort: mindestens {n} Zeichen.": "Password: at least {n} characters.",
    "Das erste Admin-Konto bitte mit tools/admin_account.py anlegen.":
        "Please create the first admin account with tools/admin_account.py.",
    "Wartungsarbeiten – bitte später wieder versuchen.": "Maintenance – please try again later.",
    "Neue Konten sind gerade nicht möglich.": "New accounts aren't possible right now.",
    "Der Einladungscode stimmt nicht.": "The invite code is wrong.",
    "Diesen Namen gibt es schon.": "That name is already taken.",
    "Dieses Konto ist gesperrt.": "This account is banned.",
    "Name oder Passwort falsch.": "Wrong name or password.",
    "Das alte Passwort stimmt nicht.": "The old password is wrong.",
    "Neues Passwort: mindestens {n} Zeichen.": "New password: at least {n} characters.",

    # ------------------------------------------------------------ wishlist.py – Merkliste
    "Dieses Digimon gibt es nicht.": "That Digimon doesn't exist.",
    "Die Merkliste ist voll – höchstens {n} Digimon.": "The wishlist is full – {n} Digimon at most.",

    # ------------------------------------------------------------ admin.py – Admin-Hilfe (steht im Tagebuch)
    "{name} von {who} ist wieder gesund.": "{who}'s {name} is healthy again.",
    "{name} von {who} ist satt und stark.": "{who}'s {name} is full and strong.",
    "{name} von {who} lebt wieder!": "{who}'s {name} is alive again!",
    "Der Admin hat geholfen: {message}": "The admin helped: {message}",

    # ------------------------------------------------------------ server.py – Meldungen
    "Ungültige Zahl.": "Invalid number.",
    "Ungültige Anfrage": "Invalid request",
    "Ungültige Auswahl.": "Invalid selection.",
    "Anfrage zu groß": "Request too large",
    "Da ist auf dem Server etwas schiefgegangen.": "Something went wrong on the server.",
    "Bitte melde dich an.": "Please log in.",
    "Nur für Admins.": "Admins only.",
    "Nur für den Admin.": "Only for the admin.",
    "Zu viele Versuche. Bitte in {n} Minuten noch einmal probieren.": "Too many attempts. Please try again in {n} minutes.",
    "Passwort geändert. Andere Geräte wurden abgemeldet.": "Password changed. Other devices were logged out.",
    "Diese Sprache gibt es nicht.": "That language doesn't exist.",
    "Dieser Partner ist nicht in deiner Sammlung.": "That partner isn't in your collection.",
    "Dein Freund ist gerade nicht online.": "Your friend isn't online right now.",
    "Du hast gerade kein Digimon.": "You don't have a Digimon right now.",
    "Es gibt keine offene Anfrage.": "There's no open request.",
    "Diesen Spieler gibt es nicht.": "That player doesn't exist.",
    "{name} ist gerade nicht online.": "{name} isn't online right now.",
    "Herausforderung an {name} geschickt. Warte auf Antwort ...": "Challenge sent to {name}. Waiting for an answer ...",
    "Auf deine eigene Herausforderung kannst du nicht antworten.": "You can't answer your own challenge.",
    "Neue Eier findest du beim Erkunden und in Kämpfen.": "You find new eggs while exploring and in battles.",
    "Ein neues Digi-Ei!": "A new Digi-Egg!",
    "Erst den Kampf gegen deinen Freund beenden.": "Finish the battle against your friend first.",
    "Davon hast du nichts mehr im Rucksack.": "You don't have any of those left in your backpack.",
    "Aber deine Sammlung ist voll – das Ei bleibt liegen.": "But your collection is full – the egg stays behind.",
    "Es liegt jetzt in deiner Sammlung.": "It's in your collection now.",
    "Das geht gerade nicht.": "That's not possible right now.",

    # ------------------------------------------------------------ shop.py + neue Items (Bits, Ewigstein, Sanduhren …)
    "+{n} Bits": "+{n} Bits",
    "{n} Bits": "{n} Bits",
    "Das gibt es im Shop nicht.": "The shop doesn't sell that.",
    "Du kannst 1 bis {n} Stück auf einmal kaufen.": "You can buy 1 to {n} at a time.",
    "Dafür reichen deine Bits nicht: {cost} Bits nötig, du hast {have}.":
        "You don't have enough Bits: {cost} Bits needed, you have {have}.",
    "Gekauft: {item} für {cost} Bits.": "Bought: {item} for {cost} Bits.",
    "Gekauft: {n}× {item} für {cost} Bits.": "Bought: {n}× {item} for {cost} Bits.",
    "Da glitzert was: {n} Bits!": "Something's sparkling: {n} Bits!",
    "Wird garantiert zu Pumpkinmon – egal, wie du dich kümmerst. Kommt in deine Sammlung.":
        "Always becomes Pumpkinmon – no matter how you take care of it. Goes into your collection.",
    "Diesen Tausch gibt es gerade nicht.": "That trade isn't available right now.",
    "Deine Sammlung ist voll – lass erst ein Digimon frei.": "Your collection is full – release a Digimon first.",
    "Getauscht: {n}× {item} gegen ein {egg}! Es liegt in deiner Sammlung.":
        "Traded: {n}× {item} for a {egg}! It's in your collection.",
    "{h} Std {m} Min": "{h} h {m} min",
    "{h} Std": "{h} h",
    "{m} Min": "{m} min",
    "Ewigstein": "Everstone",
    "Solange es ihn hält, digitiert es nicht – jederzeit abnehmbar":
        "Won't digivolve while holding it – you can take it off any time",
    "Kleine Sanduhr": "Small Hourglass",
    "Spult das Warten um 1 Std vor (Digitation, Erkunden)": "Skips 1 h of waiting (Digivolution, exploring)",
    "Sanduhr": "Hourglass",
    "Spult das Warten um 3 Std vor (Digitation, Erkunden)": "Skips 3 h of waiting (Digivolution, exploring)",
    "Große Sanduhr": "Big Hourglass",
    "Spult das Warten um 6 Std vor (Digitation, Erkunden)": "Skips 6 h of waiting (Digivolution, exploring)",
    "Löschdiskette": "Erase Disk",
    "Löscht 1 Pflegefehler": "Erases 1 care mistake",
    "{name} hält schon einen Ewigstein.": "{name} is already holding an Everstone.",
    "{name} hält jetzt den Ewigstein und digitiert nicht mehr von selbst. Abnehmen kannst du ihn jederzeit im Rucksack.":
        "{name} is now holding the Everstone and won't digivolve on its own. You can take it off any time in the backpack.",
    "{name} hält keinen Ewigstein.": "{name} isn't holding an Everstone.",
    "Ewigstein abgenommen – {name} kann wieder digitieren. Der Stein ist zurück im Rucksack.":
        "Everstone taken off – {name} can digivolve again. The stone is back in your backpack.",
    "Die Sanduhr spult {h} Std vor – {name} ist gleich zurück vom Erkunden!":
        "The hourglass skips {h} h – {name} will be back from exploring any moment!",
    "Die Sanduhr spult {h} Std vor – {name} ist in {left} zurück.":
        "The hourglass skips {h} h – {name} will be back in {left}.",
    "Die Digitation ist fällig – sie kommt, sobald es zurück ist.":
        "The Digivolution is due – it will happen as soon as it's back.",
    "Digitation in {left}.": "Digivolution in {left}.",
    "fällig – es digitiert, sobald du es aktiv setzt": "due – it will digivolve as soon as you make it active",
    "Für Digimon in der Sammlung gehen nur Sanduhren.": "Only hourglasses work on Digimon in your collection.",
    "Das geht nicht: {name} ruht in der Sammlung, dort steht die Zeit still. Eine Sanduhr geht nur für dein aktives "
    "Digimon oder für Digimon aus der Sammlung, die gerade erkunden.":
        "That doesn't work: {name} is resting in your collection, where time stands still. An hourglass only works on "
        "your active Digimon or on Digimon from your collection that are out exploring.",
    "Ein Ei schlüpft sofort, wenn du es ausbrütest – da gibt es nichts vorzuspulen.":
        "An egg hatches right away when you hatch it – there's nothing to skip.",
    "{name} ist in der Endstufe – da gibt es nichts vorzuspulen.":
        "{name} is at its final stage – there's nothing to skip.",
    "{name} hält den Ewigstein – erst abnehmen, sonst bringt die Sanduhr nichts.":
        "{name} is holding the Everstone – take it off first, or the hourglass won't do anything.",
    "Die Digitation von {name} ist schon fällig – warten lohnt sich hier nicht mehr.":
        "{name}'s Digivolution is already due – there's no waiting left to skip.",
    "im Schlaf fällig – es digitiert nach dem Aufwachen": "due while it sleeps – it will digivolve after waking up",
    "gleich so weit": "about to happen",
    "Die Sanduhr spult {h} Std vor – die Digitation ist {when}!": "The hourglass skips {h} h – the Digivolution is {when}!",
    "Die Sanduhr spult {h} Std vor – Digitation in {left}.": "The hourglass skips {h} h – Digivolution in {left}.",
    "{name} hat keine Pflegefehler – die Diskette bleibt im Rucksack.":
        "{name} has no care mistakes – the disk stays in your backpack.",
    "Löschdiskette: 1 Pflegefehler gelöscht.": "Erase Disk: 1 care mistake erased.",
    "Gelöscht! {name} hat jetzt {n} Pflegefehler in dieser Stufe ({total} insgesamt).":
        "Erased! {name} now has {n} care mistakes in this stage ({total} in total).",
    # Virus-Diskette und Ei-Scherben
    "Virus-Diskette": "Virus Disk",
    "Fügt 1 Pflegefehler hinzu – für Digitationen, die Fehler brauchen":
        "Adds 1 care mistake – for Digivolutions that need mistakes",
    "Ein Ei kann noch keine Pflegefehler haben.": "An egg can't have care mistakes yet.",
    "Noch ein Pflegefehler wäre für {name} zu gefährlich ({total} von höchstens {max}) – die Diskette bleibt im Rucksack.":
        "One more care mistake would be too dangerous for {name} ({total} of at most {max}) – the disk stays in your backpack.",
    "Virus-Diskette: 1 Pflegefehler dazu.": "Virus Disk: 1 care mistake added.",
    "Die Virus-Diskette rauscht … {name} hat jetzt {n} Pflegefehler in dieser Stufe ({total} insgesamt).":
        "The Virus Disk crackles … {name} now has {n} care mistakes in this stage ({total} in total).",
    "Ei-Scherbe {area}": "Egg Shard {area}",
    "{n} Stück ergeben ein Digi-Ei aus {area}": "{n} of them make a Digi-Egg from {area}",
    "{n}× {item}": "{n}× {item}",
    "Ei-Scherben setzt du im Rucksack zusammen.": "You put egg shards together in your backpack.",
    "Das ist keine Ei-Scherbe.": "That's not an egg shard.",
    "Für ein Digi-Ei brauchst du {need} Scherben – du hast erst {have}. Erkunde {area}!":
        "You need {need} shards for a Digi-Egg – you only have {have}. Explore {area}!",
    "Deine Sammlung ist voll – mach erst Platz, dann setz die Scherben zusammen.":
        "Your collection is full – make room first, then put the shards together.",
    "Die {n} Scherben fügen sich zusammen … ein Digi-Ei aus {area}! Es liegt jetzt in deiner Sammlung.":
        "The {n} shards fit together … a Digi-Egg from {area}! It's in your collection now.",

    # ------------------------------------------------------------ events.py – Halloween, Reset-Kristall
    "Halloween": "Halloween",
    "Geister spuken durch die Digital World! Jedes zweite wilde Digimon ist ein Geist – besiegst du ihn, gibt es "
    "doppelte Bits und manchmal ein Gruselbonbon. Beim Erkunden findest du öfter Grusel-Eier.":
        "Ghosts are haunting the Digital World! Every second wild Digimon is a ghost – beat it for double Bits and "
        "sometimes a Spooky Candy. While exploring you find spooky eggs more often.",
    "Ein Geist! Besiegst du ihn, gibt es doppelte Bits.": "A ghost! Beat it for double Bits.",
    "Der Geist hat ein Gruselbonbon fallen lassen!": "The ghost dropped a Spooky Candy!",
    "Der Geist hat ein {egg} fallen lassen!": "The ghost dropped a {egg}!",
    "Reset-Kristall": "Reset Crystal",
    "Dein Digimon wird wieder zu einem zufälligen Digi-Ei": "Your Digimon turns back into a random Digi-Egg",
    "Gruselbonbon": "Spooky Candy",
    "Hunger +1 und Kraft +1 – schaurig lecker": "Hunger +1 and Strength +1 – spookily tasty",
    "{name} nascht ein Gruselbonbon. Hunger +1, Kraft +1 – schaurig lecker!":
        "{name} nibbles a Spooky Candy. Hunger +1, Strength +1 – spookily tasty!",
    "Das ist schon ein Ei.": "That's already an egg.",
    "{name} hält den Ewigstein – erst abnehmen, dann geht der Reset.":
        "{name} is holding the Everstone – take it off first, then the reset works.",
    "Reset-Kristall: {name} ist wieder ein Digi-Ei.": "Reset Crystal: {name} is a Digi-Egg again.",
    "Der Reset-Kristall leuchtet … {name} wird wieder zu einem Digi-Ei! Was wohl diesmal daraus schlüpft?":
        "The Reset Crystal glows … {name} turns back into a Digi-Egg! What will hatch this time?",

    # ------------------------------------------------------------ themes.py – V-Pet-Designs
    "Klassisch": "Classic",
    "Original Grau": "Original Grey",
    "Agumon Orange": "Agumon Orange",
    "Gabumon Blau": "Gabumon Blue",
    "Biyomon Pink": "Biyomon Pink",
    "Palmon Grün": "Palmon Green",
    "Nachtmodus": "Night Mode",
    "Gold": "Gold",
    "Dieses Design gibt es nicht.": "That design doesn't exist.",
    "Das Design „{name}“ hast du schon.": "You already have the “{name}” design.",
    "Dafür brauchst du {n}× {item} – du hast {have}.": "You need {n}× {item} for that – you have {have}.",
    "Neues Design: {name}! Es ist gleich aktiv.": "New design: {name}! It's active right away.",
    "Das Design „{name}“ musst du erst kaufen.": "You have to buy the “{name}” design first.",
    "Das Design „{name}“ gibt es nur während des Events.": "The “{name}” design is only available during the event.",
    "Design gewechselt: {name}.": "Design changed: {name}.",

    # ------------------------------------------------------------ events.py – Story & Belohnungen (Event-Tab)
    "Jedes Jahr Ende Oktober wird es in der Digital World merkwürdig still. Nebel kriecht aus der Dunklen Zone "
    "herauf, und überall leuchten Kürbislaternen – an Orten, an denen nie jemand welche aufgestellt hat.":
        "Every year at the end of October, the Digital World grows strangely quiet. Fog creeps up from the Dark Zone, "
        "and pumpkin lanterns glow everywhere – in places where nobody ever put them.",
    "Dann feiern die Geister-Digimon ihr Fest: Bakemon schweben durch den Urwald, Wizardmon lässt Irrlichter "
    "tanzen, und irgendwo im Nebel kichert ein Pumpkinmon. Wer sich ihnen stellt, wird belohnt – Geister lassen "
    "doppelt so viele Bits fallen und manchmal ein Gruselbonbon.":
        "Then the ghost Digimon hold their festival: Bakemon drift through the jungle, Wizardmon makes will-o'-the-wisps "
        "dance, and somewhere in the fog a Pumpkinmon giggles. Whoever faces them is rewarded – ghosts drop twice as "
        "many Bits and sometimes a Spooky Candy.",
    "Und ganz selten findet ein Tamer ein Ei, das leise flackert wie eine Kerze. Was daraus schlüpft, ist kein "
    "Geheimnis: Es wird immer ein Pumpkinmon. Aber beeil dich – am 2. November verzieht sich der Nebel, und mit "
    "ihm verschwinden die Geister bis zum nächsten Jahr.":
        "And very rarely, a Tamer finds an egg that flickers softly like a candle. What hatches from it is no secret: "
        "it always becomes a Pumpkinmon. But hurry – on November 2 the fog lifts, and the ghosts vanish with it until "
        "next year.",
    "Geister besiegen: doppelte Bits": "Defeat ghosts: double Bits",
    "Geister besiegen: {p} % Chance auf ein {item}": "Defeat ghosts: {p}% chance of a {item}",
    "Geister besiegen: {p} % Chance auf das {egg}": "Defeat ghosts: {p}% chance of the {egg}",
    "Erkunden: {p} % Chance pro Ausflug auf ein {item}": "Exploring: {p}% chance per trip of a {item}",
    "Erkunden: {p} % Chance pro Ausflug auf ein Extra-Ei – die Hälfte davon ist das {egg}":
        "Exploring: {p}% chance per trip of an extra egg – half of them are the {egg}",
    "Erkunden: {p} % Chance pro Ausflug auf ein Extra-Ei": "Exploring: {p}% chance per trip of an extra egg",
    "{item} kaufen: {n} Bits": "Buy {item}: {n} Bits",
    "{n}× {item} → {egg}": "{n}× {item} → {egg}",
    "{n}× {item} → Design „{name}“": "{n}× {item} → “{name}” design",
    "{n}× {item} → Deko „{name}“ (während des Events gratis an)":
        "{n}× {item} → “{name}” decoration (on for free during the event)",
    "{item} verkaufen: {n} Bits pro Stück (im Rucksack)": "Sell {item}: {n} Bits each (in your bag)",

    # ------------------------------------------------------------ friends.py – Freundescodes
    "{name} ist jetzt dein Freund!": "{name} is now your friend!",
    "{name} ist nicht mehr dein Freund.": "{name} is no longer your friend.",
    "Diesen Freundescode gibt es nicht.": "That friend code doesn't exist.",
    "Das ist dein eigener Freundescode.": "That's your own friend code.",
    "{name} ist schon dein Freund.": "{name} is already your friend.",
    "Mehr als {n} Freunde gehen nicht.": "You can't have more than {n} friends.",
    "{name} ist nicht dein Freund.": "{name} isn't your friend.",
    "Das geht nur mit Freunden. Tauscht eure Freundescodes aus (Einstellungen → Freunde).":
        "That only works with friends. Swap your friend codes (Settings → Friends).",
    "Neuer Freundescode – der alte gilt nicht mehr.": "New friend code – the old one no longer works.",
    "kann gerade nicht kämpfen": "can't battle right now",
    "{name} kann gerade nicht kämpfen.": "{name} can't battle right now.",

    # ------------------------------------------------------------ shop.py – Verkaufen im Rucksack
    "Das kann man nicht verkaufen.": "That can't be sold.",
    "Davon hast du nichts im Rucksack.": "You don't have any of that in your bag.",
    "Du kannst 1 bis {n} Stück verkaufen.": "You can sell 1 to {n}.",
    "Verkauft: {item} für {bits} Bits.": "Sold: {item} for {bits} Bits.",
    "Verkauft: {n}× {item} für {bits} Bits.": "Sold: {n}× {item} for {bits} Bits.",

    # ------------------------------------------------------------ decor.py – Deko
    "Fledermäuse": "Bats",
    "Flattern oben durch die Symbolleiste": "Flutter through the top bar",
    "Sternenfunkeln": "Twinkling Stars",
    "Kleine Sterne funkeln oben im Display": "Little stars twinkle at the top of the screen",
    "Seifenblasen": "Bubbles",
    "Blasen steigen am Rand des Displays auf": "Bubbles rise along the edges of the screen",
    "Herzchen": "Little Hearts",
    "Ab und zu steigt ein Herz über deinem Digimon auf": "Now and then a heart rises above your Digimon",
    "Schneefall": "Snowfall",
    "Schneeflocken rieseln durchs Display": "Snowflakes drift across the screen",
    "Diese Deko gibt es nicht.": "That decoration doesn't exist.",
    "Die Deko „{name}“ hast du schon.": "You already have the “{name}” decoration.",
    "Die Deko „{name}“ gibt es nur während des Events.": "The “{name}” decoration is only available during the event.",
    "Neue Deko: {name}! Sie ist gleich an.": "New decoration: {name}! It's switched on.",
    "Die Deko „{name}“ musst du erst kaufen.": "You have to buy the “{name}” decoration first.",
    "{name}: an.": "{name}: on.",
    "{name}: aus.": "{name}: off.",

    # ------------------------------------------------------------ progress.py – Erfolge
    "Hallo, Welt!": "Hello, World!",
    "Lass ein Digi-Ei schlüpfen.": "Hatch a Digi-Egg.",
    "Großgeworden": "All Grown Up",
    "Zieh ein Digimon bis zum Rookie groß.": "Raise a Digimon to Rookie.",
    "Champion!": "Champion!",
    "Erreiche die Champion-Stufe.": "Reach the Champion stage.",
    "Ultra-Kraft": "Ultimate Power",
    "Erreiche die Ultra-Stufe.": "Reach the Ultimate stage.",
    "Mega-Digitation": "Mega Digivolution",
    "Erreiche die Mega-Stufe.": "Reach the Mega stage.",
    "Armor-Held": "Armor Hero",
    "Digitiere mit einem Armor-Ei.": "Digivolve with an Armor Egg.",
    "Alle Wappen": "Every Crest",
    "Sammle alle Armor-Formen.": "Collect all Armor forms.",
    "Sammler": "Collector",
    "Sammle 10 verschiedene Digimon.": "Collect 10 different Digimon.",
    "Eifriger Sammler": "Keen Collector",
    "Sammle 25 verschiedene Digimon.": "Collect 25 different Digimon.",
    "Digidex-Forscher": "Digidex Researcher",
    "Sammle 50 verschiedene Digimon.": "Collect 50 different Digimon.",
    "Digidex-Profi": "Digidex Pro",
    "Sammle 100 verschiedene Digimon.": "Collect 100 different Digimon.",
    "Digidex-Legende": "Digidex Legend",
    "Sammle 250 verschiedene Digimon.": "Collect 250 different Digimon.",
    "Kämpfer": "Fighter",
    "Gewinne 10 Kämpfe.": "Win 10 battles.",
    "Veteran": "Veteran",
    "Gewinne 50 Kämpfe.": "Win 50 battles.",
    "Champion der Digital World": "Champion of the Digital World",
    "Gewinne 200 Kämpfe.": "Win 200 battles.",
    "Freundschaftskampf": "Friendly Match",
    "Gewinne einen Kampf gegen einen Freund.": "Win a battle against a friend.",
    "Rivale": "Rival",
    "Gewinne 10 Kämpfe gegen Freunde.": "Win 10 battles against friends.",
    "Entdecker": "Explorer",
    "Komm 10-mal vom Erkunden zurück.": "Come back from exploring 10 times.",
    "Weltenbummler": "Globetrotter",
    "Komm 50-mal vom Erkunden zurück.": "Come back from exploring 50 times.",
    "Zwei werden eins": "Two Become One",
    "Schaffe eine Jogress.": "Complete a Jogress.",
    "Geisterjäger": "Ghost Hunter",
    "Besiege 5 Geister während Halloween.": "Beat 5 ghosts during Halloween.",
    "Kürbiskopf": "Pumpkin Head",
    "Zieh ein Pumpkinmon groß.": "Raise a Pumpkinmon.",

    # ------------------------------------------------------------ starter.py – Fragenkatalog beim ersten Start
    "Beantworte zuerst die Fragen – dann bekommst du dein erstes Digi-Ei.":
        "Answer the questions first – then you'll get your first Digi-Egg.",
    "Den Fragenkatalog hast du schon beantwortet.": "You've already answered the questions.",
    "Bitte beantworte alle Fragen.": "Please answer all the questions.",
    "mutig": "brave",
    "Du stellst dich jeder Herausforderung und gehst voran, wenn andere zögern. Manchmal stürmst du los, bevor du "
    "nachdenkst – aber wenn es brenzlig wird, ist auf dich Verlass.":
        "You face every challenge and lead the way when others hesitate. Sometimes you charge ahead before you "
        "think – but when things get tough, everyone can count on you.",
    "ruhig": "calm",
    "Du bleibst gelassen, auch wenn es stürmt. Du hörst gut zu und denkst nach, bevor du handelst. Deine Freunde "
    "schätzen dich als Ruhepol.":
        "You stay cool even when things get stormy. You listen well and think before you act. Your friends "
        "love how calm you make them feel.",
    "sanft": "gentle",
    "Du kümmerst dich gern um andere und liebst die Natur. Mit Geduld und einem großen Herzen bringst du alles "
    "zum Wachsen.":
        "You love taking care of others and you love nature. With patience and a big heart you help everything grow.",
    "schlau": "clever",
    "Du willst wissen, wie die Dinge funktionieren, und findest für jedes Problem eine Lösung. Rätsel, Technik "
    "und neue Ideen sind genau dein Ding.":
        "You want to know how things work, and you find a solution for every problem. Puzzles, gadgets and new "
        "ideas are just your thing.",
    "geheimnisvoll": "mysterious",
    "Du gehst deinen eigenen Weg, liebst Überraschungen und bist ein kleines bisschen frech. Nicht jeder sieht "
    "gleich, was alles in dir steckt.":
        "You go your own way, you love surprises and you're a tiny bit cheeky. Not everyone sees right away "
        "everything you're capable of.",
    "fröhlich": "cheerful",
    "Mit deiner guten Laune steckst du alle an, und neue Freunde findest du überall. Mit dir wird es nie "
    "langweilig!":
        "Your good mood is contagious, and you make new friends everywhere. Things are never boring with you around!",
    "Ein Freund ist traurig. Was machst du?": "A friend is sad. What do you do?",
    "Ich bringe ihn zum Lachen.": "I make them laugh.",
    "Ich höre ihm einfach zu.": "I just listen to them.",
    "Ich finde heraus, was los ist, und löse das Problem.": "I find out what's wrong and solve the problem.",
    "Ich nehme ihn mit auf ein Abenteuer.": "I take them along on an adventure.",
    "Im Wald findest du eine dunkle Höhle. Was tust du?": "You find a dark cave in the forest. What do you do?",
    "Rein da, sofort!": "Go right in!",
    "Erst mal baue ich mir eine Taschenlampe.": "First I build myself a flashlight.",
    "Ich warte versteckt, ob etwas herauskommt.": "I hide and wait to see if something comes out.",
    "Lieber nicht – draußen ist es so schön.": "Better not – it's so nice out here.",
    "Wo bist du am liebsten?": "Where do you like to be most?",
    "In einer Arena, wo etwas los ist": "In an arena where there's lots of action",
    "An einem ruhigen Strand": "On a quiet beach",
    "In einem Garten voller Blumen": "In a garden full of flowers",
    "In einer Werkstatt voller Geräte": "In a workshop full of gadgets",
    "Welche Tageszeit magst du am liebsten?": "Which time of day do you like best?",
    "Den frühen Morgen, wenn alles erwacht": "Early morning, when everything wakes up",
    "Den Mittag, wenn die Sonne brennt": "Noon, when the sun is blazing",
    "Den Abend am Wasser": "Evening by the water",
    "Die Nacht": "Night",
    "Bei einem Spiel liegst du weit hinten. Was denkst du?": "You're far behind in a game. What do you think?",
    "Jetzt erst recht!": "Now more than ever!",
    "Ich brauche eine bessere Taktik.": "I need a better strategy.",
    "Egal – Hauptsache, es macht Spaß!": "Whatever – the main thing is having fun!",
    "Ich habe noch einen Trick im Ärmel …": "I still have a trick up my sleeve …",
    "Jemand verrät dir ein Geheimnis. Was machst du?": "Someone tells you a secret. What do you do?",
    "Ich behalte es für immer für mich.": "I keep it to myself forever.",
    "Ich sammle Geheimnisse. Das ist schon mein drittes heute.": "I collect secrets. That's my third one today.",
    "Ich überlege, wie ich helfen kann.": "I think about how I can help.",
    "Ich platze fast – aber ich halte durch!": "I'm about to burst – but I hold on!",
    "Du bekommst ein Geschenk. Was soll drin sein?": "You get a present. What should be inside?",
    "Ein Bausatz für einen Roboter": "A kit to build a robot",
    "Samen für eine ganz seltene Pflanze": "Seeds for a really rare plant",
    "Eine Karte zu einem versteckten Schatz": "A map to a hidden treasure",
    "Karten für ein großes Fest mit Freunden": "Tickets to a big party with friends",
    "Wie würden dich deine Freunde beschreiben?": "How would your friends describe you?",
    "Mutig und ehrlich": "Brave and honest",
    "Entspannt und zuverlässig": "Relaxed and reliable",
    "Lieb und geduldig": "Kind and patient",
    "Witzig und ein bisschen laut": "Funny and a bit loud",
    "Schwer zu durchschauen": "Hard to figure out",
    "Ein Gewitter zieht auf. Was machst du?": "A thunderstorm is coming. What do you do?",
    "Ich beobachte die Blitze. Wie funktionieren die eigentlich?": "I watch the lightning. How does it actually work?",
    "Ich kuschle mich ein und lese ein Buch.": "I snuggle up and read a book.",
    "Ich renne lachend durch den Regen!": "I run through the rain, laughing!",
    "Ich mag die Stimmung – ein bisschen unheimlich, ein bisschen schön.":
        "I like the mood – a little spooky, a little beautiful.",
    "Welches Tier passt am besten zu dir?": "Which animal suits you best?",
    "Ein Löwe": "A lion",
    "Ein Delfin": "A dolphin",
    "Eine Eule": "An owl",
    "Ein Hase": "A rabbit",
    "Du hast einen ganzen Tag frei. Was machst du?": "You have a whole day off. What do you do?",
    "Etwas Neues ausprobieren – gern auch etwas Wildes": "Try something new – something wild is fine too",
    "Ausschlafen und den Tag genießen": "Sleep in and enjoy the day",
    "Etwas bauen oder tüfteln": "Build or tinker with something",
    "Mit allen Freunden etwas unternehmen": "Do something with all my friends",
    "Ihr spielt Theater. Welche Rolle willst du?": "You're putting on a play. Which role do you want?",
    "Den Helden, der alle rettet": "The hero who saves everyone",
    "Den geheimnisvollen Fremden": "The mysterious stranger",
    "Den klugen Erfinder": "The clever inventor",
    "Die gute Fee, die allen hilft": "The good fairy who helps everyone",
    "Jemand ist gemein zu einem kleineren Kind. Was tust du?": "Someone is being mean to a younger kid. What do you do?",
    "Ich gehe sofort dazwischen.": "I step in right away.",
    "Ich tröste das Kind.": "I comfort the kid.",
    "Ich hole Hilfe und erkläre ruhig, was passiert ist.": "I get help and calmly explain what happened.",
    "Ich spiele dem Fiesling später einen Streich.": "I play a prank on the bully later.",
    "Was ist dir am wichtigsten?": "What matters most to you?",
    "Stärker werden": "Getting stronger",
    "Frieden und Ruhe": "Peace and quiet",
    "Neues lernen": "Learning new things",
    "Spaß mit Freunden": "Having fun with friends",
    "Frei sein": "Being free",
}

# Web-Push
EN.update({
    "{name} ist gestorben": "{name} has died",
    "Das Schutz-Totem hat dein Digimon gerettet!": "The Guardian Totem saved your Digimon!",
    "Das Ei ist geschlüpft!": "The egg has hatched!",
    "Es ist ein {name}!": "It's a {name}!",
    "Digitation!": "Digivolution!",
    "Gib ihm schnell Medizin.": "Give it medicine quickly.",
    "{name} ist krank!": "{name} is sick!",
    "{name} ruft dich!": "{name} is calling you!",
    "Ungültige Push-Anmeldung.": "Invalid push subscription.",
    "Du kannst höchstens 8 Geräte für Mitteilungen anmelden.": "You can register up to 8 devices for notifications.",
    "{name} wartet im Kühlschrank auf dich.": "{name} is waiting in the fridge for you.",
    "Dein Digimon ist jetzt {name}.": "Your Digimon is now {name}.",
    "Schau nach deinem Digimon.": "Check on your Digimon.",
    "{name} ist zurück vom Erkunden!": "{name} is back from exploring!",
    "Deine Funde warten im Spiel.": "Your finds are waiting in the game.",
    "Ein Sammlungs-Digimon ist zurück!": "A Digimon from your collection is back!",
    "Push-Mitteilungen sind auf diesem Server nicht verfügbar.": "Push notifications are not available on this server.",
    "Aktiviere zuerst die Mitteilungen auf diesem Gerät.": "Enable notifications on this device first.",
    "Warte 30 Sekunden vor der nächsten Test-Mitteilung.": "Wait 30 seconds before sending another test notification.",
    "Die Mitteilung kam nicht an. Schalte die Benachrichtigungen aus und wieder ein.": "The notification could not be delivered. Turn notifications off and on again.",
    "Benachrichtigungen sind an": "Notifications are on",
    "So sieht es aus, wenn dein Digimon dich ruft.": "This is what it looks like when your Digimon calls you."
})

# Echte Jogress
EN.update({
    "Bitte bestätige die neue Fusionsregel. Lade das Spiel bei Bedarf neu.": "Please confirm the new fusion rule. Reload the game if needed.",
    "Wähle eines der beiden Digimon als Grundlage.": "Choose one of the two Digimon as the base.",
    "Jogress! Beide Digimon sind jetzt {name}. Jeder behält seine eigene Fusion.": "Jogress! Both Digimon are now {name}. Each player keeps their own fusion."
})
