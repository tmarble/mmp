#!/usr/bin/env python3
# mmp
# Copyright (c) 2023 Tom Marble
# See LICENSE for details.

import argparse
import os
import os.path
import re
import sys

from typing import List, TextIO, Any, Pattern, Tuple, Dict
from attrs import define, field, validators
from lark import Lark, Transformer, Tree, Token
from lark import v_args # type: ignore
from lark.exceptions import UnexpectedToken, GrammarError, ConfigurationError, UnexpectedCharacters


array_keys = {
    'support-files': True,
    'prefs': True }

uq_keys = {
    'disabled': True,
    'reason': True,
    'run-sequentially': True,
    'tags': True, }

class IRToken(Token): # type: ignore
    """
    Customization of Token class to support pretty printing
    """
    mmp: Any = None

    def __init__(self, type: str, value: str, mmp: Any) -> None:
        self.type = type
        self.value = value
        self.mmp = mmp

    def __repr__(self):
        return 'IRToken(%r, %r)' % (self.type, self.value)

    def pretty_basic_string(self) -> str:
        return '"' + self + '"'

    def pretty_literal_string(self) -> str:
        return "'" + self + "'"

    def pretty_ml_basic_string(self) -> str:
        return '"""' + self + '"""'

    def pretty_ml_literal_string(self) -> str:
        return "'''" + self + "'''"

    def pretty_mp_logical_implicit(self) -> str:
        if self.mmp.write_toml and self.mmp.fix_implicit:
            return str(self)
        return ''

    def pretty_unquoted_string(self) -> str:
        if self.mmp.write_toml:
            return '"' + self + '"'
        return str(self)

    def pretty_ws_unquoted_string_val(self) -> str:
        v: str = str(self)
        if len(v) > 0 and self.mmp.write_toml:
            if v[0] == '#':
                v = ' ' + v
            return v.replace('\n', '')
        return v

    def pretty_prefs_quote(self) -> str:
        if self.mmp.write_toml:
            return str(self)
        return ''

    def pretty_ws_ini_newline(self) -> str:
        value = str(self)
        if self.mmp.write_toml:
            value = value.replace('\n', '')
        return value

    def _pretty(self, _level: int): # type: ignore
        if self.type == 'basic_string':
            yield self.pretty_basic_string()
        elif self.type == 'literal_string':
            yield self.pretty_literal_string()
        elif self.type == 'ml_basic_string':
            yield self.pretty_ml_basic_string()
        elif self.type == 'ml_literal_string':
            yield self.pretty_ml_literal_string()
        elif self.type == 'mp_logical_implicit':
            yield self.pretty_mp_logical_implicit()
        elif self.type == 'unquoted_string':
            yield self.pretty_unquoted_string()
        elif self.type == 'ws_unquoted_string_val':
            yield self.pretty_ws_unquoted_string_val()
        elif self.type == 'ws_ini_newline':
            yield self.pretty_ws_ini_newline()
        elif self.type == 'prefs_quote':
            yield self.pretty_prefs_quote()
        elif self.type == 'ws_ignore':
            pass
        else: # self.type == 'unquoted_key':
            yield str(self)

class IRTree(Tree): # type: ignore
    """
    Customization of Tree class to support pretty printing
    """
    table_key: Any = None
    mmp: Any = None
    array_values: List[Any] = []
    has_val: bool = False # used in _mp_expr_to_array to indicate array_value has a val

    def _hoist_comments(self, children: List[Any], remove_ws: bool=False, recurse: bool=True) -> str:
        """
        Hoist comments from this tree (to remove them from the mp_expr when printed as TOML)
        """
        regex = '#.*$'
        rx = re.compile(regex, re.MULTILINE)
        comments: str = ''
        for c in range(len(children)): # type: ignore
            child = children[c] # type: ignore
            if isinstance(child, IRTree) and recurse:
                comments += self._hoist_comments(child.children, remove_ws, recurse) # type: ignore
            if isinstance(child, IRToken) and (child.type == 'ws_comment_newline' or child.type == 'ws_comment_newline1'):
                value: str = str(child)
                start: int = 0
                content: str = ''
                while start < len(value):
                    m = rx.search(value, start)
                    if m:
                        (i, j) = m.span()
                        if not remove_ws:
                            if i > start:
                                content += value[start:i]
                            content += '\n'
                        comment = value[i:j]
                        comments += ' ' + comment
                        start = j + 1
                    else:
                        if not remove_ws:
                            content += value[start:]
                        break
                if content != value: # update child WITHOUT the comment
                    children[c] = IRToken(child.type, content, self.mmp) # type: ignore
        return comments

    def pretty_dotted_key(self, level: int, children: Any): # type: ignore
        if self.mmp.write_toml:
            yield '"'
        for child in children: # type: ignore
            yield from child._pretty(level) # type: ignore
        if self.mmp.write_toml:
            yield '"'

    def pretty_mp_expr(self, level: int): # type: ignore
        simple_token: bool = False
        if self.mmp.write_toml and level == 0:
            yield '"'
        # comments: str = ''
        # if self.mmp.write_toml and level == 0:
        #    yield " ''' "
        #    comments = self._hoist_comments(self.children) # type: ignore
        if len(self.children) == 1 and isinstance(self.children[0], IRToken): # type: ignore
            simple_token = True
        if self.mmp.debug_expr and not simple_token: # type: ignore
            yield '('
        for child in self.children: # type: ignore
            yield from child._pretty(level + 1) # type: ignore
        if self.mmp.debug_expr and not simple_token: # type: ignore
            yield ')'
        # if self.mmp.write_toml and level == 0:
        #    yield " ''' "
        #    yield comments
        if self.mmp.write_toml and level == 0:
            yield '"'

    def pretty_array_values(self, level: int, values: Any): # type: ignore
        seen_val: bool = False
        for child in values: # type: ignore
            if isinstance(child, Tree):
                if seen_val:
                    yield ','
                yield from child._pretty(level) # type: ignore
                if not self.mmp.write_toml: # TOML will handle array_sep explicitly
                    seen_val = True
            else:
                yield f'{child}'

    def _pretty(self, level: int, _indent_str: str = ''): # type: ignore
        if self.data == 'std_table' or self.data == 'mp_table':
            yield '['
            yield from self.table_key._pretty(level) # type: ignore
            yield ']'
        elif self.data == 'array':
            yield '['
            for child in self.children: # type: ignore
                yield from child._pretty(level) # type: ignore
            yield ']'
        elif self.data == 'implicit_array':
            if self.mmp.write_toml:
                yield '['
            one: bool = len(self.children) == 1 # type: ignore
            if not one:
                yield '\n'
            for child in self.children: # type: ignore
                if self.mmp.write_toml and not one:
                     yield '  '
                yield from child._pretty(level) # type: ignore
                if self.mmp.write_toml and not one:
                     yield ',\n'
            if self.mmp.write_toml:
                yield ']'
        elif self.data == 'array_values':
            yield from self.pretty_array_values(level, self.children) # type: ignore
        elif self.data == 'mp_expr':
            yield from self.pretty_mp_expr(level) # type: ignore
        elif self.data == 'unquoted_string_val' and self.mmp.write_toml: # write children in reverse order
            yield ' '
            for child in reversed(self.children): # type: ignore
                yield from child._pretty(level) # type: ignore
        else:
            for child in self.children: # type: ignore
                yield from child._pretty(level) # type: ignore
        if self.data == 'keynoval' and self.mmp.write_toml:
            yield " '' # no value from INI" # set empty value for keys without a value

