# -*- coding: utf-8 -*-

from operator import add
import re


class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        if not self.value:
            self.value = self.name

    def __str__(self):
        return f'{self.name}, {self.value}'

    name = str()
    value = str()


class Lexer:
    text = str()
    buffer = str()
    lex = list()

    def __init__(self, text):
        self.text = text

    def run(self):
        prev = str()
        for c in self.text:
            if c.isspace() or c in (';',):
                self.checkBuffer()
            elif c in ('(', ')', '{', '}', '=', '<', '>', '+'):
                res = self.checkBuffer()
                if not res:
                    self.buffer += c
                    self.checkBuffer()
            else:
                self.buffer += c
            prev = c

    def checkBuffer(self):
        name = self.getTokenName(self.buffer)
        if name:
            lexem = self.getTokenValue(self.buffer, name)
            self.lex.append(lexem)
            # print(self.buffer, '->', lexem)
            self.buffer = str()
        else:
            return None

    def getTokenName(self, buffer):
        if not len(buffer):
            return False
        elif buffer == 'function':
            return 'FUNCTION_DEF'
        # TODO: для function_run, thread
        elif buffer == 'call':
            return 'FUNCTION_CALL'
        elif buffer == 'for':
            return 'FOR_KW'
        elif buffer == 'push':
            return 'PUSH'
        elif buffer == 'set':
            return 'SET'
        elif buffer.isdigit():
            return 'NUMBER'
        elif buffer.isalnum():
            return 'VAR'
        elif buffer == '(':
            return 'OP_BRACE'
        elif buffer == ')':
            return 'CL_BRACE'
        elif buffer == '=':
            return 'ASSIGN_OP'
        elif buffer == '<':
            return 'LESS_OP'
        elif buffer == '>':
            return 'BIGGER_OP'
        elif buffer == '{':
            return 'CR_OP_BRACE'
        elif buffer == '}':
            return 'CR_CL_BRACE'
        elif buffer == '+':
            return 'ADD_OP'
        elif re.match('\[(.+)\]', buffer):
            return 'REFERENCE'
        else:
            return None

    def getTokenValue(self, buffer, name):
        if name in ('FOR_KW', 'OP_BRACE', 'CL_BRACE', 'ASSIGN_OP', 'LESS_OP', 'BIGGER_OP', 'PUSH', 'SET', 'FUNCTION_DEF'):
            value = None
        elif name == 'REFERENCE':
            value = re.match('\[(.+)\]', buffer).groups()[0]
        elif name == 'VAR' and buffer == 'll':
            name = 'LL'
            value = 'LL'
        elif name == 'VAR' and buffer == 'hs':
            name = 'HS'
            value = 'HS'
        else:
            value = buffer
        return Token(name, value)


# with open('adjunct.c', 'r') as content_file:
#     text = content_file.read()
#     print(text)

# text = 'i = 0; i = 3;'
# text = 'x = ll; x push 3; x push 4; x [ 0 ];'

# original:
# text = '''for (i = 0; i<10; i = i+1) {  \n\
#     i + 3; \n\
# }'''
# text = '''for (i = 0; i<10; i = i+1) {
#     ;
# }'''
# text = 'x = hs; x set 3 4; x set 4 5; x [ 3 ];'

text = '''
function test (x) {\n
    for (i = 0; i<10; i = i+1) {  \n
        ; \n
    } \n
}
test(1);
test(2);
'''


future_text = '''function test (x) {\n
    for (i = 0; i<10; i = i+1) {  \n
        ; \n
    } \n
};

thread test(10);
thread test(20);
'''

print(text)
lexer = Lexer(text)
lexer.run()
for l in lexer.lex:
    print(l)


