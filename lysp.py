import functools, itertools, math, operator, pathlib, sys

Number = int | float
Sym = str

def function(params, body, env):
  return lambda *args: functools.reduce(
    lambda v, e: lysp_eval(e, env | dict(zip(params, args))), body, None
  )

def standard_env():
  return vars(math) | {
    '+':          operator.add,
    '-':          operator.sub,
    '*':          operator.mul,
    '/':          operator.truediv,
    '<':          operator.lt,
    '>':          operator.gt,
    '<=':         operator.le,
    '>=':         operator.ge,
    '==':         operator.ge,
    'is':         operator.is_,
    'abs':        lambda *x: abs(*x),
    'append':     lambda *x: list(itertools.chain(*x)),
    'apply':      lambda f, x: f(*x),
    'begin':      lambda *x: x[-1],
    'car':        lambda x: x[0],
    'cdr':        lambda x: x[1:], 
    'cons':       lambda x, y: [x] + y,
    'len':        len,
    'list':       lambda *x: list(x), 
    'list?':      lambda x: isinstance(x, list), 
    'map':        lambda *args: list(map(*args)),
    'max':        max,
    'min':        min,
    'not':        operator._not,
    'null?':      lambda x: x == [], 
    'number?':    lambda x: isinstance(x, Number),   
    'procedure?': lambda x: callable(x),
    'round':      round,
    'symbol?':    lambda x: isinstance(x, Sym),
    'print':      lambda x: print(lysp_repr(x)),
  }

def tokenize(program):
  return program.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(tokens):
  if len(tokens) == 0: raise SyntaxError('unexpected EOF while reading')
  match token := tokens.pop(0):
    case '(': return parse_list(tokens)
    case ')': raise SyntaxError('unexpected )')
    case _: return parse_atom(token)

def parse_list(tokens):
  list = []
  while tokens[0] != ')':
    list.append(parse(tokens))
  tokens.pop(0)
  return list

def parse_atom(token):
  try: return int(token)
  except ValueError: pass
  try: return float(token)
  except ValueError: pass
  return Sym(token)

def lysp_repr(e):
  return f"({' '.join(map(lysp_repr, e))})" if isinstance(e, list) else str(e)

def lysp_eval(e, env):
  match e:
    case int(x) | float(x):
      return x
    case Sym(v):
      return env[v]
    case 'quote', e:
      return e
    case 'if', c, t, f:
      return lysp_eval(t if lysp_eval(c, env) else f, env)
    case 'def', Sym(v), e:
      env[v] = lysp_eval(e, env)
    case 'defn', [f, *args], *body if len(body):
      env[f] = function(args, body, env)
    case 'fn', [*args], *body if len(body):
      return function(args, body, env)
    case fn, *args if fn not in ('quote', 'if', 'def', 'fn'):
      return lysp_eval(fn, env)(*(lysp_eval(a, env) for a in args))
    case _:
      raise SyntaxError(f"Error: could not evaluate `{lysp_repr(e)}`")

def run(program):
  global_env = standard_env()
  tokens = tokenize(program)
  result = None
  while tokens:
    result = lysp_eval(parse(tokens), global_env)
  return result

def repl():
  global_env = standard_env()
  while True:
    try:
      val = lysp_eval(parse(tokenize(input('lysp> '))), global_env)
      if val != None:
        print(lysp_repr(val))
    except (KeyboardInterrupt, EOFError):
      print('\nexiting...')
      return
    except Exception as e:
      print(f'Error: {e}')

def main():
  if len(sys.argv) > 1:
    run(pathlib.Path(sys.argv[1]).read_text())
  else:
    repl()

if __name__ == '__main__':
  main()
