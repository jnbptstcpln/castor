# Castor

> Créé le 12 juillet 2020 par Jean-Baptiste Caplan

Castor est une bibliothèque permettant entre autres l'éxécution de processus composés de noeuds. Ces processus sont décrits
par des fichiers JSON généré par l'éditeur de la plateforme Pollux. La bibliothèque Castor est conçue pour communiquer avec
la plateforme web Pollux pour proposer un controle actif des processus ainsi que des possiblités de téléchargé de nouveaux
composants ou bien déployé du code automatiquement.

## Installation

Afin de pouvoir utiliser Castor il est nécessaire de procéder à l'installation de ses différentes dépendances.
Pour cela, en étant situé dans le répertoire principal de Castor, vous pouvez utiliser la commande suivante :

```
    pip install -r requirements.txt
```

## Utilisation

### Exécution d'un processus

A l'aide du fichier `standalone.py` il est possible d'exécuter en local n'importe quel processus disponible sous forme 
d'un fichier JSON.
Pour exécuter le processus, il suffit de lancer le script de la façon suivante :
```
    python3 standalone.py --flow flow.json
``` 
Avec `flow.json` le fichier contenant la description de votre processus au format JSON.

Il est aussi possible de définir l'environnment d'exécution du processus à l'aide de l'argument `--environment` en lui 
transmettant une description de l'environnement au format JSON :
```
    python3 standalone.py --flow flow.json --environment '{"first_name": "Jean-Baptiste", "last_name": "Caplan"}'
``` 

### Exécution du daemon

Afin de pouvoir bénéficier pleinement de l'intégration de Castor avec la plateforme de gestion Pollux, il est possible de 
lancer un (ou bien plusieurs) daemon qui seront directement pilotés par Pollux.

Avant de procéder au lancement d'un daemon, il faut préalablement vérifier la configuration du daemon. Pour se faire, vérifier 
la présence du fichier `castor/config.ini`, si il n'est pas encore créé vous pouvez tout simplement dupliquer le fichier `castor/config.ini.sample`.

Le contenu de `castor/config.ini` devrait ressembler à ceci :
```ini
[pollux]
# Domaine sur lequel une instance de Pollux est accessible
host=https://pollux-instance.domain
# Clé de l'API de Pollux
key=XXXXXXXXXXX

[daemon]
# Nom de la machine hôte
machine_name="My machine"
# Nombre maximal d'exécution simultannées
concurent_execution_limit=10
# Le daemon vérifiera la présence de potentielles mise à jour des modules/libraries avant l'exécution des processus
auto_reload=true
```

Une fois la configuration en place, vous pouvez procéder au lancement du daemon avec la commande :

```
    python3 daemon.py --name DaemonName --domain default
```

Avec les paramètres `--name` et `--domain` correspondant respectivement à la dénomination du daemon qui sera affichée sur 
l'interface de gestion de Pollux et au domaine d'exécution dans lequel travaille ce daemon qui déterminera quel type de 
processus ce dernier sera en mesure d'exécuter (Seul les processus ayant le même domain d'exécution pourront être exécuter 
par ce daemon, cela permet d'avoir des daemons "spécialiste" ou encore d'avoir un domaine dédié au développement et un 
autre à la production).

Il est aussi possible de spécifier un autre fichier de configuration que celui utilser par défaut (`castor/config.ini`) :
```
    python3 daemon.py --name DaemonName --domain default --config config.ini
``` 