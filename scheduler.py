# encoding:utf-8
from time import sleep
from datetime import datetime
import logging


def schedule_every(minutes: int):
    """
    Décorateur. Lance en boucle infinie la fonction.

    Si le temps de process de la fonction est inférieur à :minutes:,
    le décorateur reste latent le temps restant.

    Ne gère pas les exceptions.

    :param minutes:
    :return:
    """

    def decorator(func):

        def inner(*args, **kwargs):
            while True:
                start = datetime.now()
                func(*args, **kwargs)
                time_left = minutes * 60 - (datetime.now() - start).seconds
                wait_until = time_left if time_left > 0 else 0

                if wait_until:
                    logging.debug(f"run pending {wait_until} seconds (scheduled)")
                sleep(wait_until)

        return inner

    return decorator


def schedule_every_five_minutes(func):
    """
    Décorateur. Boucle sur la fonction décorée toutes les cinq minutes.

    Exploite le décorateur ``schedule_every``. C'est un bon exemple de réexploitation de ce décorateur à des fins
    plus custom.

    :param func:
    :return:
    """

    @schedule_every(5)
    def inner(*args, **kwargs):
        func(*args, **kwargs)

    return inner


if __name__ == '__main__':
    logging.info("coucou")
    logging.info("super coucou")
