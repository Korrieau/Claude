#!/usr/bin/env python3
"""Bundle three.js and the game into one self-contained index.html.

An inline <script type="module"> works from file://, but an *imported* one
does not, so the library is inlined rather than fetched. Three's single
trailing `export { ... }` clause is rewritten into a plain object so the game
can keep using the familiar THREE.* names.
"""
import re, pathlib

here = pathlib.Path(__file__).parent
three = (here / 'three.module.js').read_text()

m = re.search(r"\nexport \{([^}]*)\};\s*$", three)
if not m:
    raise SystemExit('could not find three.js export clause')
names = []
for part in m.group(1).split(','):
    part = part.strip()
    if not part:
        continue
    if ' as ' in part:
        orig, alias = [p.strip() for p in part.split(' as ')]
        names.append(f'{alias}: {orig}')
    else:
        names.append(part)
three = three[:m.start()] + '\nconst THREE = {\n  ' + ',\n  '.join(names) + '\n};\n'

game = (here / 'src' / 'game.js').read_text()
shell = (here / 'src' / 'shell.html').read_text()
bundle = ('// three.js r160 - MIT - https://github.com/mrdoob/three.js\n'
          '// Inlined by build.py so the page runs straight off the filesystem.\n'
          + three + '\n\n'
          # Block-scoped so game identifiers cannot collide with three.js internals
          # that share the module scope (clamp, for one).
          + '{\n' + game + '\n}\n')
(here / 'index.html').write_text(shell.replace('__GAME__', bundle))
print('index.html:', (here / 'index.html').stat().st_size, 'bytes')
