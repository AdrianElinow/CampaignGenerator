from .SimulaeNode import SimulaeNode
from .SimulaeConstants import *
from typing import Any

class SimulaeCondition(SimulaeNode):

    def __init__(self,
                 id, 
                 name,
                 conditions: list[dict[str, Any]]):
        
        references = {
            NAME: name
        }

        super().__init__(
            given_id=id,
            nodetype=CND,
            references=references
        )

        self.Conditions = conditions


    def satisfies_conditions(self, node: SimulaeNode | None) -> bool:

        if not self.Conditions:
            return False
        
        if not node: 
            return False

        for conditional in self.Conditions:
            
            if not self.satisfies_condition(node, conditional):
                return False

        return False
    

    def satisfies_condition(self, node: SimulaeNode, conditional: dict) -> bool:
        # TODO AE: Implement

        ''' conditional structure: {
            operation : "equal|not-equal|greater-than|less-than|...-or-equal|is-member|is-not-member"
            left: {
                bind: ""
                nodetype: "<Nodetype(s)>|ANY",
                "property": "...",
                "key": "...",
                "subkey": "...",
            }
            right: {
                <same as 'left'>
                OR
                "value": "...",
            }
        }
        '''

        return True