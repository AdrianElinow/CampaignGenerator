from dataclasses import dataclass, field
import copy
import uuid
from datetime import datetime
from typing import Any
from .NGIN_utils.ngin_utils import get_unique_strs, normalize_str
from .SimulaeNode import SimulaeNode
from .SimulaeConstants import *

class SimulaeEvent(SimulaeNode):
    '''
    Unified 'event' data-structure for social and physical world-events
    '''

    Effects = []

    def __init__(self, 
                 id: str,
                 event_class: str,
                 event_type: str,
                 event_subtype: str,
                 start_timestamp: str | None,
                 end_timestamp: str | None,
                 location_id: str | None,
                 source_ids: list[str],
                 target_ids: list[str],
                 observer_ids: list[str],
                 effects):
        
        references = {
            "created_timestamp": str(datetime.now()), # created now
            "source_ids": source_ids,
            "target_ids": target_ids,
            "observer_ids": observer_ids,
            "event_class": event_class,
            "event_type": event_type,
            "event_subtype": event_subtype,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            LOC: location_id,
        }

        super().__init__(
            id, 
            nodetype=EVT,
            references=references,
        )

        self.Effects = effects

    def __post_init__(self):

        start_timestamp = self.get_reference("start_timestamp")
        timestamp = self.get_reference("created_timestamp")

        if start_timestamp is None and timestamp is not None:
            self.set_reference("start_timestamp", timestamp)

        self.observer_ids = get_unique_strs(self.observer_ids)
        self.target_ids = get_unique_strs(self.target_ids)
        self.source_ids = get_unique_strs(self.source_ids)

    def add_source(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.source_ids:
            self.source_ids.append(src_id)
            return True
        
        return False
    
    def remove_source(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.source_ids:
            self.source_ids.remove(src_id)
            return True
        
        return False
    
    def add_target(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.target_ids:
            self.target_ids.append(src_id)
            return True
        
        return False
    
    def remove_target(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.target_ids:
            self.target_ids.remove(src_id)
            return True
        
        return False
    
    def add_observer(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.observer_ids:
            self.observer_ids.append(src_id)
            return True
        
        return False
    
    def remove_observer(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id not in self.observer_ids:
            self.observer_ids.remove(src_id)
            return True
        
        return False

    def was_observed_by(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id in self.observer_ids:
            return True
        
        return False
    
    def was_perpetrated_by(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id in self.source_ids:
            return True
        
        return False
    
    def was_inflicted_upon(self, node_id: str) -> bool:
        src_id = normalize_str(node_id)
        
        if src_id and src_id in self.target_ids:
            return True
        
        return False
