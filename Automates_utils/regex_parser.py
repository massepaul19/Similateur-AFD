# regex_parser.py
class RegexNode:
    def __init__(self, kind, value=None, left=None, right=None):
        self.kind = kind  # 'char', 'concat', 'union', 'star'
        self.value = value
        self.left = left
        self.right = right

def parse_regex(regex):
    def precedence(op):
        return {'|': 1, '.': 2, '*': 3}.get(op, 0)

    def to_postfix(regex):
        output = []
        stack = []
        prev = None
        for char in regex:
            if char.isalnum():
                if prev and (prev.isalnum() or prev == '*' or prev == ')'):
                    while stack and precedence('.') <= precedence(stack[-1]):
                        output.append(stack.pop())
                    stack.append('.')
                output.append(char)
            elif char == '(':
                if prev and (prev.isalnum() or prev == '*' or prev == ')'):
                    while stack and precedence('.') <= precedence(stack[-1]):
                        output.append(stack.pop())
                    stack.append('.')
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            elif char in ['*', '|']:
                while stack and precedence(char) <= precedence(stack[-1]):
                    output.append(stack.pop())
                stack.append(char)
            prev = char
        while stack:
            output.append(stack.pop())
        return output

    def postfix_to_ast(postfix):
        stack = []
        for token in postfix:
            if token.isalnum():
                stack.append(RegexNode('char', token))
            elif token == '*':
                a = stack.pop()
                stack.append(RegexNode('star', left=a))
            elif token == '.':
                b = stack.pop()
                a = stack.pop()
                stack.append(RegexNode('concat', left=a, right=b))
            elif token == '|':
                b = stack.pop()
                a = stack.pop()
                stack.append(RegexNode('union', left=a, right=b))
        return stack[0]

    postfix = to_postfix(regex)
    return postfix_to_ast(postfix)

