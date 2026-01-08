"""
Módulo de integrações para imobiliária
"""
from .google_forms import GoogleFormsIntegration
from .chatgpt import ChatGPTIntegration
from .clickup import ClickUpIntegration
from .google_drive import GoogleDriveIntegration
from .chaves_na_mao import ChavesNaMaoIntegration
from .wasseller import WassellerIntegration

__all__ = [
    'GoogleFormsIntegration',
    'ChatGPTIntegration',
    'ClickUpIntegration',
    'GoogleDriveIntegration',
    'ChavesNaMaoIntegration',
    'WassellerIntegration'
]


