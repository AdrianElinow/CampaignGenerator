from .SimulaeNode import SimulaeNode
from .SimulaeConstants import *

class SimulaeCondition(SimulaeNode):

    def __init__(self,
                 id):
        
        super().__init__(
            given_id=id,
            nodetype=CND,
        )