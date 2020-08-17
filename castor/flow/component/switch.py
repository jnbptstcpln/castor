"""
    :version 0.1
"""
from castor.flow.component import Component
import re


class Switch1(Component):
    def func(self, value):
        """
        :description
        :size 0
        :param value:*:Valeur sur laquelle sont effectués les tests
        :return value:*:Valeur retournée en fonction du résultat des tests
        :setting default:*:Valeur retournée par défaut par le bloc (possibilité d'afficher la valeur d'entrée avec <{value}>)
        :setting cases:json:Définition des différents tests et des résultats associés
        """
        cases = self.settings.get("cases", [])

        for case in cases:

            if case['type'] == 'equals':
                if value == case['test']:
                    return case['value'].format(value=value)

            if case['type'] == 'greater':
                if float(value) >= float(case['test']):
                    return case['value'].format(value=value)

            if case['type'] == 'greater_strict':
                if float(value) > float(case['test']):
                    return case['value'].format(value=value)

            if case['type'] == 'lesser':
                if float(value) <= float(case['test']):
                    return case['value'].format(value=value)

            if case['type'] == 'lesser_strict':
                if float(value) < float(case['test']):
                    return case['value'].format(value=value)

            if case['type'] == 'contains':
                if str(case['test']) in str(value):
                    return case['value'].format(value=value)

            if case['type'] == 'starts_with':
                if str(value).startswith(str(case['test'])):
                    return case['value'].format(value=value)

            if case['type'] == 'ends_with':
                if str(value).endswith(str(case['test'])):
                    return case['value'].format(value=value)

            if case['type'] == 'regex':
                if re.search(str(case['test']), str(value)) is not None:
                    return case['value'].format(value=value)

        return self.settings.get("default", "").format(value=value)
