#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas de validação para endpoints da API SELIX.
"""

from pydantic import BaseModel, Field, validator

class PerguntaRequest(BaseModel):
    pergunta: str = Field(..., min_length=1, max_length=500)

    @validator('pergunta')
    def nao_vazia(cls, v):
        if not v.strip():
            raise ValueError('A pergunta não pode ser vazia')
        return v

class FAQRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=200)
