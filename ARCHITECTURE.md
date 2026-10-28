# Arkitekturmotivering & Systemdokumentation

**Författare:** Issam

**Datum:** 2026-10-28

**Kurs:** Automation med Ansible

## 1. Systemöversikt & Verktygsval

Jag använder tre Ubuntu-servrar i Hyper-V: controlnode, issamnode1 och
issamnode2. Controlnode kör Ansible och administrerar de andra två via SSH.
Noderna nås med sina egna mDNS-namn, issamnode1.local och issamnode2.local.
De namnen valdes för att undvika krockar med andra elevers servrar.

Jag valde Ansible eftersom vi har få noder och ett ganska statiskt skolprojekt.
SSH finns redan och jag kan starta en körning när jag behöver göra en ändring
eller kontroll. Det behövs ingen separat Ansible-agent på varje nod.
Puppet, som jag jämförde med i Lab 11, ger återkommande driftkorrigering men
kräver också agenter, certifikat och en central server att förvalta. För våra
behov tycker jag att Ansible räcker bra.

Den färdiga applikationen från Lab 10 har Nginx, Gunicorn och Flask på node1.
Nginx tar emot HTTP på port 80 och skickar anropet till Gunicorn på
127.0.0.1:8000. Flask läser sedan meddelandet från MariaDB på node2, port 3306.
Controlnode behövs för administrationen, men ingår inte i varje webbanrop.

Repot är uppdelat per labb så att utvecklingen och redovisningen finns kvar.
Lab 5 och 6 använder common och webserver. Lab 10 ligger i labb-10/lab10
och använder rollerna database och webbapp. Roller samlar uppgifter,
mallar och handlers för samma ansvar. Variabler ligger separat i group_vars,
vilket gör det lättare att ändra inställningar utan att skriva om uppgifterna.

## 2. Säkerhet & Hemligheter

Databaslösenordet ligger Vault-krypterat i group_vars/all/vault.yml.
Vault-lösenordet hålls utanför Git och anges vid körning med --ask-vault-pass.
.gitignore undantar lösenordsfiler, privata SSH-nycklar, loggar och retry-filer.
Krypteringen skyddar innehållet i Git, medan no_log hindrar känsliga
uppgifter från att skrivas ut under körningen.
[Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html)

Webbappen behöver kunna läsa lösenordet när den körs. Därför skapas
/etc/labbapp/config.json på node1 med ägaren root, gruppen webapp och
rättigheten 0640. Katalogen har 0750. Uppgiften använder no_log och
diff: false. Vault skyddar alltså källmaterialet, och filbehörigheter
begränsar åtkomsten till den dekrypterade konfigurationen.

Ansible ansluter som issam och använder become för uppgifter som kräver
sudo, exempelvis paketinstallation och tjänstekonfiguration. I Lab 4
skapades devops_admin med en egen publik SSH-nyckel på noderna. Den privata
nyckeln stannar på kontrollnoden. Nyckeln skapades utan lösenfras i
skolövningen; starkare nyckelskydd behöver övervägas i en annan miljö.

Själva webbappen kör som tjänstekontot webapp. Databaskontot labbapp får
SELECT i labbdb och tillåts från webbserverns IP. MariaDB binds till
databasnodens adress och Gunicorn lyssnar bara lokalt på node1.
Webbtrafiken använder HTTP i labbnätet. TLS och en genomarbetad
brandväggspolicy är vidare arbete för en produktionsmiljö.

## 3. Skalbarhet & Dynamik

Det statiska inventoryt passar våra två noder. Fler servrar kan läggas till
i rätt grupp och få samma roller. En extra webbserver behöver också tillåtas
som databasklient; den nuvarande variabeln web_host anger en enda IP-adress.
Större utbyggnad kräver därför även anpassade databasbehörigheter och
eventuellt lastbalansering.

I Lab 9 läser ett Python-skript servers.json och lämnar inventoryt till
Ansible som JSON. Det är en filbaserad lösning, där jag underhåller
serverlistan själv. Skriptet är flyttbart och söker nu datafilen bredvid
sig självt. En framtida koppling till en molntjänst eller CMDB skulle kunna
hämta serverlistan automatiskt, men det finns ingen sådan API-koppling här.

Jinja2-mallar använder variabler som db_host, db_port och db_name.
Samma roller kan därför återanvändas med andra värden. För separata Dev-,
Test- och Produktionsmiljöer skulle jag lägga miljöernas variabler och
Vault-data vid respektive inventory och skilja dem från gemensamma standardvärden.
Här finns en skolmiljö; de tre miljöerna är ett möjligt nästa steg.

## 4. Drift, Optimering & Återhämtning

Idempotens betyder att samma önskade tillstånd kan tillämpas igen utan
onödiga ändringar. Paket ska finnas och tjänster ska vara igång. När det
redan stämmer behövs ingen ändring. Lab 10 verifierades med changed=0,
failed=0 och unreachable=0 på båda noderna vid omkörningen.

Databastabellen skapas med IF NOT EXISTS och testmeddelandet hanteras med
en upsert. Uppgiften bedömer ändring utifrån påverkade rader.
Handlers startar om webbappen eller MariaDB, eller laddar om Nginx,
när den uppgift som meddelar dem faktiskt ändras. Det minskar onödiga
omstarter. Paketlistorna återanvänds i upp till en timme med cache_valid_time.

Jag börjar felsökningen med inventory och anslutning, sedan syntax och den
uppgift som felmeddelandet pekar på. --check kan användas som prognos,
men ersätter inte en riktig körning. Vissa kontroller och SQL-uppgifter
kan hoppas över i checkläge. Nginx-konfigurationen kontrolleras med nginx -t.
Därefter kontrolleras HTTP-svaret och meddelandet från databasen.
[Checkläge](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

Lab 10 har dokumenterade tjänstetester. I Lab 12 kontrollerades dessutom
alla sju huvudsakliga playbooks lokalt med --syntax-check. De kontrollerna
visar kodens struktur och modulupplösning; tjänstetesterna visar att
applikationen faktiskt svarade och läste data.

Om node1 slutar fungera försvinner webbsidan. Om node2 försvinner kan Flask
inte läsa meddelandet. En omkörning kan återskapa konfiguration, men
förlorad databasdata behöver en backup. Automatisk databassäkerhetskopiering
och hög tillgänglighet är inte implementerade i den här skolmiljön.
