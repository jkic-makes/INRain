#!/usr/bin/env python3
"""
INRain - a super simple beginner scripting language.
Runs .inr and .inrain files.

Syntax examples:
    print Hello World!
    set name = Bob
    print Hello, {name}!
    ask name What is your name?
    if name == Bob:
        print Nice name!
    end
    loop 5:
        print Looping!
    end
    wait 2
    run dir
    gui Hello There        (opens a simple window with text)
    button Click Me -> print You clicked!
    input_box               (opens a GUI popup to ask for text, stores in 'answer')
"""

import sys
import os
import re
import time
import subprocess

try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    HAS_GUI = True
except Exception:
    HAS_GUI = False


class INRainError(Exception):
    pass


def strip_comment(line):
    # allow # comments, but not inside {} substitutions
    out = []
    in_brace = False
    for ch in line:
        if ch == '{':
            in_brace = True
        if ch == '}':
            in_brace = False
        if ch == '#' and not in_brace:
            break
        out.append(ch)
    return ''.join(out)


def substitute(text, variables):
    def repl(match):
        key = match.group(1).strip()
        return str(variables.get(key, '{' + key + '}'))
    return re.sub(r'\{([^}]+)\}', repl, text)


def to_value(token, variables):
    token = token.strip()
    if token in variables:
        return variables[token]
    # try number
    try:
        if '.' in token:
            return float(token)
        return int(token)
    except ValueError:
        pass
    # strip quotes if present
    if (token.startswith('"') and token.endswith('"')) or \
       (token.startswith("'") and token.endswith("'")):
        return token[1:-1]
    return token


