import logging


def init_global_logger(log_level: int = logging.DEBUG, file_log_path: [str, None] = None) -> None:
    """
    Configure le singleton ``logging``. Il suffit de déclarer cette fonction
    dans le script main de l'application.

    Le format du singleton est ajouté : en console et sur un fichier si
    mentionné (en rotatingFileHandler).

    utilisation : juste importer logging, puis utiliser les commandes du singleton

    .. note::

        Ce paramétrage est très basique, si vous souhaitez ajouter un logger
        custom supplémentaire, les logs seront notifiés car le log root
        hérite quoi qu'il arrive du log de tous les autres logger; si vous
        souhaitez séparer les logs, cette fonction ne doit pas être exploitée.

    :return:
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if file_log_path:
        file_handler = logging.FileHandler(file_log_path, mode='a', encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

