"""
Math Tool for modular-2 framework.
Provides mathematical calculation capabilities.
"""
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MathTool:
    """
    Tool for performing mathematical calculations.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the math tool.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.description = "Tool for mathematical calculations and expressions"
        logger.debug("🔢 MathTool inizializzato")
    
    def run(self, input_data: Dict[str, Any]) -> str:
        """
        Execute mathematical calculation.
        
        Args:
            input_data: Input data containing expression or calculation request
            
        Returns:
            Calculation result as string
        """
        try:
            # Extract expression from various possible input formats
            expression = self._extract_expression(input_data)
            
            if not expression:
                return "Nessuna espressione matematica trovata nell'input"
            
            # Perform calculation
            result = self._calculate(expression)
            
            logger.info(f"🔢 Calcolo eseguito: {expression} = {result}")
            return str(result)
            
        except Exception as e:
            logger.error(f"❌ Errore nel calcolo matematico: {e}")
            return f"Errore nel calcolo: {str(e)}"
    
    def _extract_expression(self, input_data: Dict[str, Any]) -> str:
        """Extract mathematical expression from input data."""
        # Try different input formats
        
        # Direct expression field
        if "expression" in input_data:
            return str(input_data["expression"])
        
        # From prompt field
        if "prompt" in input_data:
            prompt = str(input_data["prompt"])
            # Look for mathematical expressions in the prompt
            math_patterns = [
                r'(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?(?:\s*[+\-*/]\s*\d+(?:\.\d+)?)*)',
                r'(\d+\s*[+\-*/]\s*\d+)',
                r'([\d+\-*/\.\s\(\)]+)',
            ]
            
            for pattern in math_patterns:
                matches = re.findall(pattern, prompt)
                if matches:
                    # Return the longest match (most likely to be complete)
                    return max(matches, key=len)
        
        # From operation and operands
        if "operation" in input_data:
            operation = input_data["operation"]
            if operation == "add" and "a" in input_data and "b" in input_data:
                return f"{input_data['a']} + {input_data['b']}"
            elif operation == "subtract" and "a" in input_data and "b" in input_data:
                return f"{input_data['a']} - {input_data['b']}"
            elif operation == "multiply" and "a" in input_data and "b" in input_data:
                return f"{input_data['a']} * {input_data['b']}"
            elif operation == "divide" and "a" in input_data and "b" in input_data:
                return f"{input_data['a']} / {input_data['b']}"
        
        # Try to extract from any string value
        for key, value in input_data.items():
            if isinstance(value, str):
                # Look for mathematical expressions
                math_match = re.search(r'(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?)', value)
                if math_match:
                    return math_match.group(1)
        
        return ""
    
    def _calculate(self, expression: str) -> float:
        """
        Safely calculate mathematical expression.
        
        Args:
            expression: Mathematical expression as string
            
        Returns:
            Calculation result
        """
        # Clean the expression
        expression = expression.strip()
        
        # Remove any non-mathematical characters (keep numbers, operators, parentheses, dots)
        cleaned_expr = re.sub(r'[^0-9+\-*/\.\(\)\s]', '', expression)
        
        if not cleaned_expr:
            raise ValueError("Nessuna espressione matematica valida trovata")
        
        # Basic validation
        if not re.match(r'^[\d+\-*/\.\(\)\s]+$', cleaned_expr):
            raise ValueError("Espressione contiene caratteri non validi")
        
        # Check for division by zero
        if '/0' in cleaned_expr.replace(' ', ''):
            raise ValueError("Divisione per zero non permessa")
        
        try:
            # Use eval safely (in a real production environment, consider using a proper math parser)
            # For now, we'll use eval with basic safety checks
            result = eval(cleaned_expr)
            
            # Validate result
            if not isinstance(result, (int, float)):
                raise ValueError("Risultato non numerico")
            
            # Check for infinity or NaN
            if str(result) in ['inf', '-inf', 'nan']:
                raise ValueError("Risultato non valido (infinito o NaN)")
            
            return float(result)
            
        except ZeroDivisionError:
            raise ValueError("Divisione per zero")
        except SyntaxError:
            raise ValueError("Sintassi dell'espressione non valida")
        except Exception as e:
            raise ValueError(f"Errore nel calcolo: {str(e)}")
    
    def should_use(self, text: str) -> bool:
        """
        Determine if this tool should be used based on the input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            True if the tool should be used
        """
        # Check for mathematical keywords and patterns
        math_keywords = [
            "calcola", "calculate", "math", "matematica", "somma", "sottrai", 
            "moltiplica", "dividi", "add", "subtract", "multiply", "divide"
        ]
        
        text_lower = text.lower()
        
        # Check for keywords
        if any(keyword in text_lower for keyword in math_keywords):
            return True
        
        # Check for mathematical expressions
        if re.search(r'\d+\s*[+\-*/]\s*\d+', text):
            return True
        
        # Check for numbers with operators
        if re.search(r'[+\-*/=]', text) and re.search(r'\d', text):
            return True
        
        return False