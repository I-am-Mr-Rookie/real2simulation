import sys,pathlib
from Build.reports import render_html
from Build.reports.typeset import TEMPLATE_TEXT
from tests.reports.fixture import synthetic_fitter_result, synthetic_report
F=synthetic_fitter_result(); d=pathlib.Path(sys.argv[1]); d.mkdir(parents=True,exist_ok=True)
for t in TEMPLATE_TEXT: (d/(t+'.html')).write_text(render_html(synthetic_report(F,t),F),encoding='utf-8')
print(sorted(p.name for p in d.iterdir()))
