import json
import os
from datetime import datetime

class PMBOKGuardRails:
    """
    Sistema de guard rails baseado nas melhores práticas do PMBOK.
    
    Este sistema valida as recomendações dos agentes e garante que estejam
    alinhadas com as melhores práticas de gerenciamento de projetos do PMBOK.
    """
    
    def __init__(self):
        """
        Inicializa o sistema de guard rails.
        """
        # Carregar regras para cada domínio
        self.rules = {
            "cronograma": self._load_schedule_rules(),
            "custos": self._load_cost_rules(),
            "escopo": self._load_scope_rules(),
            "riscos": self._load_risk_rules()
        }
    
    def _load_schedule_rules(self):
        """
        Carrega as regras para o domínio de cronograma.
        
        Returns:
            Lista de regras
        """
        return [
            {
                "id": "SCH-001",
                "name": "Notificação para SPI crítico",
                "description": "Qualquer SPI < 0.8 requer notificação imediata ao gerente do projeto",
                "condition": lambda data: data.get('spi') is not None and data.get('spi') < 0.8,
                "action": "notify",
                "message": "ALERTA CRÍTICO: O SPI está abaixo de 0.8, indicando atraso significativo no cronograma. Notifique imediatamente o gerente do projeto."
            },
            {
                "id": "SCH-002",
                "name": "Plano de recuperação para SPI baixo",
                "description": "Qualquer SPI < 0.9 requer um plano de recuperação documentado",
                "condition": lambda data: data.get('spi') is not None and data.get('spi') < 0.9,
                "action": "require",
                "message": "REQUISITO: O SPI está abaixo de 0.9. Um plano de recuperação documentado é necessário."
            },
            {
                "id": "SCH-003",
                "name": "Aprovação para extensão de prazo",
                "description": "Extensões de prazo > 10% da duração original requerem aprovação formal",
                "condition": lambda data: data.get('atraso_dias') is not None and data.get('duracao_planejada') is not None and data.get('atraso_dias') > 0.1 * data.get('duracao_planejada'),
                "action": "require",
                "message": "REQUISITO: A extensão de prazo excede 10% da duração original do projeto. Aprovação formal é necessária."
            },
            {
                "id": "SCH-004",
                "name": "Revisão da linha de base para replanejamento",
                "description": "Replanejamento de cronograma requer revisão da linha de base",
                "condition": lambda data: data.get('replanejamento') is True,
                "action": "require",
                "message": "REQUISITO: O replanejamento do cronograma requer revisão formal da linha de base."
            },
            {
                "id": "SCH-005",
                "name": "Monitoramento diário para tarefas críticas",
                "description": "Tarefas críticas devem ter monitoramento diário quando SPI < 0.9",
                "condition": lambda data: data.get('spi') is not None and data.get('spi') < 0.9 and data.get('tarefas_criticas') is not None and len(data.get('tarefas_criticas')) > 0,
                "action": "recommend",
                "message": "RECOMENDAÇÃO: Implemente monitoramento diário para todas as tarefas críticas devido ao SPI baixo."
            }
        ]
    
    def _load_cost_rules(self):
        """
        Carrega as regras para o domínio de custos.
        
        Returns:
            Lista de regras
        """
        return [
            {
                "id": "COST-001",
                "name": "Notificação para CPI crítico",
                "description": "Qualquer CPI < 0.8 requer notificação imediata ao gerente do projeto",
                "condition": lambda data: data.get('cpi') is not None and data.get('cpi') < 0.8,
                "action": "notify",
                "message": "ALERTA CRÍTICO: O CPI está abaixo de 0.8, indicando desvio significativo nos custos. Notifique imediatamente o gerente do projeto."
            },
            {
                "id": "COST-002",
                "name": "Plano de recuperação para CPI baixo",
                "description": "Qualquer CPI < 0.9 requer um plano de recuperação documentado",
                "condition": lambda data: data.get('cpi') is not None and data.get('cpi') < 0.9,
                "action": "require",
                "message": "REQUISITO: O CPI está abaixo de 0.9. Um plano de recuperação documentado é necessário."
            },
            {
                "id": "COST-003",
                "name": "Aprovação para gastos adicionais",
                "description": "Gastos adicionais > 10% do orçamento requerem aprovação formal",
                "condition": lambda data: data.get('desvio_orcamento') is not None and data.get('desvio_orcamento') > 10,
                "action": "require",
                "message": "REQUISITO: Os gastos adicionais excedem 10% do orçamento. Aprovação formal é necessária."
            },
            {
                "id": "COST-004",
                "name": "Aprovação para realocação de orçamento",
                "description": "Realocação de orçamento entre categorias > 5% requer aprovação",
                "condition": lambda data: data.get('realocacao_orcamento') is not None and data.get('realocacao_orcamento') > 5,
                "action": "require",
                "message": "REQUISITO: A realocação de orçamento entre categorias excede 5%. Aprovação formal é necessária."
            },
            {
                "id": "COST-005",
                "name": "Recálculo semanal da EAC",
                "description": "Estimativa no término (EAC) deve ser recalculada semanalmente quando CPI < 0.9",
                "condition": lambda data: data.get('cpi') is not None and data.get('cpi') < 0.9,
                "action": "recommend",
                "message": "RECOMENDAÇÃO: Recalcule a Estimativa no Término (EAC) semanalmente devido ao CPI baixo."
            }
        ]
    
    def _load_scope_rules(self):
        """
        Carrega as regras para o domínio de escopo.
        
        Returns:
            Lista de regras
        """
        return [
            {
                "id": "SCOPE-001",
                "name": "Documentação formal para mudanças de escopo",
                "description": "Todas as mudanças de escopo requerem documentação formal",
                "condition": lambda data: data.get('mudanca_escopo') == 'Sim',
                "action": "require",
                "message": "REQUISITO: Todas as mudanças de escopo requerem documentação formal."
            },
            {
                "id": "SCOPE-002",
                "name": "Revisão da linha de base para impacto no cronograma",
                "description": "Mudanças com impacto no cronograma > 10 dias requerem revisão da linha de base",
                "condition": lambda data: data.get('impacto_cronograma') is not None and data.get('impacto_cronograma') > 10,
                "action": "require",
                "message": "REQUISITO: A mudança de escopo tem impacto significativo no cronograma. Revisão da linha de base é necessária."
            },
            {
                "id": "SCOPE-003",
                "name": "Revisão do orçamento para impacto no custo",
                "description": "Mudanças com impacto no custo > 5% requerem revisão do orçamento",
                "condition": lambda data: data.get('impacto_custo_percentual') is not None and data.get('impacto_custo_percentual') > 5,
                "action": "require",
                "message": "REQUISITO: A mudança de escopo tem impacto significativo no custo. Revisão do orçamento é necessária."
            },
            {
                "id": "SCOPE-004",
                "name": "Revisão do plano para múltiplas mudanças",
                "description": "Mais de 3 mudanças de escopo requerem revisão do plano de gerenciamento do projeto",
                "condition": lambda data: data.get('num_mudancas_escopo') is not None and data.get('num_mudancas_escopo') > 3,
                "action": "require",
                "message": "REQUISITO: Múltiplas mudanças de escopo foram identificadas. Revisão do plano de gerenciamento do projeto é necessária."
            },
            {
                "id": "SCOPE-005",
                "name": "Análise de impacto para mudanças de escopo",
                "description": "Todas as mudanças de escopo devem incluir análise de impacto em cronograma e custos",
                "condition": lambda data: data.get('mudanca_escopo') == 'Sim',
                "action": "require",
                "message": "REQUISITO: Todas as mudanças de escopo devem incluir análise de impacto em cronograma e custos."
            }
        ]
    
    def _load_risk_rules(self):
        """
        Carrega as regras para o domínio de riscos.
        
        Returns:
            Lista de regras
        """
        return [
            {
                "id": "RISK-001",
                "name": "Planos de mitigação para riscos altos",
                "description": "Riscos com nível 'Alto' requerem planos de mitigação documentados",
                "condition": lambda data: data.get('riscos_altos') is not None and len(data.get('riscos_altos')) > 0,
                "action": "require",
                "message": "REQUISITO: Todos os riscos de nível 'Alto' requerem planos de mitigação documentados."
            },
            {
                "id": "RISK-002",
                "name": "Planos de contingência para riscos críticos",
                "description": "Riscos com probabilidade >= 4 e impacto >= 4 requerem planos de contingência",
                "condition": lambda data: data.get('riscos_criticos') is not None and len(data.get('riscos_criticos')) > 0,
                "action": "require",
                "message": "REQUISITO: Todos os riscos críticos (probabilidade >= 4 e impacto >= 4) requerem planos de contingência."
            },
            {
                "id": "RISK-003",
                "name": "Revisão quinzenal do registro de riscos",
                "description": "Registro de riscos deve ser revisado pelo menos quinzenalmente",
                "condition": lambda data: True,  # Sempre aplicável
                "action": "recommend",
                "message": "RECOMENDAÇÃO: O registro de riscos deve ser revisado pelo menos quinzenalmente."
            },
            {
                "id": "RISK-004",
                "name": "Notificação para novos riscos altos",
                "description": "Novos riscos identificados com nível 'Alto' requerem notificação imediata ao gerente do projeto",
                "condition": lambda data: data.get('novos_riscos_altos') is not None and len(data.get('novos_riscos_altos')) > 0,
                "action": "notify",
                "message": "ALERTA: Novos riscos de nível 'Alto' foram identificados. Notifique imediatamente o gerente do projeto."
            },
            {
                "id": "RISK-005",
                "name": "Monitoramento semanal para riscos de alta exposição",
                "description": "Riscos com valor de exposição (probabilidade * impacto) >= 12 requerem monitoramento semanal",
                "condition": lambda data: data.get('riscos_alta_exposicao') is not None and len(data.get('riscos_alta_exposicao')) > 0,
                "action": "recommend",
                "message": "RECOMENDAÇÃO: Implemente monitoramento semanal para todos os riscos com valor de exposição >= 12."
            }
        ]
    
    def validate(self, domain, data):
        """
        Valida os dados com base nas regras do domínio.
        
        Args:
            domain: Domínio das regras (cronograma, custos, escopo, riscos)
            data: Dados a serem validados
            
        Returns:
            Dicionário com resultados da validação
        """
        if domain not in self.rules:
            return {
                "valid": False,
                "messages": [f"Domínio inválido: {domain}"],
                "validation_date": datetime.now().isoformat()
            }
        
        # Aplicar regras
        messages = []
        valid = True
        
        for rule in self.rules[domain]:
            try:
                if rule["condition"](data):
                    messages.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "message": rule["message"],
                        "action": rule["action"]
                    })
                    
                    # Se a ação for "require" e não for atendida, marcar como inválido
                    if rule["action"] == "require" and not self._check_requirement_met(rule, data):
                        valid = False
            except Exception as e:
                messages.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "message": f"Erro ao aplicar regra: {str(e)}",
                    "action": "error"
                })
        
        return {
            "valid": valid,
            "messages": messages,
            "validation_date": datetime.now().isoformat()
        }
    
    def _check_requirement_met(self, rule, data):
        """
        Verifica se um requisito foi atendido.
        
        Args:
            rule: Regra a ser verificada
            data: Dados a serem validados
            
        Returns:
            True se o requisito foi atendido, False caso contrário
        """
        # Implementação básica - verificar se há um campo indicando que o requisito foi atendido
        requirement_key = f"requirement_{rule['id']}_met"
        return data.get(requirement_key, False)
    
    def validate_recommendations(self, domain, recommendations, data):
        """
        Valida as recomendações com base nas regras do domínio.
        
        Args:
            domain: Domínio das regras (cronograma, custos, escopo, riscos)
            recommendations: Lista de recomendações a serem validadas
            data: Dados do projeto
            
        Returns:
            Dicionário com resultados da validação
        """
        # Validar dados
        validation_results = self.validate(domain, data)
        
        # Verificar se as recomendações atendem aos requisitos
        required_topics = []
        for message in validation_results["messages"]:
            if message["action"] == "require":
                required_topics.append(message["rule_name"])
        
        # Verificar se as recomendações cobrem os tópicos obrigatórios
        missing_topics = []
        for topic in required_topics:
            if not self._topic_covered_in_recommendations(topic, recommendations):
                missing_topics.append(topic)
        
        # Adicionar recomendações obrigatórias ausentes
        additional_recommendations = []
        for message in validation_results["messages"]:
            if message["action"] == "recommend" or (message["action"] == "require" and message["rule_name"] in missing_topics):
                additional_recommendations.append(message["message"])
        
        return {
            "valid": len(missing_topics) == 0,
            "missing_topics": missing_topics,
            "additional_recommendations": additional_recommendations,
            "validation_messages": validation_results["messages"],
            "validation_date": datetime.now().isoformat()
        }
    
    def _topic_covered_in_recommendations(self, topic, recommendations):
        """
        Verifica se um tópico está coberto nas recomendações.
        
        Args:
            topic: Tópico a ser verificado
            recommendations: Lista de recomendações
            
        Returns:
            True se o tópico está coberto, False caso contrário
        """
        # Implementação básica - verificar se alguma recomendação contém palavras-chave do tópico
        keywords = self._extract_keywords(topic)
        
        for recommendation in recommendations:
            recommendation_lower = recommendation.lower()
            if any(keyword in recommendation_lower for keyword in keywords):
                return True
        
        return False
    
    def _extract_keywords(self, topic):
        """
        Extrai palavras-chave de um tópico.
        
        Args:
            topic: Tópico
            
        Returns:
            Lista de palavras-chave
        """
        # Implementação básica - extrair palavras com mais de 4 caracteres
        words = topic.lower().split()
        return [word for word in words if len(word) > 4 and word not in ["para", "com", "que", "deve", "quando", "requer"]]
    
    def generate_report(self, validation_results):
        """
        Gera um relatório com base nos resultados da validação.
        
        Args:
            validation_results: Resultados da validação
            
        Returns:
            Relatório formatado
        """
        report = f"""
        RELATÓRIO DE VALIDAÇÃO (GUARD RAILS)
        
        Data da validação: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        STATUS: {"VÁLIDO" if validation_results.get('valid', False) else "INVÁLIDO"}
        
        MENSAGENS DE VALIDAÇÃO:
        """
        
        for message in validation_results.get('validation_messages', []):
            action_label = {
                "notify": "ALERTA",
                "require": "REQUISITO",
                "recommend": "RECOMENDAÇÃO",
                "error": "ERRO"
            }.get(message.get('action', ''), message.get('action', '').upper())
            
            report += f"- [{message.get('rule_id', 'N/A')}] {action_label}: {message.get('message', 'N/A')}\n"
        
        if 'missing_topics' in validation_results and len(validation_results['missing_topics']) > 0:
            report += "\nTÓPICOS OBRIGATÓRIOS NÃO COBERTOS:\n"
            for topic in validation_results['missing_topics']:
                report += f"- {topic}\n"
        
        if 'additional_recommendations' in validation_results and len(validation_results['additional_recommendations']) > 0:
            report += "\nRECOMENDAÇÕES ADICIONAIS:\n"
            for recommendation in validation_results['additional_recommendations']:
                report += f"- {recommendation}\n"
        
        return report

# Exemplo de uso
if __name__ == "__main__":
    # Criar sistema de guard rails
    guard_rails = PMBOKGuardRails()
    
    # Dados de exemplo para cronograma
    schedule_data = {
        "spi": 0.75,
        "atraso_dias": 15,
        "duracao_planejada": 100,
        "tarefas_criticas": ["Tarefa 1", "Tarefa 2"],
        "replanejamento": True
    }
    
    # Validar dados
    validation_results = guard_rails.validate("cronograma", schedule_data)
    
    # Recomendações de exemplo
    recommendations = [
        "Revisar o caminho crítico e identificar oportunidades de fast-tracking",
        "Alocar recursos adicionais para as tarefas críticas",
        "Implementar horas extras para recuperar o atraso"
    ]
    
    # Validar recomendações
    recommendation_validation = guard_rails.validate_recommendations("cronograma", recommendations, schedule_data)
    
    # Gerar relatório
    report = guard_rails.generate_report(recommendation_validation)
    
    print(report)