class Node:
    def __init__(self, value):
        if type(value) == Node:
            self.value = value.value
            self.descendants = value.descendants
        else:
            self.value = value
            self.descendants = []

    def __str__(self):
        return str(self.value)

    def print(self, spac):
        print(spac, self)
        for n in self.descendants:
            if n:
                n.print(spac + '   ')

    def toPolishReverse(self):
        res = list()
        for d in self.descendants:
            if d:
                res.append(d.toPolishReverse())
        if self.value and self.value.name == 'FUNCTION_DEF':
            res = [('FUNCTION_DEF_END', 'FUNCTION_DEF_END')] + res
        if self.value:
            res.append((self.value.name, self.value.value))
        return res


class Parser:
    def __init__(self, tokenList):
        self.tokenList = tokenList
        self.n = 0
        self.masterNode = Node(None)

    def run(self):
        self.masterNode = self.parse(self.masterNode)
        return self.masterNode

    def parse(self, node):
        res = parse.expr(0)
        node.descendants.append(res)
        new_res = res
        while self.n < len(self.tokenList) and new_res:
            # new_res = parse.expr(self.n+1) # HS, LL, iter
            # new_res = parse.expr(self.n+2)
            # new_res = parse.expr(self.n+5)
            new_res = parse.expr(self.n+3)
            # res n+5
            rees1 = parse.stmt(self.n+5)
            rees2 = parse.stmt(self.n+6)
            print('rr', rees2)
            node.descendants += [new_res, rees1, rees2]
        return node

    def expr(self, n):
        if n > len(self.tokenList):
            return None
        curTok = self.tokenList[n]
        print('cur', curTok, n, self.tokenList[n-1])
        node = Node(curTok)
        sum_n = 0

        # TODO: объявление функции
        if curTok.name == 'FUNCTION_CALL':
            print('function call')
            func_name = self.match('VAR', n+1)
            m2 = self.match('OP_BRACE', n+2)
            arg = self.match('VAR', n+3)
            m4 = self.match('CL_BRACE', n+4)

            # res = self.expr(n+5)
            node.descendants += [func_name, arg]

        elif curTok.name == 'FUNCTION_DEF':
            self.stmt(n+1)
            m1 = self.match('VAR', n+1)
            m2 = self.match('OP_BRACE', n+2)
            m3 = self.match('VAR', n+3)
            m4 = self.match('CL_BRACE', n+4)

            brace = self.match('CR_OP_BRACE', n+5)
            res = self.expr(n+6)

            # TODO: куда-то записать функцию
            node.descendants += [res]
            # return res

        elif curTok.name == 'FOR_KW':
            # TODO: n+* можно поправить, заменив на self.n. проверить, должно работать на корректных входах. на некорректных выдавать ошибку
            self.match('OP_BRACE', n+1)
            index_assignation = self.stmt(n+2)
            stop_condition = self.stmt(n+5)
            iterator = self.stmt(n+8)

            self.match('CL_BRACE', n+1)
            brace = self.match('CR_OP_BRACE', n+14)

            # res = self.expr(n+15)
            # res = self.expr(n+2)
            # res = parse.stmt(n+15)

            node.descendants += [index_assignation,
                                 stop_condition, iterator]
        elif curTok.name == 'CR_CL_BRACE':
            return None
            # child = self.expr(n+2)
            # node.descendants += [child]
            # self.stmt(n)
        elif curTok.name == 'VAR':
            print('here')
            # print(curTok.name, self.match('OP_BRACE', n+1), self.match('VAR', n+2), self.match('CL_BRACE', n+3))
        else:
            res = self.stmt(self.n)
            return Node(res)
            res.print('')

        return node

    def stmt(self, n):
        varName = self.match('VAR', n)
        op_brace, cl_brace = self.match('OP_BRACE', n+1), self.match('CL_BRACE', n+3)

        print('oo', op_brace, cl_brace)

        if all([varName, op_brace, cl_brace]):
            node = Node(Token('FUNCTION_CALL', 'FUNCTION_CALL'))
            arg_num = self.tokenList[n+2]
            node.descendants = [
                Node(Token(varName.value, arg_num))
            ]
            return node

        op = self.match('ASSIGN_OP', n+1)
        if not op:
            op = self.match('LESS_OP', n+1)
        if not op:
            op = self.match('ADD_OP', n+1)
        if not op:
            op = self.match('REFERENCE', n+1)
        if not op:
            op = self.match('PUSH', n+1)
        if not op:
            op = self.match('SET', n+1)

        val, val2 = None, None
        if op and not op.name == 'REFERENCE':
            val = self.match('NUMBER', n+2)
            val2 = self.match('NUMBER', n+3)
            if not val:
                val = self.match('LL', n+2)
            if not val:
                val = self.match('HS', n+2)
            if not val:
                val = self.stmt(self.n+1)

        node = Node(op)

        # print('oop', op, varName, val)

        node.descendants += [Node(varName)]
        if val:
            node.descendants += [Node(val)]
        if val2:
            node.descendants += [Node(val2)]
        return node

    def match(self, expected, n):
        if n >= len(self.tokenList):
            return False

        if self.tokenList[n].name == expected:
            self.n += 1
            return self.tokenList[n]
        else:
            # self.n += 1
            return False
            # raise Exception('Syntax error', expected, self.tokenList[n].name)


