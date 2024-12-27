from check_phat_nguoi.utils.singleton import Singleton

from .models import PlatesModel


class PlatesContext(Singleton, PlatesModel): ...


plates_context: PlatesContext = PlatesContext()


__all__ = ["PlatesContext", "plates_context"]