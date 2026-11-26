import pathlib
p = pathlib.Path('app.py')
t = p.read_text()
t = t.replace('class="vc-btn" style="cursor:pointer"', "class='vc-btn' style='cursor:pointer'")
p.write_text(t)
print('FIXED QUOTES')
