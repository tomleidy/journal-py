"""Type hints for the ephem library"""
from typing import TypeVar, Protocol, runtime_checkable, Union
from datetime import datetime
import ephem

# Base types
EphemDate = Union[ephem.Date, float]  # Changed from TypeVar to Union
EphemDegrees = TypeVar('EphemDegrees', bound=float)
EphemHours = TypeVar('EphemHours', bound=float)

# pylint: disable=missing-function-docstring


@runtime_checkable
class EphemBody(Protocol):
    """Protocol for ephem celestial bodies"""
    name: str
    _ra: EphemHours
    _dec: EphemDegrees
    ra: EphemHours
    dec: EphemDegrees
    alt: EphemDegrees
    az: EphemDegrees

    def compute(self, observer: 'EphemObserver') -> None: ...


@runtime_checkable
class EphemObserver(Protocol):
    """Protocol for ephem Observer class"""
    lat: str
    lon: str
    elevation: float
    pressure: float
    horizon: str
    date: EphemDate

    def next_rising(self, body: EphemBody) -> EphemDate: ...
    def next_setting(self, body: EphemBody) -> EphemDate: ...
    def next_transit(self, body: EphemBody) -> EphemDate: ...
    def previous_rising(self, body: EphemBody) -> EphemDate: ...
    def previous_setting(self, body: EphemBody) -> EphemDate: ...
    def previous_transit(self, body: EphemBody) -> EphemDate: ...


# Custom exceptions
CircumpolarError = ephem.CircumpolarError
AlwaysUpError = ephem.AlwaysUpError
NeverUpError = ephem.NeverUpError

# Helper functions for type conversion

# pylint: disable=invalid-name


def hours(_: str) -> EphemHours: ...
def degrees(_: str) -> EphemDegrees: ...
def Date(_: Union[datetime, str, float]) -> EphemDate: ...


# Constants
pi: float = ephem.pi
