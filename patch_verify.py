import pathlib
p = pathlib.Path('run.py')
t = p.read_text()
# remove old broken badge tries
lines = [l for l in t.splitlines() if 'm-badge-js' not in l and 'M</span>' not in l]
t = '\n'.join(lines)
badge = "realyungalhaji <span style=\"display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#1D9BF0;color:#fff;border-radius:50%;font-size:11px;font-weight:900;vertical-align:middle;margin-left:3px\">M</span>"
# inject in after_request before set_data
old = "r.set_data(h)"
new = f"h = h.replace('realyungalhaji', '{badge}')\n   r.set_data(h)"
if old in t and 'realyungalhaji <span' not in t:
    t = t.replace(old, new)
    p.write_text(t)
    print('PATCHED')
else:
    print('ALREADY PATCHED OR NOT FOUND')
    p.write_text(t)