@v_args() # type: ignore
class IRTransformer(Transformer): # type: ignore
    """
    Simplifies the parse tree into the IR
    """
    mmp: Any = None

    def __init__(self, visit_tokens: bool=True, mmp: Any=None) -> None:
        super().__init__(visit_tokens=visit_tokens)
        self.mmp = mmp

    def _debug_args(self, args: Tuple[Any], rule: str='') -> None:
        if self.mmp.verbose: # type: ignore
            if not rule:
                rule = sys._getframe().f_code.co_name # type: ignore
            self.mmp.err(f'{rule}: {len(args)}')
            for i in range(len(args)):
                if isinstance(args[i], Tree) and (args[i].data == 'std_table' or args[i].data == 'mp_table'):
                    self.mmp.err(f'  {i}: {args[i].__repr__()} [{args[i].table_key.__repr__()}] {type(args[i])}')
                else:
                    self.mmp.err(f'  {i}: {args[i].__repr__()} {type(args[i])}')
        if rule == 'expression':
            self.mmp.err('')

    def _mp_table_key(self, arg: Any) -> Token:
        value: str = ''
        if isinstance(arg, Tree):
            for child in arg.children: # type: ignore
                val = self._mp_table_key(child)
                value += str(val)
        else:
            value += str(arg)
        return IRToken('basic_string', value, self.mmp)

    def _token(self, args: Tuple[Any], value: str = '', debug: bool=True) -> Token:
        rule: str = sys._getframe(1).f_code.co_name # type: ignore
        if debug:
            self._debug_args(args, rule)
        if not value:
            if len(args) == 0:
                return None # type: ignore
            value = str(args[0])
        return IRToken(rule, value, self.mmp)

    def _token_combine(self, args: Tuple[Any], debug: bool=True) -> Token:
        rule: str = sys._getframe(1).f_code.co_name # type: ignore
        if debug:
            self._debug_args(args, rule)
        value: str = ''.join([token for token in args if token])
        return IRToken(rule, value, self.mmp)

    def _remove_empty_children(self, args: Tuple[Any]) -> List[Any]:
        children = []
        for arg in args:
            if arg != None:
                if isinstance(arg, IRTree):
                    children.append(arg) # type: ignore
                elif isinstance(arg, IRToken): # elide empty tokens
                    if arg.type.startswith('ws') and len(arg) == 0:
                        pass
                    else:
                        children.append(arg) # type: ignore
                else:
                    children.append(IRToken(arg.type, str(arg), self.mmp)) # type: ignore
        return children # type: ignore

    def _tree(self, args: Tuple[Any], children: List[Any] | None = None) -> IRTree:
        rule: str = sys._getframe(1).f_code.co_name # type: ignore
        self._debug_args(args, rule)
        if not children:
            children = self._remove_empty_children(args)
        tree = IRTree(rule, children)
        tree.mmp = self.mmp
        return tree

    def _val_should_not_be_mp_expr(self, key: str, args: Tuple[Any]) -> Tuple[bool, bool]:
        "Returns tuple of (should_not_be_mp_expr, key_ends_in_if)"
        should_not_be_mp_expr: bool = False
        key_ends_in_if: bool = False
        if isinstance(args[2], IRTree) and args[2].data == 'val': # type: ignore
            if len(args[2].children) == 1 and isinstance(args[2].children[0], IRTree) and args[2].children[0].data == 'mp_expr': # type: ignore
                if key.endswith('-if'): # type: ignore
                    key_ends_in_if = True
                    self.mmp.read_toml = False # we found a *-if keyval, thus we preserve the mp_expr
                else:
                    should_not_be_mp_expr = True # convert from mp_expr to unquoted_string or implicit_array
            elif self.mmp.write_toml and key.endswith('-if') and len(args[2].children) == 1 and isinstance(args[2].children[0], IRToken) and args[2].children[0].type == 'boolean': # type: ignore
                key_ends_in_if = True
                # coerce boolean type to appear as basic_string
                args[2].children[0].type = 'unquoted_key' # type: ignore
        return (should_not_be_mp_expr, key_ends_in_if)

    def _convert_mp_expr(self, key: str, children: List[Any], ia: Tree[Any] | None=None) -> Tree[Any]:
        if ia == None:
            ia = IRTree('implicit_array', [])
            ia.mmp = self.mmp
            ia = self._convert_mp_expr(key, children[2].children, ia) # type: ignore
            # if self.mmp.write_toml and not key in uq_keys:
            #     comments: str = ia._hoist_comments(ia.children, True, False) # type: ignore
            #     if len(comments) > 0: # type: ignore
            #         ia.children.append(IRToken('ws_comment_newline', comments + '\n', self.mmp))
            if len(ia.children) == 1 and key not in array_keys: # type: ignore
                # singleton value
                iav = ia.children[0]
                # if self.mmp.write_toml:
                #     comments: str = iav._hoist_comments(iav.children, True) # type: ignore
                #     if len(comments) > 0: # type: ignore
                #         iav.children.append(IRToken('ws_comment_newline', comments, self.mmp)) # type: ignore
                first = key in uq_keys and self.mmp.write_toml
                for child in iav.children: # type: ignore
                    if isinstance(child, IRToken):
                        if child.type == 'alpha_unquoted_key': # type: ignore
                            # unquoted keys need to be quoted in TOML values
                            child.type = 'unquoted_string' # type: ignore
                        elif child.type.startswith('ws'):
                            if child.find('\n') >= 0:
                                child.type = 'ws_ini_newline' # remove newlines for TOML
                            elif first:
                                child.type = 'ws_ignore' # remove leading whitespace
                    first = False
                children[2].children = iav.children # type: ignore
            else:
                children[2].children = [ia]
            keyval = IRTree('keyval', children)
            keyval.mmp = self.mmp
            return keyval
        iav = IRTree('implicit_array_value', [])
        iav.mmp = self.mmp
        if len(children) == 1 and isinstance(children[0], IRTree) and children[0].data == 'prefs_keyval': # type: ignore
            # handle prefs_keyval
            wschar: IRToken = children[0].children[0] # type: ignore
            wschar.type = 'ws_comment_newline'
            iav.children.append(wschar) # type: ignore
            iav.children.append(IRToken('prefs_quote', '"', self.mmp)) # type: ignore
            iav.children.append(children[0].children[1]) # type: ignore
            iav.children.append(children[0].children[2]) # type: ignore
            iav.children.append(children[0].children[3]) # type: ignore
            iav.children.append(IRToken('prefs_quote', '"', self.mmp)) # type: ignore
            ia.children.insert(0, iav)
        elif len(children) == 1 and isinstance(children[0], IRToken):
            # handle simple token
            token: IRToken = children[0] # type: ignore
            iav.children.append(token) # type: ignore
            ia.children.insert(0, iav)
        elif len(children) == 2 and isinstance(children[0], IRTree) and children[0].data == 'mp_not' and isinstance(children[1], IRToken): # type: ignore
            # handle mp_not token
            token: IRToken = children[1] # type: ignore
            token = IRToken(token.type, '!' + token, self.mmp) # type: ignore
            iav.children.append(token) # type: ignore
            ia.children.insert(0, iav)
        else:
            # review the children in reverse order
            for i in reversed(range(len(children))):
                child = children[i]
                if isinstance(child, IRTree):
                    if child.data == 'mp_expr':
                        ia = self._convert_mp_expr(key, child.children, ia) # type: ignore
                    else:
                        raise Exception(f'unexpected child of mp_expr: {child.__repr__()}')
                elif child.type == 'mp_logical_implicit':
                    pass # ignore
                elif child.type.startswith('ws_comment_newline'):
                    # add to the first iav
                    if len(ia.children) > 0:
                        iav = ia.children[0]
                        iav.children.insert(0, child)
                    else:
                        raise Exception(f'unexpected token at the end of an mp_expr: {child.__repr__()}')
                elif child.type == 'mp_not':
                    # add to the first TOKEN in iav
                    if len(ia.children) > 0:
                        iav = ia.children[0]
                        if len(iav.children) > 0 and isinstance(iav.children[0], IRToken):
                            iav.children[0] = IRToken(iav.children[0].type, '!' + iav.children[0], self.mmp) # type: ignore
                        else:
                            raise Exception(f'unexpected mp_not at the end of an mp_expr: {child.__repr__()}')
                    else:
                        raise Exception(f'unexpected token at the end of an mp_expr: {child.__repr__()}')
                else:
                    raise Exception(f'unexpected token in mp_expr: {child.__repr__()}')
        return ia # type: ignore

    def _mp_expr_to_array(self, children: List[Any], array: Tree[Any] | None=None) -> Tree[Any]:
        if array == None:
            array_value = IRTree('array_value', [])
            array_value.mmp = self.mmp
            array_values = IRTree('array_values', [array_value])
            array_values.mmp = self.mmp
            array = IRTree('array', [array_values])
            array.mmp = self.mmp
            array = self._mp_expr_to_array(children[2].children, array) # type: ignore
            # handle the last array_value
            array_values = array.children[0]
            array_value = array_values.children[-1]
            if array_value.has_val: # type: ignore
                # re-promote all (non leading ws) array_value children to mp_expr
                mp_expr: IRTree = IRTree('mp_expr', [], None)
                mp_expr.mmp = self.mmp
                i: int = 0
                while i < len(array_value.children) and isinstance(array_value.children[i], IRToken) and array_value.children[i].type.startswith('ws'): # type: ignore
                    i += 1
                mp_expr.children = array_value.children[i:] # type: ignore
                array_value.children = array_value.children[0:i] # type: ignore
                array_value.children.append(mp_expr) # here is your ONE mp_expr per line
                if self.mmp.write_toml and len(array_values.children) > 1:
                    array_value.children.append(IRToken('array_sep', ',\n', self.mmp)) # type: ignore
            # handle adding white space for a one-liner
            # if len(array_values.children) == 1:
            #     array_value = array_values.children[0]
            #     ws: str = ''
            #     i = 0
            #     while i < len(array_value.children) and isinstance(array_value.children[i], IRToken) and array_value.children[i].type.startswith('ws'): # type: ignore
            #         ws += str(array_value.children[i])
            #         i += 1
            #     if ws.find('\n') < 0:
            #         ws = '\n  ' + ws # start on next line
            #     array_value.children = array_value.children[i:] # type: ignore
            #     array_value.children.insert(0, IRToken('ws_comment_newline1', ws, self.mmp))
            # handle 0 or 1 vs 2+
            if self.mmp.write_toml:
                array_value = array_values.children[0]
                comments: str = array_value._hoist_comments(array_value.children, True, False) # type: ignore
                if len(comments) > 0: # type: ignore
                    array_value.children.append(IRToken('ws_comment_newline', comments + '\n', self.mmp))
                if len(array_values.children) > 1:
                    array_value.children.insert(0, IRToken('ws_comment_newline', '\n  ', self.mmp))
            # setup val
            children[2].children = [array]
            keyval = IRTree('keyval', children)
            keyval.mmp = self.mmp
            return keyval
        else:
            for i in range(len(children)):
                child = children[i]
                if isinstance(child, IRTree):
                    if child.data == 'mp_expr':
                        array = self._mp_expr_to_array(child.children, array) # type: ignore
                    else:
                        raise Exception(f'unexpected child of mp_expr: {child.__repr__()}')
                elif child.type == 'mp_logical_implicit':
                    pass # ignore
                else:
                    array_values = array.children[0]
                    array_value = array_values.children[-1]
                    if child.type.startswith('ws_comment_newline') and child.find('\n') >= 0:
                        if array_value.has_val: # type: ignore
                            # prepare next new array value
                            new_array_value = IRTree('array_value', []) # add comment to next array_value
                            new_array_value.mmp = self.mmp
                            # move ending whitespace to new_array_value below
                            while isinstance(array_value.children[-1], IRToken) and array_value.children[-1].type.startswith('ws'): # type: ignore
                                new_array_value.children.append(array_value.children.pop()) # type: ignore
                            # re-promote all (non leading ws) array_value children to mp_expr
                            mp_expr: IRTree = IRTree('mp_expr', [], None)
                            mp_expr.mmp = self.mmp
                            i: int = 0
                            while i < len(array_value.children) and isinstance(array_value.children[i], IRToken) and array_value.children[i].type.startswith('ws'): # type: ignore
                                i += 1
                            mp_expr.children = array_value.children[i:] # type: ignore
                            array_value.children = array_value.children[0:i] # type: ignore
                            array_value.children.append(mp_expr) # here is your ONE mp_expr per line
                            if self.mmp.write_toml:
                                array_value.children.append(IRToken('array_sep', ',', self.mmp)) # type: ignore
                            array_values.children.append(new_array_value)
                            array_value = new_array_value
                    if not child.type.startswith('ws'):
                        array_value.has_val = True # type: ignore
                    array_value.children.append(child) # type: ignore
        return array # type: ignore

    def _val_should_be_unquoted_string(self, args: Tuple[Any]) -> bool:
        if isinstance(args[2], IRTree) and args[2].data == 'val': # type: ignore
            if len(args[2].children) == 1 and isinstance(args[2].children[0], IRTree) and args[2].children[0].data == 'implicit_array': # type: ignore
                if isinstance(args[0], Tree) and args[0].data == 'key' and len(args[0].children) == 1 and isinstance(args[0].children[0], IRToken) and args[0].children[0].type == 'unquoted_key' and args[0].children[0] in uq_keys: # type: ignore
                    return True # convert from implicit_array to unquoted_string
        return False

    def _convert_unquoted_string(self, args: List[Any]) -> Tree[Any]:
        ia = args[2].children[0] # type: ignore
        unquoted_string = ''
        unquoted_start = ''
        for child in ia.children:
            if unquoted_string is None:
                break
            if isinstance(child, IRTree) and child.data == 'implicit_array_value':
                for token in child.children: # type: ignore
                    if unquoted_string is None:
                        break
                    if isinstance(token, IRToken): # type: ignore
                        if token.type == 'alpha_unquoted_key' or token.type == 'unquoted_string':
                            unquoted_string += str(token)
                        elif token.type.startswith('ws'):
                            if len(unquoted_string) > 0:
                                unquoted_string += str(token)
                            elif not self.mmp.write_toml:
                                unquoted_start = str(token)
                        else:
                            unquoted_string = None
                    else:
                        unquoted_string = None
            else:
                unquoted_string = None
        if unquoted_string is not None:
            args[2].children = [IRToken('ws_comment_newline1', unquoted_start, self.mmp),
                                IRToken('unquoted_string', unquoted_string, self.mmp)] # type: ignore
        return self._tree(args) # type: ignore

    def alpha(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def alpha_lower(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def alpha_upper(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def alpha_unquoted_key(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def array(self, args: Tuple[Any]) -> IRTree:
        return self._tree(args)

    def array_sep(self, args: Tuple[Any]) -> Token:
        return self._token(args)

    def array_values(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        array_values: Tree[Any] | None = None
        if isinstance(args[-1], Tree) and args[-1].data == 'array_values': # type: ignore
            array_values = args.pop() # type: ignore
        else:
            array_values = IRTree(rule, [], None)
            array_values.mmp = self.mmp
        if args[-1] is None or isinstance(args[-1], Token) and args[-1].type == 'array_sep': # type: ignore
            args.pop() # type: ignore
        array_value: IRTree = IRTree('array_value', self._remove_empty_children(args), None)
        array_value.mmp = self.mmp
        if self.mmp.write_toml:
            array_value.children.append(IRToken('array_sep', ',', self.mmp)) # type: ignore
        array_values.children.insert(0, array_value) # type: ignore
        return array_values # type: ignore

    def basic_char(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def basic_string(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def basic_unescaped(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def bin_int(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def bin_prefix(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def boolean(self, args: Tuple[Any]) -> Token:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        # self._debug_args(args, rule)
        value: str = 'true'
        if len(args) == 1 and isinstance(args[0], Tree) and isinstance(args[0].data, Token):
            value = str(args[0].data)
        return IRToken(rule, value, self.mmp)

    def colon(self, args: Tuple[Any]) -> Token:
        return self._token(args, ':', False)

    def comment(self, args: Tuple[Token]) -> Token:
        return self._token_combine(args, False)

    def date_fullyear(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def date_mday(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def date_month(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def date_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def dec_int(self, args: Tuple[Any]) -> Token:
        prefix: str = ''
        if args[0]:
            prefix = str(args[0])
        value: str = prefix + args[1] # type: ignore
        return self._token(args, value)

    def digit(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def digit0_1(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def digit0_7(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def digit1_9(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def dot(self, args: Tuple[Any]) -> Token:
        return self._token(args, '.', False)

    def dotted_key(self, args: Tuple[Any]) -> Tree[Any]:
        return self._tree(args)

    def dot_sep(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def e(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def equals(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def escaped(self, args: Tuple[Any]) -> Token:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        # self._debug_args(args, rule)
        e = args[0]
        escape = e.children[0] # type: ignore
        value: str = ''
        if escape == '"' or escape == '\\':
            value = '\\' + str(escape)
        elif escape == 'b':
            value = '\\b'
        elif escape == 'f':
            value = '\\f'
        elif escape == 'n':
            value = '\\n'
        elif escape == 'r':
            value = '\\r'
        elif escape == 't':
            value = '\\t'
        elif escape == 'x':
            value = '\\x'
            for i in range(2):
                value += e.children[i+1] # type: ignore
        elif escape == 'u':
            value = '\\u'
            for i in range(4):
                value += e.children[i+1] # type: ignore
        elif escape == 'U':
            value = '\\U'
            for i in range(8):
                value += e.children[i+1] # type: ignore
        return IRToken(rule, value, self.mmp)

    def exp(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def expression(self, args: Tuple[Any]) -> None | Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        children = []
        first = True
        for child in args:
            if child is not None:
                if isinstance(child, Tree) or child.type == 'comment':
                    children.append(child) # type: ignore
                elif child.type.startswith('ws'):
                    if len(child) > 0 and (not self.mmp.write_toml or not first):
                        children.append(child) # type: ignore
            first = False
        if len(children) == 0: # type: ignore
            return None
        tree: IRTree = IRTree('expression', children, None)
        tree.mmp = self.mmp
        return tree

    def float(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def float_int_part(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def float_exp_part(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def frac(self, args: Tuple[Any]) -> Token:
        return self._token(args, '.' + args[0], False)

    def full_date(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def full_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def hexdig(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def hex_int(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def hex_prefix(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def implicit_array(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        implicit_array: Tree[Any] | None = None
        if isinstance(args[-1], Tree) and args[-1].data == 'implicit_array': # type: ignore
            implicit_array = args.pop() # type: ignore
        else:
            implicit_array = IRTree(rule, [], None)
            implicit_array.mmp = self.mmp
            implicit_array_value1: IRTree = IRTree('implicit_array_value', list(args[2:4]), None)
            implicit_array_value1.mmp = self.mmp
            implicit_array.children.append(implicit_array_value1) # type: ignore
            args.pop() # type: ignore
            args.pop() # type: ignore
        implicit_array_value0: IRTree = IRTree('implicit_array_value', list(args), None)
        implicit_array_value0.mmp = self.mmp
        implicit_array.children.insert(0, implicit_array_value0) # type: ignore
        return implicit_array # type: ignore

    def integer(self, args: Tuple[Any]) -> Token:
        return self._token(args)

    def key(self, args: Tuple[Any]) -> Tree[Any]:
        return self._tree(args)

    def keynoval(self, args: Tuple[Any]) -> Tree[Any]:
        self.mmp.read_toml = False # Illegal TOML syntax found
        return self._tree(args)

    def keyval(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        key: str = ''
        if isinstance(args[0], Tree) and args[0].data == 'key' and len(args[0].children) == 1 and isinstance(args[0].children[0], IRToken) and args[0].children[0].type == 'unquoted_key': # type: ignore
            key = args[0].children[0] # type: ignore
        should_not_be_mp_expr: bool = False
        key_ends_in_if: bool = False
        (should_not_be_mp_expr, key_ends_in_if) = self._val_should_not_be_mp_expr(key, args)
        if should_not_be_mp_expr:
            tree = self._convert_mp_expr(key, children=list(args))
            if self._val_should_be_unquoted_string(tree.children): # type: ignore
                tree = self._convert_unquoted_string(tree.children) # type: ignore
        elif key_ends_in_if:
            tree = self._mp_expr_to_array(list(args))
        else:
            tree = self._tree(args=args)
        return tree

    def keyval_sep(self, args: Tuple[Any]) -> Token:
        if self.mmp.write_toml:
            return IRToken('keyval_sep', ' = ', self.mmp)
        return self._token_combine(args, False)

    def literal_string(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def literal_char(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def local_date(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def local_date_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def local_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def lparen(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def manifest(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        children: List[Any] = []
        for child in args:
            if child != None:
                children.append(child)
        tree: IRTree = IRTree(rule, children, None)
        tree.mmp = self.mmp
        return tree

    def minus(self, args: Tuple[Any]) -> Token:
        return self._token(args, '-', False)

    def ml_basic_body(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, True)

    def ml_basic_string(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def ml_literal_body(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def ml_literal_string(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def mlb_char(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def mlb_content(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def mlb_escaped_nl(self, args: Tuple[Any]) -> Token:
        value: str = '\\'
        for arg in args:
            if arg != None:
                value += arg
        return self._token(args, value, False)

    def mlb_quotes(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def mll_content(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def mll_quotes(self, args: Tuple[Any]) -> Token:
       return self._token_combine(args, False)

    def mp_expr(self, args: Tuple[Any]) -> Tree[any]: # type: ignore
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        # NOTE: will defer final type of mp_expr when resolved as a keyval
        # self.mmp.read_toml = False # Illegal TOML syntax found
        tree: IRTree = IRTree(rule, [], None)
        tree.mmp = self.mmp
        if len(args) == 3 and isinstance(args[0], Tree) and args[0].data == 'mp_expr':
            # IMPLICIT OR
            tree.children = list(args)
            tree.children.insert(1, IRToken('mp_logical_implicit', ' ||', self.mmp)) # type: ignore
        else:
            for arg in args:
                if arg:
                    if isinstance(arg, Token) and arg.type == 'ws_comment_newline' and len(arg) == 0:
                        pass
                    else:
                        tree.children.append(arg) # type: ignore
        return tree

    def mp_op(self, args: Tuple[Any]) -> Token:
        return self._token(args)

    def mp_logical(self, args: Tuple[Any]) -> Token:
        return self._token(args)

    def mp_not(self, args: Tuple[Any]) -> Token:
        return self._token(args, '!')

    def mp_table(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        self.mmp.read_toml = False # Illegal TOML syntax found
        tree = IRTree(rule, [], None)
        tree.mmp = self.mmp
        if self.mmp.write_toml:
            tree.table_key = self._mp_table_key(args[1]) # type: ignore
        else:
            tree.table_key = args[1] # type: ignore
        return tree

    def mp_terminal(self, args: Tuple[Any]) -> Tree[Any]:
        token = args[0]
        if self.mmp.write_toml and token.type == 'basic_string':
            token.type = 'literal_string'
        return token

    def newline(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def oct_int(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def oct_prefix(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def offset_date_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def partial_time(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def plus(self, args: Tuple[Any]) -> Token:
        return self._token(args, '+', False)

    def prefs_keyval(self, args: Tuple[Any]) -> Tree[Any]:
        children = list(args)
        if self.mmp.write_toml: # convert WSCHAR to empty ws_comment_newline
            children[0] = IRToken('ws_comment_newline', '', self.mmp)
        return self._tree(args, children) # explicitly preserve empty ws_comment_newline

    def rparen(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def simple_key(self, args: Tuple[Any]) -> Token:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        return args[0] # preserve string type

    def special_float(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def std_table(self, args: Tuple[Any]) -> Tree[Any]:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        tree = IRTree(rule, [], None)
        tree.mmp = self.mmp
        tree.table_key = args[1] # type: ignore
        if self.mmp.write_toml:
            tree.table_key = self._mp_table_key(args[1]) # type: ignore
        else:
            tree.table_key = args[1] # type: ignore
        return tree

    def string(self, args: Tuple[Any]) -> Token:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        return IRToken(args[0].type, str(args[0]), self.mmp) # preserve string type

    def time_delim(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def table(self, args: Tuple[Any]) -> Tree[Any]:
        return args[0]

    def time_hour(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def time_minute(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def time_numoffset(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def time_offset(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def time_secfrac(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def time_second(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def quoted_key(self, args: Tuple[Any]) -> Token:
        rule: str = sys._getframe().f_code.co_name # type: ignore
        self._debug_args(args, rule)
        return args[0] # preserve string type

    def underscore(self, args: Tuple[Any]) -> Token:
        return self._token(args, '_', False)

    def unquoted_char(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def unquoted_key(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def unquoted_string(self, args: Tuple[Any]) -> Token:
        self.mmp.read_toml = False # Illegal TOML syntax found
        return self._token_combine(args, False)

    def unquoted_string_val(self, args: Tuple[Any]) -> Tree[any]: # type: ignore
        self.mmp.read_toml = False # Illegal TOML syntax found
        children: List[Any] = []
        children.append(IRToken('ws_unquoted_string_val', str(args[0]), self.mmp))
        children.append(args[1]) # type: ignore
        return self._tree(children) # type: ignore

    def unsigned_dec_int(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args)

    def val(self, args: Tuple[Any]) -> Tree[Any]:
        return self._tree(args)

    def ws(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def ws_comment_newline(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def ws_comment_newline1(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

    def z(self, args: Tuple[Any]) -> Token:
        return self._token(args, '', False)

    def zero_prefixable_int(self, args: Tuple[Any]) -> Token:
        return self._token_combine(args, False)

@define
class MetaManifestParser:
    """
    Meta Manifest Parser is the main class for the mmp program.
    """
    argv: List[str] = field(validator=validators.deep_iterable(
                                member_validator=validators.instance_of(type=str),
                                iterable_validator=validators.instance_of(type=list)),
                            default=['mmp.py'])
    debug_expr: bool = field(validator=validators.instance_of(type=bool), default=False) # type: ignore
    errfile: TextIO = field(default=sys.stderr)
    fix_implicit: bool = field(validator=validators.instance_of(type=bool), default=False) # type: ignore
    ignore_includes: bool = field(validator=validators.instance_of(type=bool), # type: ignore
                                  default=False)
    ini_files: Dict[str, bool] = field(default={}) # type: ignore
    ir_ebnf: str = field(validator=validators.instance_of(type=str), # type: ignore
                         default='') # type: ignore
    match: str = field(default='(mochitest|chrome|a11y|browser|xpcshell)\x2Eini')
    regex: Pattern[str] = field(default=None)
    read_toml: bool = field(validator=validators.instance_of(type=bool), default=True) # type: ignore
    outfile: TextIO = field(default=sys.stdout)
    topsrcdir: str = field(validator=validators.instance_of(type=str), # type: ignore
                           default='')
    verbose: bool = field(validator=validators.instance_of(type=bool), # type: ignore
                          default=False)
    strict_toml: bool = field(validator=validators.instance_of(type=bool), default=False) # type: ignore
    write_toml: bool = field(validator=validators.instance_of(type=bool), default=True) # type: ignore

    def out(self, a: Any, end: str = '\n') -> None:
        "Print to outfile (STDOUT)"
        print(a, file=self.outfile, end=end)

    def out2(self, a: Any, b: Any, end: str = '\n') -> None:
        print(a, b, file=self.outfile, end=end)

    def err(self, a: Any) -> None:
        "Print to error file (STDERR)"
        print(a, file=self.errfile) # type: ignore

    def err2(self, a: Any, b: Any) -> None:
        print(a, b, file=self.errfile) # type: ignore

    def verr(self, a: Any) -> None:
        "Print to error file (STDERR) if in verbose mode"
        if self.verbose:
            self.err(a)

    def verr2(self, a: Any, b: Any) -> None:
        if self.verbose:
            self.err2(a, b)

    def run(self) -> int:
        rc: int = 0
        program: str = os.path.basename(p=sys.argv[0])
        if len(self.argv) == 1:
            if program == 'ipykernel_launcher.py': # running in vs code
                program = 'mmp.py'
                self.argv = [program, '--help']
            else:
                self.argv = sys.argv
        sys.argv = self.argv
        topsrcdir: str = '.'
        if 'MOZILLA_CENTRAL' in os.environ:
            topsrcdir: str = os.environ['MOZILLA_CENTRAL']
        parser = argparse.ArgumentParser('Meta Manifest Parser')
        # OPTIONS ----------------------------------------
        parser.add_argument('-v', '--verbose',
                            help='Prints details of each action',
                            action='store_true', required=False)
        topsrcdir: str = '.'
        if 'MOZILLA_CENTRAL' in os.environ:
            topsrcdir: str = os.environ['MOZILLA_CENTRAL']
        parser.add_argument('-D', '--debug-expr',
                            help='Add explicit parens around each MP expression',
                            action='store_true', required=False)
        parser.add_argument('-F', '--fix-implicit',
                            help='Fix implicit MP logical expressions',
                            action='store_true', required=False)
        parser.add_argument('-t', '--topsrcdir',
                            help=f'Path to mozilla-central [{topsrcdir}]',
                            default=topsrcdir, required=False)
        parser.add_argument('-T', '--strict-toml',
                            help='Will fail if input is not valid TOML',
                            action='store_true', required=False)
        parser.add_argument('-j', '--ignore-includes',
                            help='Ignore ini files that include other ini files',
                            action='store_true', required=False)
        parser.add_argument('-k', '--keep-dotted',
                            help='Preserve dotted keys in table names',
                            action='store_true', required=False)
        parser.add_argument('-m', '--match',
                            help=f'file match regex [{self.match}]',
                            default=self.match, required=False)
        parser.add_argument('-o', '--output-file',
                            help=f'Write to file [STDOUT]',
                            default=None, required=False)
        parser.add_argument('-W', '--write-ini',
                            help=f'Write as INI',
                            action='store_true', required=False)
        # ACTIONS ----------------------------------------
        parser.add_argument('-f', '--find-ini',
                            help='Identify manifestparser ini files',
                            action='store_true', required=False)
        parser.add_argument('-r', '--read-ini',
                            help=f'Read an ini file',
                            default=None, required=False)
        args: argparse.Namespace = parser.parse_args()
        self.verbose = args.verbose
        self.ignore_includes = args.ignore_includes
        self.write_toml = not args.write_ini
        self.strict_toml = args.strict_toml
        self.debug_expr = args.debug_expr
        self.fix_implicit = args.fix_implicit
        if args.output_file:
            self.outfile = open(file=args.output_file, mode='w')
        if self.verbose:
            self.err(f'topsrcdir: {args.topsrcdir}')
            self.err(f'ignore_includes: {self.ignore_includes}')
            self.err(f'match: {args.match}')
            self.err(f'output-file: {"STDOUT" if self.outfile == sys.stdout else args.output_file}')
            self.err(f'write-ini: {not self.write_toml}')
            self.err(f'strict-toml: {self.strict_toml}')
            self.err(f'debug-expr: {self.debug_expr}')
            self.err(f'fix-implicit: {self.fix_implicit}')
        if not self.validate_topsrcdir(args.topsrcdir):
            self.err(f'topsrcdir invalid: "{args.topsrcdir}"')
            rc = 1
        elif not self.validate_match(args.match):
            self.err(f'match invalid: "{args.match}"')
            rc = 1
        elif args.find_ini:
            rc = 0 if self.find_ini() else 1
        elif args.read_ini:
            rc = 0 if self.initialize_parser() and self.read_ini(args.read_ini) else 1
        else:
            self.err('No action specified, see mmp.py --help')
            rc = 1
        self.outfile.close()
        return rc

    def validate_topsrcdir(self, topsrcdir: str) -> bool:
        """
        Ensure topsrcdir is a valid mozilla-central directory.
        """
        (drive, tail) = os.path.splitdrive(p=topsrcdir)
        if len(tail) == 0:
            self.err('topsrcdir is empty')
            return False
        if tail[0] != os.sep:
            tail = os.path.join(os.getcwd(), tail)
        else:
            tail = drive + tail
        self.topsrcdir = os.path.normpath(tail)
        if not os.path.isdir(self.topsrcdir):
            self.err('topsrcdir is not a directory')
            return False
        mach: str = os.path.join(self.topsrcdir, 'mach')
        if not os.path.exists(mach):
            self.err('topsrcdir is not a firefox repo')
            return False
        return True

    def validate_match(self, match: str) -> bool:
        """
        Ensure match is a valid regular expression.
        """
        self.match = match
        self.regex = re.compile(match)
        return True

    def read_binary_file_as_string(self, fullpath: str) -> str | None:
        """
        Returns contents of the file as a string (or None on error)
        """
        try:
            file = open(file=fullpath, mode="rb") # binary to preserve CRLF
        except FileNotFoundError as e:
            self.err(f'{e}')
            return None
        try:
            text: str = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return None
        file.close()
        return text

    def read_file_as_string(self, fullpath: str) -> str | None:
        """
        Returns contents of the file as a string (or None on error)
        """
        try:
            file = open(file=fullpath, mode="r")
        except FileNotFoundError as e:
            self.err(f'{e}')
            return None
        try:
            text: str = file.read()
        except UnicodeDecodeError:
            return None
        file.close()
        return text

    def check_for_includes(self, path: str, indent: int=0) -> None:
        """
        Prints fullpath if it includes a section `[include`
        Then recursively follows include path.
        """
        ini: str | None = self.read_file_as_string(os.path.join(self.topsrcdir, path))
        if ini == None:
            return
        pad = '  ' * indent
        if ini.find('[include:') >= 0:
            self.ini_files[path] = True
            self.verr(f'{pad}INCLUDES found in {path}:')
            regex = '\\[include:([^\\]]+)\\]'
            rx = re.compile(regex, re.MULTILINE)
            start: int = 0
            while start < len(ini):
                m = rx.search(ini, start)
                if m:
                    (i, j) = m.span()
                    if i >= start:
                        include_filename = ini[i+9:j-1]
                        self.verr(f'{pad}INCLUDE={include_filename}=')
                        include_path = os.path.join(os.path.dirname(path), include_filename)
                        include_path = os.path.realpath(include_path)
                        include_path = '.' + include_path[len(self.topsrcdir):] # make path relative
                        self.ini_files[include_path] = True
                        self.check_for_includes(include_path, indent+1)
                    start = j + 1
                else:
                    break

    def find_ini(self) -> bool:
        """
        Prints relative path of each matching *.ini file
        """
        self.ini_files = {}
        for root, _dirs, files in os.walk(self.topsrcdir, topdown=True):
            for file in files:
                if file.endswith('.ini'):
                    fullpath: str = os.path.join(root, file)
                    path = '.' + fullpath[len(self.topsrcdir):] # make path relative
                    if not path.startswith('./obj-'): # ignore build directories
                        if self.regex.fullmatch(file):
                            self.ini_files[path] = True
                        if not self.ignore_includes:
                            self.check_for_includes(path)
        for f in sorted(self.ini_files.keys()):
            self.out(f)
        return True

    def initialize_parser(self) -> bool:
        """
        Initializes the parser from the ir.ebnf file
        """
        pdir: str = os.path.dirname(p=sys.argv[0])
        ir_ebnf_path = os.path.join(pdir, 'ir.ebnf')
        if not os.path.exists(ir_ebnf_path):
            self.err(f'ir.ebnf not found: {ir_ebnf_path}')
            return False
        ir_ebnf: str | None = self.read_file_as_string(ir_ebnf_path)
        if ir_ebnf == None:
            self.err(f'cannot read ir.ebnf: {ir_ebnf_path}')
            return False
        self.ir_ebnf = ir_ebnf
        return True

    def read_ini(self, ini_file: str) -> bool:
        """
        Reads the given *.ini file
        """
        fullpath: str = os.path.join(self.topsrcdir, ini_file)
        ini: str | None = self.read_binary_file_as_string(fullpath)
        if ini == None:
            return False
        try:
            parser = Lark(self.ir_ebnf, parser='earley', start='manifest')
        except GrammarError as e:
            self.err(f'GrammarError with ir.ebnf: {e}')
            return False
        except ConfigurationError as e:
            self.err(f'ConfigurationError with ir.ebnf: {e}')
            return False
        try:
            manifest = parser.parse(ini)
        except UnexpectedToken as e:
            self.err(f'parsing error: {e}')
        except UnexpectedCharacters as e:
            self.err(f'parsing error: {e}')
            return False
        self.verr("==TRANSFORM==")
        self.read_toml = True # assume TOML
        manifest: Tree[Token] = IRTransformer(True, self).transform(manifest) # type: ignore
        self.verr(f"== File is legal TOML? {self.read_toml} ==")
        self.verr("==PLAIN==")
        self.verr(manifest)
        if not self.read_toml and self.strict_toml:
            self.err('error: input is not strict TOML')
            return False
        self.verr(f"== PRETTY as TOML? {self.write_toml}==")
        self.out(manifest.pretty()) # type: ignore
        return True

if __name__ == "__main__":
    sys.exit(MetaManifestParser().run())
