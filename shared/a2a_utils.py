"""
Agent-to-Agent Communication Utilities
Handles inter-agent message passing and state management
"""

from typing import Dict, Any, List
import json
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp
        }


class A2ACommunication:
    """Agent-to-Agent communication handler"""
    
    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.agent_state: Dict[str, Dict[str, Any]] = {}
    
    def send_message(self, message: AgentMessage) -> bool:
        """Send message between agents"""
        self.message_queue.append(message)
        return True
    
    def get_messages(self, recipient_id: str) -> List[AgentMessage]:
        """Retrieve messages for a specific agent"""
        return [m for m in self.message_queue if m.recipient_id == recipient_id]
    
    def clear_messages(self, recipient_id: str) -> None:
        """Clear processed messages"""
        self.message_queue = [m for m in self.message_queue if m.recipient_id != recipient_id]
    
    def update_agent_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        """Update agent state"""
        self.agent_state[agent_id] = state
    
    def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve agent state"""
        return self.agent_state.get(agent_id, {})


class StateManager:
    """Manages workflow state across all agents"""
    
    def __init__(self):
        self.workflow_state = {
            "state_1_intake": None,
            "state_2_audit_chamber": None,
            "state_3_contextual_rag": None,
            "state_4_jury_verdict": None,
            "state_5_mitigation": None
        }
        self.case_data: Dict[str, Any] = {}
    
    def set_stage(self, stage: str, data: Dict[str, Any]) -> None:
        """Set workflow stage data"""
        if f"state_{stage}" in self.workflow_state:
            self.workflow_state[f"state_{stage}"] = data
    
    def get_stage(self, stage: str) -> Dict[str, Any]:
        """Get workflow stage data"""
        return self.workflow_state.get(f"state_{stage}", {})
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get all workflow context"""
        return {
            "workflow_state": self.workflow_state,
            "case_data": self.case_data
        }
    
    def update_case(self, case_id: str, data: Dict[str, Any]) -> None:
        """Update case data"""
        self.case_data[case_id] = data
