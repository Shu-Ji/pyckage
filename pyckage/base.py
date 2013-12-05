# !/usr/bin/env python
# coding: u8


import re


class HtmlError(Exception):
    def __init__(self, ele):
        self.ele = ele
        Exception.__init__(self)

    def __str__(self):
        return 'more than one `id` found in: `%s`' % self.ele


class InputTypeError(Exception):
    def __init__(self, ele):
        self.ele = ele
        Exception.__init__(self)

    def __str__(self):
        return 'invalid type of input: `%s`' % self.ele


class Constant(object):
    # tag type
    BLOCK_COMMENT = 0
    LINE_COMMENT = 1
    HTML_OPEN_TAG = 2
    HTML_CLOSED_TAG = 3
    EMPTY_LINE = 4
    PLAIN_TEXT = 5

    # open tags
    OPEN_TAGS = ('area', 'base', 'basefont', 'br', 'col', 'embed', 'frame',
            'hr', 'img', 'input', 'keygen', 'link', 'menuitem', 'meta',
            'param', 'source', 'track', 'wbr')


class Node(object):
    def __init__(self, line):
        self.has_children = False
        self.left = self.right = None
        self.children = []
        self.type = self.query2node(line)
        print (self.type, self.has_children, self.left, self.right)
        print

    def query2node(self, line):
        line = line.strip()
        if isinstance(line, str):
            line = line.decode('u8')

        print '=' * 20, repr(line)
        if not line:
            return Constant.EMPTY_LINE
        if line == '#:':
            return Constant.BLOCK_COMMENT
        if line.startswith('##'):
            return Constant.LINE_COMMENT
        if line.startswith('-'):
            return Constant.PLAIN_TEXT

        # remove the inline comment
        line = re.sub(r'\s+##.*$', '', line)

        if not re.match(ur'^'  # must starts with:
                ur'(\w)'  # letter
                ur'|'  # or
                ur'([@.:#]\w)'  # @for, .btn, :password, #btn-login
                ur'|'  # or
                ur'(#:$)'  # #: block comment
                ur'|'  # or
                ur'-'  # -plain text
                , line):
            raise SyntaxError('`%s`' % line)
        has_children = line.endswith(':')

        line = re.sub(r'\s+:$', ':', line)  # trim whitespace before `:`

        # split element and attributes
        ele_attrs = line.split(' ', 1)
        if len(ele_attrs) == 1:  # no attribute: `div.btn:`
            attrs = ''
            ele = ele_attrs[0]
            if has_children:  # trim the tail `:`
                ele = ele[:-1]
        else:
            ele, attrs = ele_attrs
            if has_children:
                attrs = attrs[:-1]

        # attrs
        if attrs:
            equal_re = re.compile(r' *= *')
            comma_re = re.compile(r' *, *')
            _attrs = {}
            for attr in comma_re.split(attrs):
                attr = equal_re.split(attr.strip(), 1)
                if len(attr) > 1:  # attr has value
                    attr0, attr1 = attr
                else:  # such as `checked`, `autofocus`, `required`, ...
                    attr0, attr1 = attr[0], None
                _attrs[attr0] = attr1
            attrs = _attrs
        else:
            attrs = {}

        # deal with something special
        if re.match(r'^[#.]\w', ele):  # `.btn#btn` means `div.btn#btn`
            ele = u'div%s' % ele
        elif ele[0] == ':':  # `:text.username` means `input:text.username`
            ele = u'input%s' % ele

        # input type
        if ele.startswith('input:'):
            try:
                input_type = re.findall(r'^(input:(\w+))', ele)[0]
            except IndexError:
                raise InputTypeError(ele)
            ele = 'input%s' % ele[len(input_type[0]):]
            attrs['type'] = input_type[1]

        tag = re.finditer('\w+', ele).next().group(0)
        id_class = ele[len(tag):]

        id = re.findall(r'#([^.#]+)', id_class)
        if len(id) > 1:
            raise HtmlError(ele)
        if id:
            attrs['id'] = id[0]
        cls = re.findall(r'\.([^.#]+)', id_class)
        if cls:
            cls = ' '.join(cls)
            _cls = attrs.pop('class', '')
            attrs['class'] = cls + ' ' + _cls

        _attrs = []
        for k, v in attrs.iteritems():
            if v is None:
                _attrs.append(k)
            else:
                _attrs.append('%s="%s"' % (k, v.strip()))
        attrs = ' '.join(_attrs)
        if tag in Constant.OPEN_TAGS:
            self.left = '<%s %s />' % (tag, attrs)
            self.right = None
        else:
            if attrs:
                attrs = ' ' + attrs
            self.left = '<%s%s>' % (tag, attrs)
            self.right = '</%s>' % tag
        self.has_children = has_children

    def add_child(self, child):
        self.children.append(child)


class Template(object):
    def __init__(self, source, **kwargs):
        self.code = None
        self.format_func = kwargs.pop('format_func', None)
        self.parser(source)

    def parser(self, source):
        source_lines = []
        block_lines = []
        oneindent = ' '
        indention = 0
        def write(self, offset, data):
            source_lines.append(( oneindent * (indention - offset)) + data)

        def format_indent(data):
            space_num = 0
            deal_space_num = False
            new_lines = []
            current_indent = oneindent * indention

            for line in data.splitlines():
                if deal_space_num == False and line.strip():
                    space_num = len(line) - len(line.lstrip())
                    deal_space_num = True

                new_lines.append(current_indent + line[space_num:])
            return '\n'.join(new_lines)
        self.tokenize(source)

    def tokenize(self, source):
        if isinstance(source, str):
            source = source.decode('u8')
        if isinstance(source, unicode):
            source = source.splitlines()
        for indention, line in self.lines(source):
            Node(line)

    def get_variable(self, value):
        if self.format_func is not None:
            value = self.format_func(value)
        isinst = lambda t: isinstance(value, t)
        if isinst(unicode):
            return value.encode('u8')
        elif not isinst(str):
            return str(value)
        return value

    def render(self, *args, **kwargs):
        lines = []
        d = dict(*args, **kwargs)
        d['__write'] = lines.append
        d['__write_var'] = lambda x: lines.append(self.get_variable(x))
        d['__get_var'] = lambda x: self.get_variable(x)
        exec self.code in d
        return ''.join(lines)

    @staticmethod
    def lines(all):
        last = ''
        p = re.compile(r'^ +')
        for line in all:
            line = line.rstrip()
            if line:
                if last:
                    line = '%s%s' % (last, line)
                    last = ''
                if line[-1] in ('\\', ','):
                    last = line
                else:
                    m = p.match(line)
                    indention = 0
                    if m is not None:
                        indention = len(m.group(0))
                    if indention % 4 != 0:
                        raise IndentationError(
                                '`%s`\n\n\tindention must be divisible by 4, '
                                'got %s' % (line, indention))
                    yield indention, line.lstrip()


def test():
    with open('main.pyt') as f:
        Template(f)
    return
    Node('#:')
    Node('.btn.btn-primary#btn-login href=/login, data-url=#test:')
    Node(':text.username class=btn #btn-p, required, autofocus, value=登录')


if __name__ == '__main__':
    test()
