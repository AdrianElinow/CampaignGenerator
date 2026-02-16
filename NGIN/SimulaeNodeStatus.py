from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from .NGIN_utils.ngin_utils import logAll

if TYPE_CHECKING:
    from .SimulaeNode import SimulaeNode

class SimulaeNodeStatus(Enum):
    ''' Simulae Node status '''
    ALIVE = 0
    DEAD = 1

    def toJSON(self):
        if self == 0:
            return "ALIVE"
        elif self == 1:
            return "DEAD"

def jsonify( state: SimulaeNode ):
    logAll("jsonify(state)")

    d = state.__dict__

    for k,v in state.Relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d
