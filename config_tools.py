# encoding:utf-8
"""
Config Tools
============

Les classes ConfigSuperClass et SubConfig permettent l'exploitation d'une
configuration dans un singleton (instance commune à toute l'application),
ce depuis n'importe quel fichier ou dictionnaire.

Structuration d'une classe custom
---------------------------------

La superclass ConfigSuperClass permet de customiser la configuration requise depuis
les paramètres fournis dans le __init__. La configuration peut hériter d'une autre
configuration, les classmethods permettent leur exploitation.

.. code:: python

    class _SubConfig(SubConfig):  # sous classe
        def __init__(self, param3, param4):  # implémentation des paramètres
            self.param3 = param3
            self.param4 = param4


    class ConfigurationData(ConfigSuperClass, metaclass=Singleton):  # classe de config
        def __init__(self, param1, param2, subconf):  # implémentation des paramètres
            self.param1 = param1
            self.param2 = param2
            self.subconf = _SubConfig(**subconf)  # les sous paramètre sont distribué dans une classe


La classe SubClass permet de faire hériter le comportement de la ConfigSuperClass
sans pour autant en faire un singleton (dans le cas où la subclass modélise une clé
à une profondeur supplémentaire dans la configuration).

.. code:: python

    class NewConfigurationData(ConfigSuperClass, metaclass=Singleton):
        def __init__(self, param5, param6, subconf, data_conf):
            # récupération d'une classe de conf initiale
            self.config_data = ConfigurationData.load_from_dict(data_conf)
            self.param5 = param5
            self.param6 = param6

.. note::

    La superclass ConfigSuperClass a un comportement exhaustif, le moindre
    paramètre non implémenté dans la classe ou manquant relèvera une exception
    de type ConfigFileParamError. des valeurs par défaut peuvent néanmoins être
    implémentées dans le __init__.


Déclaration de l'instance
-------------------------

La 1ere déclaration nécessite les données, passées en argument dans le __init__. Le yaml doit contenir
la meme structure clé/valeur que la classe visée, en prenant en compte toutes les sous classes.
L'instanciation passe par fichier ou dictionnaire:

.. code::

    ConfigurationData.load_from_file("file.yml")

    with open("file.yml", "r", encoding="utf-8") as file:
        content = yaml.load(file, Loader=yaml.Loader)

    ConfigurationData.load_from_dict(**content)



Récupération de l'instance dans le projet
-----------------------------------------

Une fois la classe instanciée, son instance peut être récupérée avec la méthode "instance".

.. code:: python

    config = ConfigurationData.instance()

    config.param1


Bonnes pratiques d'utilisation
------------------------------

L'objectif de cette classe est de faciliter l'exploitation des données statiques et d'avoir par la même occasion
un contexte de paramétrage.

L'instanciation peut se faire au fil de l'eau dans le script principal, mais l'appel de l'instance doit absolument
être enclavé dans les méthodes et fonctions (ou à la limite dans un try except) dans le reste du projet, pour ne pas
imposer systématiquement le contexte à l'import et la lecture des modules (tests unitaire, imports de libs,
et génération de la doc).

Si plusieurs couches de paramètres sont en place :

Le paramétrage final (projet courant) possède une classe ayant pour attribut les autres classes de paramétrage. Etant
elles-mêmes des singleton, leur simple instanciation suffira pour les exploiter dans le code de leur libraries
respectives. Leur import étant placé dans une classe englobante, celle-ci sera la seule appelée :

- une instance unique de paramétrage (possédant les instances filles uniques aussi)
- un seul chargement initial des paramètres pour tout le projet
- un seul fichier de paramétrage en yaml

La boucle est bouclée, le paramétrage est unique et totalement géré dans le projet, module par module.

"""
from os.path import isfile
from yaml import load, Loader


class ConfigFileParamError(Exception):
    """
    Utilisé pour préciser que l'exception provient d'un paramètre manquant ou en trop.
    """


def _type_error_response(origin, e):
    """
    Relève l'exception ConfigFileParamError avec un message user-friendly.
    L'exécution de cette fonction révèle qu'il y a une anomalie dans le fichier
    yaml fourni, ou le dictionnaire : un paramètre manquant ou en trop.

    :param origin:
    :param e:
    :return:
    """
    msg = f"le paramètre {e} est manquant ou superflu dans la configuration fournie ({origin})."
    raise ConfigFileParamError(msg)


class Singleton(type):
    """
    Super classe d'attribution de la particularité singleton.

    C'est une metaclass et doit être intégrée comme tel.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def instance(cls):
        """
        Renvoie l'instance. Renvoie une ConfigFileParamError si l'instance n'existe pas.

        La classe ne pouvant être instanciée sans ses paramètres, la remontée d'une erreur
        par cette méthode signifie que les paramètres n'ont pas été chargés préalablement dans
        le script.

        :return:
        """
        if cls in cls._instances:
            return cls._instances[cls]
        raise ConfigFileParamError("L'instance a été appelée sans avoir chargé les données")


class _ReprConfigurationMixin:
    """
    Sous classe possédant le comportement de la représentation d'une classe de configuration.
    Si l'instance de la classe est appelée comme tel, cette représentation sera retournée.

    """

    def __repr__(self):
        msg = f"{self.__class__.__name__}({', '.join([f'{key}={repr(val)}' for key, val in self.__dict__.items()])})"
        return msg


class SubConfig(_ReprConfigurationMixin):
    """
    Classe de confort. Pour la représenation d'une sous classe de configuration (non singleton),
    elle permet d'avoir une représentation commune avec les classe héritant ConfigSuperClass
    """


class ConfigSuperClass(_ReprConfigurationMixin):
    """
    Super classe pour la configuration. Abstraite.

    Possède les quatres fonction nécessaires:

        - la méthode constructeur d'import de la config depuis un fichier
        - la méthode constructeur d'import de la config depuis un dict
        - la méthode d'instance d'import de la config depuis un fichier
        - la méthode d'instance d'import de la config depuis un dict

    """

    @classmethod
    def from_file(cls, yaml_file: str):
        """
        Constructeur. Importe la configuration depuis le fichier yaml_file et instancie.

        :param yaml_file:
        :return:
        """
        assert isfile(yaml_file), f"le path {yaml_file} spécifié ne renvoie pas vers un fichier"

        with open(yaml_file, "r", encoding="utf-8") as file:
            content = load(file, Loader=Loader)

        try:
            return cls(**content)
        except TypeError as e:
            _type_error_response(yaml_file, e)

    @classmethod
    def load_from_dict(cls, _dict: dict):
        """
        Constructeur. Importe la configuration depuis le dict _dict et instancie.

        :param _dict:
        :return:
        """
        try:
            return cls(**_dict)
        except TypeError as e:
            _type_error_response("dict variable", e)

    def reload_from_file(self, yaml_file: str):
        """
        recharge les attributs de l'instance depuis le fichier yaml_file.

        :param yaml_file:
        :return:
        """
        assert isfile(yaml_file), f"le path {yaml_file} spécifié ne renvoie pas vers un fichier"

        with open(yaml_file, "r", encoding="utf-8") as file:
            content = load(file, Loader=Loader)

        try:
            self.__init__(**content)
        except TypeError as e:
            _type_error_response(yaml_file, e)

    def reload_from_dict(self, _dict: dict):
        """
        recharge les attributs de l'instance depuis le dict _dict.

        :param _dict:
        :return:
        """
        try:
            self.__init__(**_dict)
        except TypeError as e:
            _type_error_response("dict variable", e)
