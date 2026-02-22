from dataclasses import dataclass, field
import copy
import uuid
from typing import Any
from .NGIN_utils.ngin_utils import get_unique_strs, normalize_str

class SimulaeEvent:
    '''
    Unified 'event' data-structure for social and physical world-events
    '''

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    namespace: str = ""
    version: str = ""
    timestamp: str = ""

    event_class: str = ""
    event_type: str = ""
    event_subtype: str = ""

    start_timestamp: str | None = None
    end_timestamp: str | None = None

    location_id: str | None = None

    source_ids: list = []
    target_ids: list = []
    observer_ids: list = []

    payload = None
    causality = None

    def __init__(self, 
                 id: str,
                 namespace: str,
                 version: str,
                 timestamp: str,
                 event_class: str,
                 event_type: str,
                 event_subtype: str,
                 start_timestamp: str | None,
                 end_timestamp: str | None,
                 location_id: str | None,
                 source_ids: list[str],
                 target_ids: list[str],
                 observer_ids: list[str],
                 payload,
                 causality):

        id = id
        namespace = namespace
        version = version
        timestamp = timestamp
        event_class = event_class
        event_type = event_type
        event_subtype = event_subtype
        start_timestamp = start_timestamp
        end_timestamp = end_timestamp
        location_id = location_id
        source_ids = source_ids
        target_ids = target_ids
        observer_ids = observer_ids
        payload = payload
        causality = causality

    def __post_init__(self):

        if not self.event_class:
            raise ValueError("event_class is required")
        
        if not self.event_type:
            raise ValueError("event_type is required")
        

        if self.start_timestamp is None and self.timestamp is not None:
            self.start_timestamp = self.timestamp
        elif self.timestamp is None and self.start_timestamp is not None:
            self.timestamp = self.start_timestamp

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

    def to_dict(self) -> dict[str, Any]:

        data: dict[str, Any] = {
            'id': self.id,
            'event_class': self.event_class,
            'event_type': self.event_type,
            'event_subtype': self.event_subtype,
            'timestamp': self.timestamp,
            'start_timestamp': self.start_timestamp,
            'end_timestamp': self.end_timestamp,
            'payload': self.payload,
            'targets': self.target_ids,
            'sources': self.source_ids,
            'causality': self.causality,
        }

        return { key: value for key, value in data.items() if value is not None }
