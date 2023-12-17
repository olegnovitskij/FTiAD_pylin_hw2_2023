from flask import Flask, request, jsonify

class Calculator:
    def __init__(self, expression):
        self.expression = expression.replace(' ', '')

    def preprocess_expression(self):
        self.expression = self.expression.replace('(-', '(0-').replace(',-', ',0-')

    def tokenize_expression(self):
        tokens = []
        current_token = ''

        for i, char in enumerate(self.expression):
            if char.isdigit() or char == '.':
                current_token += char
            elif char == '-' and (i == 0 or self.expression[i-1] in ['(', '+', '-', '*', '/']):
                current_token += char
            else:
                if current_token:
                    tokens.append(float(current_token))
                    current_token = ''
                tokens.append(char)

        if current_token:
            tokens.append(float(current_token))

        return tokens

    def to_reverse_polish_notation(self):
        output = []
        operators = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        for token in self.tokenize_expression():
            if isinstance(token, float):
                output.append(token)
            elif token in precedence:
                while (operators and operators[-1] in precedence and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()

        while operators:
            output.append(operators.pop())

        return output

    def calculate_rpn(self):
        stack = []

        for token in self.to_reverse_polish_notation():
            if isinstance(token, float):
                stack.append(token)
            else:
                b = stack.pop()
                a = stack.pop()

                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ValueError('Division by zero')
                    stack.append(a / b)

        return stack[0]


app = Flask(__name__)

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        expression = data['expression']

        calculator = Calculator(expression)
        calculator.preprocess_expression()
        result = calculator.calculate_rpn()

        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
    # !curl -X POST -H "Content-Type: application/json" -d '{"expression": "-3.7 + (-4) * (-(-2 - 1)) / 5"}' http://127.0.0.1:5000/calculate