#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# schemas.py - Modelos Pydantic V2
# Versão: 2.0.0-GOS3

from pydantic import BaseModel, Field, field_validator

class PerguntaRequest(BaseModel):
    """Modelo para requisição de pergunta ao SELIX"""
    pergunta: str = Field(..., min_length=1, max_length=500, description="Pergunta do usuário")
    
    @field_validator('pergunta')
    @classmethod
    def validate_pergunta(cls, v: str) -> str:
        """Valida e sanitiza a pergunta"""
        if not v or not v.strip():
            raise ValueError('Pergunta não pode estar vazia')
        # Remove caracteres potencialmente perigosos
        v = v.strip()
        if len(v) > 500:
            raise ValueError('Pergunta muito longa (máximo 500 caracteres)')
        return v

class RespostaBase(BaseModel):
    """Modelo base para respostas da API"""
    success: bool = True
    message: str = ""
    data: dict = {}

class HealthResponse(BaseModel):
    """Resposta do endpoint /health"""
    status: str = "ok"
    versao: str = "4.0"
    timestamp: str

class ErroResponse(BaseModel):
    """Resposta padronizada para erros"""
    erro: str
    detalhe: str | None = None
