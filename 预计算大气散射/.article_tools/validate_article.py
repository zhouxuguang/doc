"""Audit local links, equation numbering, diagram layout and immutable inputs."""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT/'.article_tools/qa'
IMAGES = ROOT/'atmosphere_scattering_images'
article = ROOT/'预计算大气散射技术详解.md'
source = article.read_text()

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ('href', 'src'):
            if attrs.get(name):
                self.targets.append(attrs[name])
        if tag == 'img':
            self.images.append(attrs.get('src'))

def missing_links(html_path, base):
    parser = Links()
    parser.feed(html_path.read_text())
    missing = []
    for target in parser.targets:
        url = urlsplit(target)
        if url.scheme or not url.path:
            continue
        if not (base/unquote(url.path)).exists():
            missing.append(target)
    return sorted(set(missing)), parser.images

missing, referenced_images = missing_links(QA/'article_body.html', ROOT)
preview_missing, _ = missing_links(QA/'article_preview.html', QA)
assert not missing and not preview_missing, (missing, preview_missing)

tags = list(map(int, re.findall(r'\\tag\{(\d+)\}', source)))
assert tags == list(range(1, 85))
latex = json.loads((QA/'latex_validation.json').read_text())
assert not latex['errors']
expressions = json.loads((QA/'math_expressions.json').read_text())
assert sum(bool(item['display']) for item in expressions) == 84
assert latex['count'] == len(expressions)
assert not any(ord(c) < 32 and c not in '\n\t' for c in source)
paragraphs = source.split('\n\n')
duplicates = sorted({p[:90] for p in paragraphs if len(p) > 70 and paragraphs.count(p) > 1})
assert not duplicates, duplicates

audit_files = ['figure_layout_audit.json', 'reference_figure_layout_audit.json',
               'paper_reading_figure_layout_audit.json', 'explanatory_figure_layout_audit.json']
audits = []
for name in audit_files:
    audits.extend(json.loads((QA/name).read_text()))
assert len(audits) == 26
overlaps = sum(len(a['overlaps']) for a in audits)
outside = sum(len(a['outside_canvas']) for a in audits)
assert overlaps == 0 and outside == 0
assert len(list(IMAGES.glob('*.svg'))) == len(audits)
assert len(referenced_images) == 36 and len(set(referenced_images)) == 35
for item in audits:
    assert (IMAGES/(item['figure']+'.svg')).exists()
    assert (IMAGES/(item['figure']+'.png')).exists()

manifest = json.loads((IMAGES/'capture_manifest.json').read_text())
sha256 = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
captures = {item['file']: sha256(IMAGES/item['file']) == item['image_sha256']
            for item in manifest['captures']}
engine = Path(manifest['engine_root'])
sources = {name: sha256(engine/name) == digest for name, digest in manifest['source_hashes'].items()}
assert all(captures.values()) and all(sources.values())
examples = json.loads((QA/'main_text_examples_validation.json').read_text())

report = json.loads((QA/'validation_report.json').read_text())
report.update({
    'han_characters': len(re.findall(r'[\u4e00-\u9fff]', source)),
    'numbered_equations': len(tags), 'latex_expressions': latex['count'], 'latex_errors': [],
    'svg_diagrams': len(audits), 'png_images': len(list(IMAGES.glob('*.png'))),
    'image_references': len(referenced_images), 'unique_referenced_images': len(set(referenced_images)),
    'missing_local_links': missing, 'missing_preview_links': preview_missing,
    'duplicate_long_paragraphs': duplicates,
    'figure_text_overlaps': overlaps, 'figure_text_outside_canvas': outside,
    'capture_hashes_unchanged': captures, 'source_hashes_unchanged': sources,
    'explanatory_diagrams': 4,
    'explanatory_figures': [a['figure']+'.png' for a in audits if a['figure'].startswith('explain_')],
    'main_text_example_groups': len(examples),
    'main_text_examples_validation': '.article_tools/qa/main_text_examples_validation.json',
    'explanatory_figure_validation': '.article_tools/qa/explanatory_figure_validation.json',
    'visual_review': 'All original and previously redrawn diagrams were inspected in earlier revisions. '
                     'Individually inspected final G-J PNGs for legibility, geometry, line/text interaction '
                     'and caption consistency. KaTeX renders every article expression to HTML/MathML; '
                     'MathJax renders all 84 numbered equations to SVG. '
                     'Equation 75 now explicitly names the shader inverse matrix to avoid mixing CPU '
                     'matrix composition with shader vector conventions.',
})
(QA/'validation_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({key: report[key] for key in [
    'han_characters', 'numbered_equations', 'latex_expressions', 'svg_diagrams', 'png_images',
    'figure_text_overlaps', 'figure_text_outside_canvas', 'main_text_example_groups',
    'missing_local_links', 'missing_preview_links', 'capture_hashes_unchanged',
]}, ensure_ascii=False))
