"""
    :version 0.1
"""
from castor.flow.component import Component


class Log(Component):
    def func(self, value):
        """
        :description Permet d'ajouter l'entrée aux logs du processus
        :size 0
        :param value:*:Valeur à ajouter aux logs
        :setting template:string:Mise en forme du message (par défaut <{value}>)
        """
        self.flow.log(self.settings.get("template", "{value}").format(value=value))


class Sleep(Component):
    def func(self, value):
        """
        :description Permet d'ajouter un temps de pause dans l'exécution
        :size 0
        :param value:*:Valeur à transmettre
        :return value:*:Valeur transmise après la pause
        :setting duration:float:Durée de la pause en seconde
        """
        import time
        time.sleep(float(self.settings.get("duration", "1").replace(',', '.')))
        return value


class Exit(Component):
    def func(self, value):
        """
        :description Permet de terminer l'exécution du processus tout en ajoutant aux logs la valeur passée en paramètre
        :size 0
        :param value:*:Valeur qui sera ajoutée aux logs
        """
        self.flow.log("Exit : \"{}\"".format(value))
        self.exit()

class Restart(Component):
    def func(self, value):
        """
        :description Permet de rédémarrer le processus
        :size 0
        :param value:*:Valeur transmise pour activer le bloc
        :setting environment:string:Définit si l'environnement doit être conservé ou non
        :setting message:string:Message à ajouter aux logs (possiblité d'afficher l'entrée avec <{value}>)
        """
        keep_environment = False if self.settings.get("environment", "reset") == "reset" else True

        template = self.settings.get("message", None)
        message = None
        if template is not None:
            message = template.format(value=value)

        self.restart(keep_environment, message)

class Format1(Component):
    def func(self, str1):
        """
        :description Permet de formatter la chaine de caractères passée en entrée
        :size 0
        :param str1:string:Chaine de caractères
        :return result:string:Résultat du formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{str1}>)
        """
        return self.settings.get("template", "{str1}").format(str1=str1)

class Format2(Component):
    def func(self, str1, str2):
        """
        :description Permet de formatter les chaines de caractères passées en entrées
        :size 0
        :param str1:string:Première chaine de caractères
        :param str2:string:Seconde chaine de caractères
        :return result:string:Résultat du formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{str1}{str2}>)
        """
        return self.settings.get("template", "{str1}{str2}").format(str1=str1, str2=str2)


class Format3(Component):
    def func(self, str1, str2, str3):
        """
        :description Permet de formatter les chaines de caractères passées en entrées
        :size 0
        :param str1:string:Première chaine de caractères
        :param str2:string:Seconde chaine de caractères
        :param str3:string:Troisième chaine de caractères
        :return result:string:Résultat de formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{str1}{str2}{str2}>)
        """
        return self.settings.get("template", "{str1}{str2}{str3}").format(str1=str1, str2=str2, str3=str3)


class Get(Component):
    def func(self):
        """
        :description Permet de récupérer une valeur stockée dans l'environnement du processus
        :size 0
        :setting variable_name:string:Nom de la variable à récupérer
        :return value:*:Valeur récupérée
        """
        return self.environment.get(self.settings.get("variable_name"))


class Set(Component):
    def func(self, value):
        """
        :description Permet de stocker une valeur dans l'environnement du processus
        :size 0
        :setting variable_name:string:Nom de la variable à définir
        :param value:*:Valeur à stocker
        """
        self.environment.set(self.settings.get("variable_name"), value)


class Date(Component):
    def func(self):
        """
        :description Retourne la date actuelle selon le format spécifié
        :size 0
        :setting format:string:Format de la date, par défaut <%d/%m/%Y %H:%M:%S> (<%d> jour, <%m> mois, <%Y> année, <%H> heure, <%M> minute, <%S> seconde)
        :return date:string:Date atuelle selon le format spécifié
        """
        from datetime import datetime
        format = self.settings.get("format", "%d/%m/%Y %H:%M:%S")
        return datetime.now().strftime(format)


class Increment(Component):
    def func(self, value):
        """
        :description Permet d'incrémenter une variable d'environnement
        :size 0
        :param value:*:Valeur pour transmettre le flux d'exécution
        :return value:*:Transmission de la variable reçue en entrée
        :setting variable_name:string:Nom de la variable à incrémenter
        """
        variable_name = self.settings.get("variable_name")
        self.environment.set(variable_name, int(self.environment.get(variable_name, "0")) + 1)
        return value


class Decrement(Component):
    def func(self, value):
        """
        :description Permet de décrémenter une variable d'environnement
        :size 0
        :param value:*:Valeur pour transmettre le flux d'exécution
        :return value:*:Transmission de la variable reçue en entrée
        :setting variable_name:string:Nom de la variable à décrémenter
        """
        variable_name = self.settings.get("variable_name")
        self.environment.set(variable_name, int(self.environment.get(variable_name, "0")) - 1)
        return value