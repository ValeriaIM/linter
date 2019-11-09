import sys
import os
import re
import threading


def set_tab(s):
    global tab

    if s[:3] == 'tab':
        tab = int(s[6:s.find(';')])


def set_doubleSigns(s):
    global doubleSigns

    if s[:11] == 'doubleSigns':
        doubleSigns = s[14:s.find(';')].split(', ')


def set_firstSigns(s):
    global firstSigns

    if s[:10] == 'firstSigns':
        firstSigns = s[13:s.find(';')].split(', ')


def set_words_with_indent(s):
    global wordsWithIndent

    if s[:15] == 'wordsWithIndent':
        wordsWithIndent = s[18:s.find(';')].split(', ')


def set_words_without_punctuation(s):
    global wordsWithoutPunctuation

    if s[:23] == 'wordsWithoutPunctuation':
        wordsWithoutPunctuation = s[26:s.find(';')].split(', ')


def set_reserved_words(s):
    global reservedWords

    if s[:13] == 'reservedWords':
        reservedWords = s[16:s.find(';')].split(', ')


def set_fixed_types(s):
    global types

    if s[:5] == 'types':
        types = s[8:s.find(';')].split(', ')


def set_style(s):
    global keywordStyle
    global variableStyle
    global constStyle
    global funcStyle
    global procedureStyle
    global typeStyle
    global recordStyle

    if s[:12] == 'keywordStyle':
        keywordStyle = s[15:s.find(';')]
    if s[:13] == 'variableStyle':
        variableStyle = s[16:s.find(';')]
    if s[:10] == 'constStyle':
        constStyle = s[13:s.find(';')]
    if s[:9] == 'funcStyle':
        funcStyle = s[12:s.find(';')]
    if s[:14] == 'procedureStyle':
        procedureStyle = s[17:s.find(';')]
    if s[:9] == 'typeStyle':
        typeStyle = s[12:s.find(';')]
    if s[:11] == 'recordStyle':
        recordStyle = s[14:s.find(';')]


def tokenizator(s):
    global tokens
    global firstSigns
    global doubleSigns

    state = 'start'
    i = 0
    word = []
    flfs = False  # fl firstSigns

    while 1:
        if state == 'start':
            a = ''.join(word) + s[i]
            if (i == len(s)) or (s[i] == '\n') or (a.lower() == 'end.'):
                state = 'end'
                i = i - 1
            elif re.match(r'\W', s[i]):
                if firstSigns.count(s[i]) != 0:
                    if word:
                        tokens.append(''.join(word))
                    del word[:]
                    state = 'start'
                    a = s[i] + s[i + 1]
                    if doubleSigns.count(a) != 0:
                        tokens.append(a)
                        i = i + 1
                    else:
                        tokens.append(s[i])
                else:
                    state = 'new word'
                    i = i - 1
            else:
                word.append(s[i])
        elif state == 'new word':
            if word:
                tokens.append(''.join(word))
            tokens.append(s[i])
            del word[:]
            state = 'start'
        elif state == 'end':
            if word:
                tokens.append(''.join(word))
            if (s[i] == '\n') or (s[i] == '.'):
                tokens.append(s[i])
            break
        i = i + 1


def check_tab():
    global tokens
    global closeOperatorBracket
    global openOperatorBracket
    global tab
    global wordsWithIndent
    global wordsWithoutPunctuation

    s = 1
    indent = 0
    countSpaces = 0
    fl = False
    flFirstB = True
    flw = 0  # wordsWithIndent

    if tokens[0] == ' ':
        print('tab error, str', s, 'pos', 0)

    for token in tokens:
        sToken = token.lower()
        if token == '\n':
            s = s + 1
            countSpaces = 0
            fl = True
            continue
        elif sToken == closeOperatorBracket:
            indent = indent - tab
        elif (sToken == 'var') or (sToken == 'const') or (sToken == 'type'):
            indent = tab
            fl = False
        elif (sToken == openOperatorBracket) and flFirstB:
            indent = 0
            flFirstB = False
        if fl:
            if sToken == ' ':
                countSpaces = countSpaces + 1
            elif countSpaces == indent:
                fl = False
            else:
                print('tab error, str', s, 'pos', indent)
                fl = False
        elif flw == s:
            flw = 0
        elif (flw < s) and flw:
            indent = indent - tab
            flw = 0
        if wordsWithIndent.count(sToken) != 0:
            indent = indent + tab
            flw = s
        elif sToken == closeOperatorBracket:
            indent = indent - tab
        elif sToken == openOperatorBracket:
            indent = indent + tab
            if flw:
                flw = flw + 2


