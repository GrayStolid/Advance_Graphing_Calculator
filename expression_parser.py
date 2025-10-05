"""
Expression Parser Module
Handles conversion between infix, prefix, and postfix notations
"""

import re
import math


class ExpressionParser:
    def __init__(self):
        # Operator precedence (higher number = higher precedence)
        self.precedence = {
            '+': 1, '-': 1,
            '*': 2, '/': 2, '%': 2,
            '^': 3, '**': 3,
            'sin': 4, 'cos': 4, 'tan': 4,
            'log': 4, 'ln': 4, 'sqrt': 4,
            'exp': 4, 'abs': 4
        }
        
        # Right associative operators
        self.right_associative = {'^', '**'}
        
        # Functions that take one argument
        self.functions = {'sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp', 'abs'}
    
    def normalize_expression(self, expression):
        """Normalize expression for consistent parsing"""
        # Replace common patterns
        expression = expression.replace(' ', '')
        expression = expression.replace('**', '^')
        
        # Add multiplication signs where needed
        expression = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression)  # 2x -> 2*x
        expression = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression)  # x2 -> x*2
        expression = re.sub(r'(\))(\()', r'\1*\2', expression)        # )( -> )*(
        expression = re.sub(r'(\d)(\()', r'\1*\2', expression)        # 2( -> 2*(
        expression = re.sub(r'(\))([a-zA-Z])', r'\1*\2', expression)  # )x -> )*x
        
        return expression
    
    def tokenize(self, expression):
        """Tokenize expression into operators, operands, and functions"""
        tokens = []
        i = 0
        
        while i < len(expression):
            if expression[i].isspace():
                i += 1
                continue
            
            # Numbers (including decimals)
            if expression[i].isdigit() or expression[i] == '.':
                num = ''
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    num += expression[i]
                    i += 1
                tokens.append(num)
                continue
            
            # Functions and variables
            if expression[i].isalpha():
                name = ''
                while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                    name += expression[i]
                    i += 1
                tokens.append(name)
                continue
            
            # Two-character operators
            if i < len(expression) - 1:
                two_char = expression[i:i+2]
                if two_char in self.precedence:
                    tokens.append(two_char)
                    i += 2
                    continue
            
            # Single character operators and parentheses
            tokens.append(expression[i])
            i += 1
        
        return tokens
    
    def infix_to_postfix(self, expression):
        """Convert infix to postfix using Shunting Yard algorithm"""
        tokens = self.tokenize(expression)
        output = []
        operator_stack = []
        
        for token in tokens:
            # Operand (number or variable)
            if self.is_operand(token):
                output.append(token)
            
            # Function
            elif token in self.functions:
                operator_stack.append(token)
            
            # Left parenthesis
            elif token == '(':
                operator_stack.append(token)
            
            # Right parenthesis
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()  # Remove the '('
                # If there's a function on top of stack, pop it
                if operator_stack and operator_stack[-1] in self.functions:
                    output.append(operator_stack.pop())
            
            # Operator
            elif token in self.precedence:
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       operator_stack[-1] in self.precedence and
                       (self.precedence[operator_stack[-1]] > self.precedence[token] or
                        (self.precedence[operator_stack[-1]] == self.precedence[token] and 
                         token not in self.right_associative))):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
        
        # Pop remaining operators
        while operator_stack:
            output.append(operator_stack.pop())
        
        return ' '.join(output)
    
    def infix_to_prefix(self, expression):
        """Convert infix to prefix"""
        # Reverse the expression
        tokens = self.tokenize(expression)
        tokens.reverse()
        
        # Swap parentheses
        for i in range(len(tokens)):
            if tokens[i] == '(':
                tokens[i] = ')'
            elif tokens[i] == ')':
                tokens[i] = '('
        
        # Get postfix of reversed expression
        reversed_expr = ''.join(tokens)
        postfix = self.infix_to_postfix(reversed_expr)
        
        # Reverse the result
        prefix_tokens = postfix.split()
        prefix_tokens.reverse()
        
        return ' '.join(prefix_tokens)
    
    def is_operand(self, token):
        """Check if token is an operand (number or variable)"""
        try:
            float(token)
            return True
        except ValueError:
            return token.isalpha() and token not in self.functions and token not in self.precedence
    
    def get_parse_tree_representation(self, expression):
        """Get a simple text representation of the parse tree"""
        try:
            postfix = self.infix_to_postfix(expression)
            tokens = postfix.split()
            
            if not tokens:
                return "Empty expression"
            
            # Build tree representation using stack
            stack = []
            
            for token in tokens:
                if self.is_operand(token):
                    stack.append(token)
                elif token in self.functions:
                    if stack:
                        operand = stack.pop()
                        stack.append(f"{token}({operand})")
                elif token in self.precedence:
                    if len(stack) >= 2:
                        right = stack.pop()
                        left = stack.pop()
                        stack.append(f"({left} {token} {right})")
                    elif len(stack) == 1 and token in ['+', '-']:
                        # Unary operator
                        operand = stack.pop()
                        stack.append(f"({token}{operand})")
            
            return stack[0] if stack else "Invalid expression"
            
        except Exception as e:
            return f"Error building parse tree: {str(e)}"
    
    def evaluate_expression(self, expression, variables=None):
        """Evaluate expression with given variables"""
        if variables is None:
            variables = {}
        
        try:
            # Normalize expression
            expr = self.normalize_expression(expression)
            
            # Replace variables
            for var, value in variables.items():
                expr = expr.replace(var, str(value))
            
            # Replace functions with math module equivalents
            expr = expr.replace('sin', 'math.sin')
            expr = expr.replace('cos', 'math.cos')
            expr = expr.replace('tan', 'math.tan')
            expr = expr.replace('log', 'math.log10')
            expr = expr.replace('ln', 'math.log')
            expr = expr.replace('sqrt', 'math.sqrt')
            expr = expr.replace('exp', 'math.exp')
            expr = expr.replace('abs', 'math.fabs')
            expr = expr.replace('^', '**')
            # Evaluate safely
            return eval(expr, {"__builtins__": {}, "math": math})
            
        except Exception as e:
            raise ValueError(f"Cannot evaluate expression: {str(e)}")