def eval_condition(cond, variables):
    cond = cond.strip()
    for op in ['==', '!=', '>=', '<=', '>', '<']:
        if op in cond:
            left, right = cond.split(op, 1)
            lv = to_value(left.strip(), variables)
            rv = to_value(right.strip(), variables)
            try:
                lv_num, rv_num = float(lv), float(rv)
                lv, rv = lv_num, rv_num
            except (ValueError, TypeError):
                lv, rv = str(lv), str(rv)
            if op == '==':
                return lv == rv
            if op == '!=':
                return lv != rv
            if op == '>=':
                return lv >= rv
            if op == '<=':
                return lv <= rv
            if op == '>':
                return lv > rv
            if op == '<':
                return lv < rv
    # bare variable truthy check
    val = to_value(cond, variables)
    return bool(val) and val != 0 and val != '0'


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.gui_root = None

    def get_gui_root(self):
        if not HAS_GUI:
            raise INRainError("GUI features need tkinter, which isn't installed.")
        if self.gui_root is None:
            self.gui_root = tk.Tk()
            self.gui_root.title("INRain")
        return self.gui_root

    def run_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()
        lines = [strip_comment(l.rstrip('\n')) for l in raw_lines]
        self.run_block(lines, 0, len(lines))
        if self.gui_root is not None:
            self.gui_root.mainloop()

    def find_matching_end(self, lines, start):
        """Given index of a line ending in ':' find index of its 'end'."""
        depth = 1
        i = start + 1
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.endswith(':') and (
                stripped.startswith('if ') or stripped.startswith('loop ') or
                stripped.startswith('while ') or stripped.startswith('for ')
            ):
                depth += 1
            elif stripped == 'end':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        raise INRainError(f"Missing 'end' for block starting at line {start+1}")

    def run_block(self, lines, start, stop):
        i = start
        while i < stop:
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            try:
                if stripped.startswith('if ') and stripped.endswith(':'):
                    cond = stripped[3:-1].strip()
                    end_idx = self.find_matching_end(lines, i)
                    # find optional 'else' at same depth
                    else_idx = self.find_else(lines, i + 1, end_idx)
                    if eval_condition(cond, self.variables):
                        body_end = else_idx if else_idx else end_idx
                        self.run_block(lines, i + 1, body_end)
                    elif else_idx:
                        self.run_block(lines, else_idx + 1, end_idx)
                    i = end_idx + 1
                    continue

                if stripped.startswith('loop ') and stripped.endswith(':'):
                    count_expr = stripped[5:-1].strip()
                    count = int(to_value(count_expr, self.variables))
                    end_idx = self.find_matching_end(lines, i)
                    for _ in range(count):
                        self.run_block(lines, i + 1, end_idx)
                    i = end_idx + 1
                    continue

                if stripped.startswith('while ') and stripped.endswith(':'):
                    cond = stripped[6:-1].strip()
                    end_idx = self.find_matching_end(lines, i)
                    while eval_condition(cond, self.variables):
                        self.run_block(lines, i + 1, end_idx)
                    i = end_idx + 1
                    continue

                if stripped == 'end' or stripped == 'else:' or stripped == 'else':
                    i += 1
                    continue

                self.run_line(stripped)
            except INRainError as e:
                print(f"[INRain error] line {i+1}: {e}")
            i += 1

    def find_else(self, lines, start, end_idx):
        depth = 0
        i = start
        while i < end_idx:
            s = lines[i].strip()
            if s.endswith(':') and (s.startswith('if ') or s.startswith('loop ') or s.startswith('while ')):
                depth += 1
            elif s == 'end':
                depth -= 1
            elif s in ('else', 'else:') and depth == 0:
                return i
            i += 1
        return None

    def run_line(self, line):
        v = self.variables

        # print Hello World!
        if line.startswith('print '):
            text = line[6:]
            print(substitute(text, v))
            return
        if line == 'print':
            print()
            return

        # set name = Bob
        if line.startswith('set '):
            rest = line[4:]
            if '=' not in rest:
                raise INRainError("set needs an '=' e.g. set x = 5")
            name, expr = rest.split('=', 1)
            name = name.strip()
            expr = expr.strip()
            v[name] = self.eval_expr(expr)
            return

        # ask name What is your name?
        if line.startswith('ask '):
            rest = line[4:].strip()
            parts = rest.split(' ', 1)
            varname = parts[0]
            prompt = parts[1] if len(parts) > 1 else ''
            answer = input(substitute(prompt, v) + ' ')
            v[varname] = answer
            return

        # wait 2
        if line.startswith('wait '):
            secs = to_value(line[5:].strip(), v)
            time.sleep(float(secs))
            return

        # run dir   (runs a real cmd/shell command)
        if line.startswith('run '):
            cmd = substitute(line[4:], v)
            subprocess.run(cmd, shell=True)
            return

        # add/sub/mul/div x 5
        for op, symbol in [('add', '+'), ('sub', '-'), ('mul', '*'), ('div', '/')]:
            if line.startswith(op + ' '):
                rest = line[len(op) + 1:].strip()
                varname, amount = rest.split(' ', 1)
                amount = to_value(amount.strip(), v)
                current = v.get(varname, 0)
                if symbol == '+':
                    v[varname] = current + amount
                elif symbol == '-':
                    v[varname] = current - amount
                elif symbol == '*':
                    v[varname] = current * amount
                elif symbol == '/':
                    v[varname] = current / amount
                return

        # --- GUI commands ---
        if line.startswith('gui '):
            text = substitute(line[4:], v)
            root = self.get_gui_root()
            label = tk.Label(root, text=text, font=('Segoe UI', 14))
            label.pack(padx=20, pady=20)
            return

        if line.startswith('button '):
            # button Click Me -> print You clicked!
            if '->' not in line:
                raise INRainError("button needs -> e.g. button Click Me -> print Hi!")
            label_text, action = line[7:].split('->', 1)
            label_text = substitute(label_text.strip(), v)
            action = action.strip()
            root = self.get_gui_root()

            def on_click(a=action):
                self.run_line(a)

            btn = tk.Button(root, text=label_text, command=on_click, font=('Segoe UI', 12))
            btn.pack(padx=10, pady=10)
            return

        if line.startswith('input_box'):
            # input_box name Whats your name?  (stores result in variable "name")
            rest = line[len('input_box'):].strip()
            if rest:
                parts = rest.split(' ', 1)
                varname = parts[0]
                prompt = parts[1] if len(parts) > 1 else 'Enter a value:'
            else:
                varname = 'answer'
                prompt = 'Enter a value:'
            root = self.get_gui_root()
            result = simpledialog.askstring("INRain", substitute(prompt, v), parent=root)
            v[varname] = result if result is not None else ''
            return

        if line.startswith('popup '):
            text = substitute(line[6:], v)
            root = self.get_gui_root()
            messagebox.showinfo("INRain", text)
            return

        if line == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return

        raise INRainError(f"Unknown command: {line}")

    def eval_expr(self, expr):
        v = self.variables
        expr = expr.strip()
        # simple math: a + b, a - b, a * b, a / b
        m = re.match(r'^(.+?)\s*([\+\-\*/])\s*(.+)$', expr)
        if m:
            left, op, right = m.groups()
            lv = to_value(left.strip(), v)
            rv = to_value(right.strip(), v)
            try:
                lv_f, rv_f = float(lv), float(rv)
                if op == '+':
                    result = lv_f + rv_f
                elif op == '-':
                    result = lv_f - rv_f
                elif op == '*':
                    result = lv_f * rv_f
                elif op == '/':
                    result = lv_f / rv_f
                # return int if whole number
                if result == int(result):
                    return int(result)
                return result
            except (ValueError, TypeError):
                if op == '+':
                    return str(lv) + str(rv)
        return substitute(str(to_value(expr, v)), v) if isinstance(to_value(expr, v), str) else to_value(expr, v)


def main():
    if len(sys.argv) < 2:
        print("INRain - usage: inrain <file.inr | file.inrain>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        sys.exit(1)
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.inr', '.inrain'):
        print(f"Warning: '{ext}' is not .inr or .inrain, running anyway...")
    interp = Interpreter()
    interp.run_file(path)


if __name__ == '__main__':
    main()