def check_style():
    check_keyword_style()
    check_variable_style()
    check_const_style()
    check_type_style()


def check_variable_style():
    global tokens
    global reservedWords
    global types
    global variableStyle

    fl = False
    s = 1
    key = ''
    style = variableStyle

    for token in tokens:
        if token == '\n':
            s = s + 1
            continue
        if token == 'var':
            if fl:
                textError = 'logic error: Word has already been used, str'
                print(textError, s, 'word -', token)
            fl = True
            continue
        if token == 'begin':
            fl = False
            continue
        if fl and re.match(r'\w+', token):
            if reservedWords.count(token) != 0:
                print('style error: Word reserved, str', s, 'word -', token)
            elif types.count(token) == 0:
                key = token
            else:
                set_variable(key, token, s)
                if (style == 'all small') and (key != key.lower()):
                    print('variable style error, str', s, 'word -', key)
                if (style == 'all big') and (key != key.upper()):
                    print('variable style error, str', s, 'word -', key)
                if (style == 'first big') and (key != key.capitalize()):
                    print('variable style error, str', s, 'word -', key)


def set_variable(key, typeT, s):
    global variables

    if key:
        variables[key] = typeT
    else:
        print('syntaxis error: Waited word, str', s, 'word', key)


def check_const_style():
    global tokens
    global reservedWords
    global types
    global constStyle

    fl = False
    flu = False
    flp = False
    s = 1
    key = ''
    value = ''
    token = ''
    typeT = ''

    for index in range(len(tokens)):
        token = tokens[index]
        if token == '\n':
            s = s + 1
            continue
        if token == 'const':
            if flu:
                textError = 'logic error: Word has already been used, str'
                print(textError, s, 'word -', token)
            fl = True
            flu = True
            continue
        if (token == 'var') or (token == 'begin') or (token == 'type'):
            fl = False
            continue
        if fl and re.match(r'\w+', token):
            if reservedWords.count(token) != 0:
                print('style error: Word reserved, str', s, 'word -', token)
            elif types.count(token) != 0:  # типизированная константа
                typeT = token
            elif len(key) == 0:
                key = token
            elif len(value) == 0:
                token1 = tokens[index - 1]
                token2 = tokens[index - 2]
                if (token2 == '$') and ((token1 == '-') or (token1 == '+')):
                    value = token2 + token1
                else:
                    if (token2 == '$') or (token2 == '-') or (token2 == '+'):
                        value = token2
                value = value + token
                token1 = tokens[index + 1]
                token2 = tokens[index + 2]
                if (token1 == '.'):
                    if re.match(r'\w+', token2):
                        flp = True
                        continue
                    else:
                        print('syntaxis error, str', s, 'word', value)
            else:
                token1 = tokens[index - 1]
                token2 = tokens[index - 2]
                if flp and (token2 == value) and (token1 == '.'):
                    value = value + '.' + token
                    flp = False
            if key and value:
                if (constStyle == 'all small') and (key != key.lower()):
                    print('const style error, str', s, 'word -', key)
                if (constStyle == 'all big') and (key != key.upper()):
                    print('const style error, str', s, 'word -', key)
                if (constStyle == 'first big') and (key != key.capitalize()):
                    print('const style error, str', s, 'word -', key)
                set_type_const(key, value, typeT, s)
                key = ''
                value = ''
                typeT = ''


def set_type_const(key, value, typeT, s):

    if typeT:
        set_variable(key, typeT, s)
        return
    if re.search(r'[^\d, E, -, +, $, \.]', value):
        if len(value) == 1:
            typeT = 'char'
        else:
            typeT = 'string'
    elif (len(re.findall(r'$', value)) == 1) and value[0] == '$':
        typeT = 'real'
        point = re.search(r'\.', value)
        e = re.search(r'E', value)
        if point or e:
            ('syntaxis error, str', s, 'word', value)
        minus = re.findall(r'-', value)
        plus = re.findall(r'\+', value)
        lenm = len(minus)
        lenp = len(plus)
        if (lenm > 1) or (lenp > 1):
            ('syntaxis error, str', s, 'word', value)
        elif (lenm == 1) or (lenp == 1):
            if (value[1] != '-') or (value[1] != '+'):
                ('syntaxis error, str', s, 'word', value)
    elif (re.match(r'\.', value)) or (re.match(r'E', value)):
        typeT = 'real'
    else:
        typeT = 'int'
    set_variable(key, typeT, s)


