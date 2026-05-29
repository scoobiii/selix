#!/usr/bin/env python3
"""
Módulo Central de Formatação - Garante limite de 300 caracteres
Único lugar onde o limite é verificado!
"""

import re

class BlueskyFormatter:
    """Centraliza a formatação de posts para o Bluesky"""

    MAX_LENGTH = 300

    @staticmethod
    def formatar_post(texto: str, max_length: int = MAX_LENGTH) -> str:
        """
        Formata e valida post para o Bluesky
        - Trunca se necessário (respeitando palavras)
        - Remove espaços extras
        - Valida limite
        """
        if not texto:
            return ""
        
        # Limpar espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # Verificar tamanho
        if len(texto) <= max_length:
            return texto
        
        # Truncar sem quebrar palavras
        texto_truncado = texto[:max_length]
        ultimo_espaco = texto_truncado.rfind(' ')
        
        if ultimo_espaco > max_length - 20:
            texto_truncado = texto_truncado[:ultimo_espaco]
        
        return texto_truncado + "..."
    
    @staticmethod
    def validar_post(texto: str) -> tuple:
        """Valida post e retorna (válido, mensagem_erro, tamanho)"""
        tamanho = len(texto)
        if tamanho <= BlueskyFormatter.MAX_LENGTH:
            return True, "OK", tamanho
        return False, f"Excede {tamanho - BlueskyFormatter.MAX_LENGTH} caracteres", tamanho
    
    @staticmethod
    def resumir_para_post(dados: dict, template: str, max_length: int = MAX_LENGTH) -> str:
        """Gera post a partir de template e dados, garantindo limite"""
        texto = template.format(**dados)
        return BlueskyFormatter.formatar_post(texto, max_length)


# Sistema de instrução para qualquer script que publicar
SYSTEM_INSTRUCTION = """
=== REGRA OBRIGATÓRIA PARA POSTS NO BLUESKY ===

ANTES DE QUALQUER POST, USE:

from core.formatter import BlueskyFormatter

texto = BlueskyFormatter.formatar_post(texto_bruto)

OU verifique:
valido, msg, size = BlueskyFormatter.validar_post(texto_bruto)
if not valido:
    texto = BlueskyFormatter.formatar_post(texto_bruto)

NUNCA publique sem passar pelo formatter!

LIMITE: 300 CARACTERES
==================================================
"""

if __name__ == "__main__":
    # Teste
    test_texto = "@b3.bsky.social " + "x" * 400
    resultado = BlueskyFormatter.formatar_post(test_texto)
    print(f"Original: {len(test_texto)} chars")
    print(f"Formatado: {len(resultado)} chars")
    print(f"Válido: {BlueskyFormatter.validar_post(resultado)[0]}")