parse = Parser(lexer.lex)
print('----')
tree = parse.run()
tree.print('')
polishReverse = tree.toPolishReverse()

bucket = list()


def flatten(l):
    ret = list()
    if type(l) == list:
        for el in l:
            bucket.append(flatten(el))
    else:
        return l


flatten(polishReverse)
bucket = [b for b in bucket if b is not None]

print('new polish', bucket)


class LinkedNode:
    def __init__(self, value):
        self.value = value
        self.next = None

    def getByKey(self, key, n):
        if not self.value:
            return None
        if int(key) == int(n):
            return self
        return self.next.getByKey(key, n+1), n

    def findByKey(self, key):
        if not self.value:
            return None
        if int(key) == int(self.value):
            return self
        return self.next.findByKey(key)

    def add(self, value):
        if not self.value:
            self.value = value
            self.next = self.__class__(None)
            return
        nxt = self.next
        if nxt:
            self.next.add(value)

    def print(self):
        print(self.value)
        nxt = self.next
        if nxt:
            self.next.print()

    def __str__(self):
        return str(self.value)

    # TODO: "__setitem__"


class HashSet:
    def __init__(self):
        self.bucketN = 10
        self.buckets = list()
        for n in range(self.bucketN):
            self.buckets.append(LinkedNode(None))

    def hsh(self, value):
        return int(str(value)[0])

    def __getitem__(self, key):
        h = self.hsh(key)
        bucket = self.buckets[h]

        res = bucket.findByKey(key)
        if not res:
            return None
        return res

    def add(self, key, value):
        h = self.hsh(key)
        bucket = self.buckets[h]

        res = bucket.findByKey(key)
        if not res:
            bucket.add(value)
        return res

    def __str__(self):
        ret = list()
        for b in self.buckets:
            ret.append(str(b.value))
        return str(ret)