def check_keyword_style():
    global tokens
    global reservedWords
    global types
    global keywordStyle

    fl = False
    s = 1

    for index in range(len(tokens)):
        token = tokens[index]
        if token == '\n':
            s = s + 1
            continue
        a = reservedWords.count(token.lower())
        b = types.count(token.lower())
        if (a != 0) or (b != 0):
            if (keywordStyle == 'all small') and (token != token.lower()):
                tokens[index] = token.lower()
                print('keyword style error, str', s, 'word -', token)
            if (keywordStyle == 'all big') and (token != token.upper()):
                print('keyword style error, str', s, 'word -', token)
                tokens[index] = token.upper()
            if (keywordStyle == 'first big') and (token != token.capitalize()):
                print('keyword style error, str', s, 'word -', token)
                tokens[index] = token.capitalize()


def check_type_style():
    global tokens
    global reservedWords
    global types
    global typeStyle

    fl = False
    flu = False
    s = 1
    name = ''

    for token in tokens:
        if token == '\n':
            s = s + 1
            name = ''
            continue
        elif token == 'type':
            if flu:
                textError = 'logic error: Word has already been used, str'
                print(textError, s, 'word -', token)
            fl = True
            flu = True
            continue
        elif (token == 'var') or (token == 'begin'):
            fl = False
            continue
        if fl and re.match(r'\w+', token):
            if reservedWords.count(token) != 0:
                print('style error: Word reserved, str', s, 'word -', token)
            elif name:
                continue
            else:
                name = token
                if (typeStyle == 'all small') and (name != name.lower()):
                    print('type style error, str', s, 'word -', name)
                if (typeStyle == 'all big') and (name != name.upper()):
                    print('type style error, str', s, 'word -', name)
                if (typeStyle == 'first big') and (name != name.capitalize()):
                    print('type style error, str', s, 'word -', name)


def check_punctuation():
    global tokens
    global wordsWithoutPunctuation
    global wordsWithIndent

    s = 1
    fl = False
    flV = False
    strV = 0
    flBracket = False  # ' and "
    flEnd = False
    lastStrWithV = 0  # ;
    words = wordsWithoutPunctuation

    for index in range(len(tokens)):
        token1 = tokens[index].lower()
        if index + 1 < len(tokens):
            token2 = tokens[index + 1]
            if (token1 == '\'') or (token1 == '\"'):
                flBracket = not(flBracket)
                continue
            elif token1 == ';':
                if flBracket:
                    continue
                lastStrWithV = s
                if (token2 != '\n'):
                    print('punctuation error: Waited enter, str', s)
            elif words.count(token1) != 0:
                if flBracket:
                    continue
                fl = True
            elif (token1 != ';') and (token2 == '\n'):
                if flBracket:
                    continue
                flV = True
                strV = s
            if token1 == 'else':
                if flBracket:
                    continue
                if lastStrWithV == s - 1:
                    textError = 'punctuation error: Did\'t wait ; before else, str'
                    print(textError, s - 1)  # запятая перед else
            elif token1 == '\n':
                if flBracket:
                    continue
                if flV and (strV == s):
                    continue
                if fl:
                    if lastStrWithV == s:
                        print('punctuation error: Did\'t wait ;, str', s)
                    fl = False
                else:
                    if lastStrWithV != s:
                        token3 = tokens[index - 1].lower()
                        if wordsWithIndent.count(token3) == 0:
                            print('punctuation error: Waited ;, str', s)
                s = s + 1
        elif (token1 == ';'):
            print('punctuation error: Did\'t wait ;, str', s)
        elif (token1 == '.'):
            break


def check_files():
    global tokens

    files = os.listdir(r'Tests')
    #print (files)
    for file in files:
        tokens = []
        s = 'Tests\\' + file
        print('\n' + file + ':')
        f = open(s)
        for line in f:
            tokenizator(line)
        # print(tokens)        
        check_style()
        check_tab()
        check_punctuation()
        # print(tokens)
        f.close()


def main():
    f = open('regulations.txt')
    for line in f:
        set_tab(line)
        set_doubleSigns(line)
        set_firstSigns(line)
        set_words_with_indent(line)
        set_words_without_punctuation(line)
        set_style(line)
        set_reserved_words(line)
        set_fixed_types(line)
    #print(reservedWords)
    f.close()
    check_files()


if __name__ == "__main__":
    openOperatorBracket = 'begin'
    closeOperatorBracket = 'end'

    tab = 0

    keywordStyle = "all small"
    variableStyle = "all small"
    constStyle = "all small"
    funcStyle = "all small"
    procedureStyle = "all small"
    typeStyle = "all small"
    recordStyle = "all small"

    wordsWithIndent = []
    wordsWithoutPunctuation = []
    reservedWords = []
    types = []
    doubleSigns = []
    firstSigns = []

    tokens = []
    variables = {}
    #consts = {}
    main()
