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
        """
        self.flow.log(value)

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
        :description Permet de terminer l'exécution du processus
        :size 0
        :param value:*:Valeur qui sera ajoutée aux logs
        """
        self.flow.log("Exit : {}".format(value))
        self.exit()


class Format1(Component):
    def func(self, string1):
        """
        :description Permet de formatter la chaine de caractères passée en entrée
        :size 0
        :param string1:string:Chaine de caractères
        :return result:string:Résultat du formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{0}>)
        """
        return self.settings.get("template", "{0}").format(string1)

class Format2(Component):
    def func(self, string1, string2):
        """
        :description Permet de formatter les chaines de caractères passées en entrées
        :size 0
        :param string1:string:Première chaine de caractères
        :param string2:string:Seconde chaine de caractères
        :return result:string:Résultat du formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{0}{1}>)
        """
        return self.settings.get("template", "{0}{1}").format(string1, string2)


class Format3(Component):
    def func(self, string1, string2, string3):
        """
        :description Permet de formatter les chaines de caractères passées en entrées
        :size 0
        :param string1:string:Première chaine de caractères
        :param string2:string:Seconde chaine de caractères
        :param string3:string:Troisième chaine de caractères
        :return result:string:Résultat de formattage
        :setting template:string:Modèle selon lequel sera formattée la sortie (par défaut <{0}{1}{2}>)
        """
        return self.settings.get("template", "{0}{1}{2}").format(string1, string2, string3)


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