import spacy
import re
from datetime import datetime
from typing import Optional, Dict, Any

# Carregar o modelo de linguagem spaCy (menor para protótipo)
# Certifique-se de ter baixado: python -m spacy download pt_core_news_sm
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("Modelo pt_core_news_sm não encontrado. Baixe-o com: python -m spacy download pt_core_news_sm")
    # Tentar carregar um modelo maior como fallback ou instruir o usuário
    # nlp = spacy.load("pt_core_news_lg") # Alternativa maior
    exit()

class StatusTextProcessor:
    def __init__(self):
        # Padrões regex para extrair informações comuns
        self.patterns = {
            "project_id": r"PROJ[ -]?(\d+)",
            "completion_percentage": r"(\d{1,3}(?:[.,]\d{1,2})?)\s*%\s*(?:conclu[ií]do|completo|de progresso)",
            "spi": r"SPI(?:\s*[:=-])?\s*(\d+(?:[.,]\d{1,2})?)",
            "cpi": r"CPI(?:\s*[:=-])?\s*(\d+(?:[.,]\d{1,2})?)",
            "budget": r"or[çc]amento(?:\s*total)?(?:\s*[:=-])?\s*R\$ *([\d.,]+)",
            "actual_cost": r"custo\s*atual(?:\s*[:=-])?\s*R\$ *([\d.,]+)",
            "delay_days": r"atraso(?:\s*de)?\s*(\d+)\s*dias?",
            "scope_change_keywords": ["mudan[cç]a de escopo", "altera[cç][aã]o de escopo", "escopo alterado"],
            "risk_keywords": ["risco identificado", "novo risco", "amea[cç]a", "problema potencial"]
        }

    def _extract_with_regex(self, text: str, pattern_key: str) -> Optional[Any]:
        match = re.search(self.patterns[pattern_key], text, re.IGNORECASE)
        if match:
            if pattern_key in ["budget", "actual_cost"]:
                # Limpar e converter valor monetário
                value_str = match.group(1).replace(".", "").replace(",", ".")
                return float(value_str)
            elif pattern_key in ["completion_percentage", "spi", "cpi", "delay_days"]:
                return float(match.group(1).replace(",", "."))
            return match.group(1)
        return None

    def _extract_entities(self, doc) -> Dict[str, list]:
        entities = {
            "dates": [],
            "orgs": [],
            "persons": [],
            "locations": []
        }
        for ent in doc.ents:
            if ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["orgs"].append(ent.text)
            elif ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ in ["LOC", "GPE"]:
                entities["locations"].append(ent.text)
        return entities

    def process_status_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            return {"error": f"Arquivo não encontrado: {file_path}", "status": "error"}
        except Exception as e:
            return {"error": f"Erro ao ler arquivo {file_path}: {e}", "status": "error"}

        doc = nlp(text)

        # Tentativa de extrair data e gerente
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        extracted_info = {
            "file_path": file_path,
            "project_id": self._extract_with_regex(text, "project_id"),
            "report_date": dates[0] if dates else None,
            "manager": persons[0] if persons else None,
            "raw_text": text,
            "entities": self._extract_entities(doc)
        }

        metrics = {
            "completion_percentage": self._extract_with_regex(text, "completion_percentage"),
            "spi": self._extract_with_regex(text, "spi"),
            "cpi": self._extract_with_regex(text, "cpi"),
            "budget": self._extract_with_regex(text, "budget"),
            "actual_cost": self._extract_with_regex(text, "actual_cost"),
            "delay_days": self._extract_with_regex(text, "delay_days"),
            "scope_change_detected": any(keyword in text.lower() for keyword in self.patterns["scope_change_keywords"]),
            "risk_detected": any(keyword in text.lower() for keyword in self.patterns["risk_keywords"])
        }

        # Remover chaves com valores None para limpeza
        metrics = {k: v for k, v in metrics.items() if v is not None}

        return {
            "project_info": extracted_info,
            "metrics": metrics,
            "status": "success"
        }

# Exemplo de uso (para teste)
if __name__ == "__main__":
    processor = StatusTextProcessor()
    # Crie um arquivo de exemplo em ../status_files/PROJ-001_cronograma.txt
    # Ex: "Status do PROJ-001: 50% concluído. SPI de 0.8. Atraso de 10 dias."
    example_file = "../status_files/PROJ-001_cronograma.txt" # Ajuste o caminho se necessário

    # Criar diretório e arquivo de exemplo se não existirem
    import os
    if not os.path.exists("../status_files"):
        os.makedirs("../status_files")
    if not os.path.exists(example_file):
        with open(example_file, "w", encoding="utf-8") as f:
            f.write(
                "Status do PROJ-001: O projeto está 50% concluído. O SPI atual é de 0.85. "
                "Temos um atraso de 10 dias. O orçamento é R$ 100.000,00 e o custo atual R$ 60.000,00. "
                "Foi identificado um novo risco. Gerente: João Silva. Data do relatório: 10/07/2025."
            )

    result = processor.process_status_file(example_file)
    if result["status"] == "success":
        print("Informações do Projeto:", result["project_info"])
        print("Métricas Extraídas:", result["metrics"])
    else:
        print("Erro:", result["error"])