# TODO: выполнение просто функций, по очереди, т.е. когда они syncronized по умолчанию
# TODO: выполнение функций с блокировками
class Interpreter:
    # TODO: интерпретатор должен сплодить самого себя и уметь выполнять инструкции поочередно
    # например, интерпретировать функцию
    def __init__(self, operandList):
        self.operandList = operandList
        self.varTable = {}
        self.opTable = {}
        self.op_id = 0
        self.stack = []
        self.parsingFunction = False

    def next_step(self, op):
        name = op[0]
        value = op[1]

        if self.parsingFunction and name != 'FUNCTION_DEF':
            self.functionOperandList.append(op)
        elif name == 'FUNCTION_DEF_END':
            self.parsingFunction = True
            self.functionOperandList = []
        elif name == 'FUNCTION_DEF':
            self.parsingFunction = False
            self.varTable[value] = self.functionOperandList
            self.functionOperandList = []
        elif name == 'FUNCTION_RUN':
            print('now running')
        elif name in ('VAR', 'NUMBER', 'LL', 'HS'):
            self.stack.append(op)
        elif name == 'ASSIGN_OP':
            op1 = self.stack.pop()
            op2 = self.stack.pop()

            op1_value = op1 if type(op1) is not tuple else op1[1]
            op2_value = op2 if type(op2) is not tuple else op2[1]

            if type(op1) == tuple and op1[0] == 'LL':
                op1_value = LinkedNode(None)
            if type(op1) == tuple and op1[0] == 'HS':
                op1_value = HashSet()

            self.varTable[op2_value] = op1_value
            self.varTable['last'] = op2_value

            print(self.varTable)

            # TODO: "порядок операций" для выполнения предыдущих операций в FOR

        elif name == 'SET':
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            var = self.stack.pop()

            op1_value = op1 if type(op1) is not tuple else op1[1]
            op2_value = op2 if type(op2) is not tuple else op2[1]

            self.varTable[var[1]].add(op2_value, op1_value)

        elif name == 'PUSH':
            val = self.stack.pop()
            key = self.stack.pop()
            # var = stack.pop()

            op1_value = op1 if type(op1) is not tuple else op1[1]
            op2_value = op2 if type(op2) is not tuple else op2[1]

            self.varTable[op2_value].add(op1_value)
            self.varTable[op2_value].print()

        elif name == 'LESS_OP':
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            op2_value = self.varTable[op2[1]]
            self.stack.append(op2_value < op1[1])

            if op2[1] not in self.opTable.keys():
                self.opTable[op2[1]] = {}
            opz_value = op1 if type(op1) is not tuple else op1[1]
            self.opTable[op2[1]]['comp'] = lambda x: x < int(opz_value)
        elif name == 'BIGGER_OP':
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            self.stack.append(op1 > op2)
        elif name == 'ADD_OP':
            op1 = self.stack.pop()
            op2 = self.stack.pop()
            op2_value = self.varTable[op2[1]]
            self.stack.append(int(op1[1])+int(op2_value))

            if op2[1] not in self.opTable.keys():
                self.opTable[op2[1]] = {}
            op1_value = op1 if type(op1) is not tuple else op1[1]

            op1_value = int(op1_value)
            self.opTable[op2[1]]['app'] = lambda x: x + op1_value

        elif name == 'REFERENCE':
            op1 = self.stack.pop()
            i = value

            op1_value = op1 if type(op1) is not tuple else op1[1]
            obj = self.varTable[op1_value]
            if type(obj) == HashSet:
                res = obj[i]
            elif type(obj) == LinkedNode:
                res = obj.getByKey(i, 0)

            self.stack.append(res)

        elif name == 'FOR_KW':
            l = self.varTable['last']
            op = self.opTable[l]['comp']
            app = self.opTable[l]['app']

            while(op(self.varTable[l])):
                print('varTable', self.varTable)
                self.varTable[l] = app(self.varTable[l])

        elif name == 'FUNCTION_CALL':
            print('considered this')
            # выполняем по одной за одной
            # TODO: оператор вызова функции, функция берется из таблицы по имени переменной
            # TODO: вызов подразумевает замену в таблице значений входными аргументами, выполнение инструкции за инструкциеей
            pass

        elif name == 'THREAD':
            # TODO: ключевое слово (тред название_функции) для вызова программы в треде
            # перебираем треды и выполняем функции в каждом одну за одной
            # Для каждого из треда, выполнить следующую инструкцию
            # т.е. сначала первая команда из одной функции, потом первая из второй, и так далее до конца
            pass

        print('stack', self.stack)
        print('varTable', self.varTable)

        for k in self.varTable.keys():
            if self.varTable[k] and k not in ('last',):
                print(k, self.varTable[k])
        print('-----')

    def next(self):
        op = self.operandList[self.op_id]
        self.next_step(op)
        self.op_id += 1

    def __call__(self):
        while self.op_id < len(self.operandList):
            print('op_id', self.op_id, len(self.operandList))
            self.next()


i = Interpreter(bucket)
i()
