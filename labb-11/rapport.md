# Lab 11 – Ansible och Puppet

I det här labbet jämförde jag Ansible och Puppet. Utgick från Nginx-exemplen
i uppgiften och läste Dag 7-PDF:en. Försökte koppla skillnaderna till det
vi redan gjort med controlnode och våra två noder.

## Push och pull

Med Ansible startar jag körningen från controlnode. Den tar kontakt med
noderna via SSH och kör uppgifterna där. Det är push, som vi har använt
i tidigare labbar. Behöver ingen separat Ansible-agent på varje nod.
[Ansible – anslutningar](https://docs.ansible.com/projects/ansible/latest/user_guide/connection_details.html)

Puppet använder normalt pull. Där finns en agent på varje nod som hämtar
en katalog från den centrala servern. Katalogen byggs från koden och
nodens facts och beskriver hur noden ska vara konfigurerad.
[Puppet – arkitektur](https://help.puppet.com/core/9/Content/PuppetCore/architecture.htm)

Om någon ändrar en inställning på node1 som vår Ansible-playbook hanterar
behövs en ny körning för att rätta tillbaka den. När körningen behöver
ändra värdet får uppgiften changed. Körningen kan startas manuellt eller
schemaläggas.

Puppets agent kör återkommande i bakgrunden. Den kan upptäcka ändringen
vid nästa kontroll och återställa det värde som koden anger. Det är
driftkorrigering och gäller det som Puppet hanterar.
[Puppet – agenten](https://help.puppet.com/pe/current/topics/the_puppet_agent.htm)

## Ordningen i koden

### Ansible

De två uppgifterna i Ansible-exemplet ser ut så här:

```yaml
- name: Installera Nginx
  ansible.builtin.package:
    name: nginx
    state: present

- name: Skapa konfigurationsfil
  ansible.builtin.copy:
    content: "server { listen 80; }"
    dest: /etc/nginx/sites-available/default
```

Ansible kör normalt tasks uppifrån och ned. Först installeras Nginx och
sedan skrivs konfigurationsfilen. Om jag byter ordning på en ny server
kan filuppgiften misslyckas. Vi har då inte installerat Nginx ännu och
mappen där filen ska sparas kan saknas.
[Ansible – körordning](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html)

### Puppet

Motsvarande exempel i Puppet:

```puppet
package { 'nginx':
  ensure => installed,
}

file { '/etc/nginx/sites-available/default':
  ensure  => file,
  content => 'server { listen 80; }',
  require => Package['nginx'],
}
```

Puppet bygger en beroendegraf över resurserna. Här kräver filen paketet
nginx genom require. Paketet hanteras därför först även om filblocket
står ovanför paketblocket.

Det var den delen jag läste om i Dag 7-PDF:en. Ordningen mellan de här
blocken styrs av beroendet. För resurser utan styrande beroenden kan
ordningen i filen fortfarande användas.
[Puppet – beroenden och ordning](https://help.puppet.com/core/current/content/puppetcore/lang_relationships.htm)

Båda exemplen beskriver önskat tillstånd. Ansible kör sina tasks i ordning,
men behöver bara ändra det som inte redan är rätt. Det kunde vi se med
changed=0 vid omkörningen i Lab 10.

## Jämförelsetabell

| Område | Ansible | Puppet |
| --- | --- | --- |
| Arkitektur | Vanligen push från controlnode, via SSH i vår miljö. | Vanligen pull med central server och agenter på noderna. |
| Språk/syntax | YAML med tasks och moduler. | Eget deklarativt språk, [Puppet DSL](https://help.puppet.com/core/current/content/puppetcore/puppet_language.htm), med resurser och beroenden. |
| Körordning | Tasks körs normalt i skriven ordning. | Beroenden kan styra ordningen mellan resurserna. |
| Fördelar | Enkelt att komma igång när SSH finns. Lätt att följa körningen stegvis. | Återkommande driftkorrigering och tydliga beroenden. |
| Nackdelar | Drift rättas först när en ny körning startas, manuellt eller automatiskt. | Agenter, central server och certifikat behöver installeras och underhållas. |

Med varje ny Puppet-nod behöver agent och certifikat hanteras. Det kan
automatiseras, men är ändå fler delar att hålla ordning på. Kostnaden
här handlar främst om arbetstid och underhåll.

## Mitt val och min reflektion

Jag skulle välja Ansible. Vi har inte många noder och det är inte en
växande eller dynamisk miljö som ständigt ändras. Vi behöver inte hela
tiden lägga till och ta bort noder. Det är ett statiskt skolprojekt i
en kurs.

Vi har redan SSH och kan köra våra playbooks när vi behöver göra en
ändring eller kontroll. För just våra projekt tycker jag att det räcker bra.
Puppets återkommande kontroller är en fördel, men innebär också mer
att installera och underhålla.

Ansible kan också användas med dynamiska inventories. Mitt val handlar
om vad vi behöver i det här projektet.
[Ansible – dynamiskt inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_dynamic_inventory.html)

Under genomgången gick jag själv till Dag 7-PDF:en och läste om hur Puppet
bygger beroendegrafen. Det hjälpte mig att förstå varför en resurs längre
ned i filen kan behöva hanteras först. Kopplade det sedan till vår egen
miljö och det vi gjort i tidigare labbar.

## Kursmaterial

- Examinerande Laborationer, Lab 11.
- Dag 7 Alternative CM Tools & Jämförande analys samt Kubernetes, särskilt sidan 7 om Puppet.
