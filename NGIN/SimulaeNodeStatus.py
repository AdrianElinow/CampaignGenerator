from NGIN import SimulaeNode
from NGIN.NGIN_utils.ngin_utils import logDebug
from enum import Enum

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
    logDebug("jsonify(state)")

    d = state.__dict__

    for k,v in state.Relations.items():

        v =  v = { nid:node.__dict__ for nid, node in v.items() }
        d['relations'][k] = v

    return d