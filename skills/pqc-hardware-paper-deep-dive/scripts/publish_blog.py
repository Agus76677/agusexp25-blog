#!/usr/bin/env python3
"""Export validated paper HTML/PDF to Hana/Astro; optionally build, commit and push."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Element:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element()
        self.stack = [self.root]
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID: self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.stack.pop()
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
    def handle_data(self, data): self.stack[-1].children.append(data)

def descendants(node):
    if isinstance(node, Element):
        yield node
        for child in node.children: yield from descendants(child)

def plain(node):
    return node if isinstance(node, str) else ''.join(plain(c) for c in node.children)

def digest(data): return hashlib.sha256(data).hexdigest()
def content_digest(path, data):
    # Git may check generated text out as CRLF on Windows.
    if Path(path).suffix in ('.mdx', '.json', '.astro'):
        data = data.replace(b'\r\n', b'\n')
    return digest(data)
def run(args, cwd): subprocess.run([str(a) for a in args], cwd=str(cwd), check=True)
def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], encoding='utf-8').strip()

COMPONENT = '''---
interface Props { html: string }
const { html } = Astro.props
---
<div class="pqc-paper" set:html={html} />
<style>
  .pqc-paper { min-width: 0; overflow-wrap: anywhere; }
  .pqc-paper :global(figure) { margin: 1.4em 0; }
  .pqc-paper :global(img) { max-width: 100%; height: auto; margin-inline: auto; background: white; }
  .pqc-paper :global(figcaption) { text-align: center; font-size: .85em; opacity: .8; }
  .pqc-paper :global(.table-scroll) { overflow-x: auto; }
  .pqc-paper :global(table) { width: 100%; border-collapse: collapse; font-size: .9em; }
  .pqc-paper :global(th), .pqc-paper :global(td) { padding: .5em; border: 1px solid #8885; }
  .pqc-paper :global(.fact) { font-weight: 600; font-size: .85em; }
  .pqc-paper :global(.analysis) { color: #c76c30; }
  .pqc-paper :global(.citation) { font-size: .85em; }
  .pqc-paper :global(math[display="block"]) { overflow-x: auto; padding: .8em 0; }
  .pqc-paper :global(.algorithm) { border-block: 2px solid #8888; margin: 1em 0; }
  .pqc-paper :global(.algorithm-caption), .pqc-paper :global(.algorithm-io) { padding: .6em; border-bottom: 1px solid #8885; }
  .pqc-paper :global(.algorithm-lines) { list-style: none; padding: .5em; counter-reset: step; }
  .pqc-paper :global(.algorithm-step) { display: flex; gap: .7em; counter-increment: step; }
  .pqc-paper :global(.algorithm-line-number::before) { content: counter(step); opacity: .6; }
  .pqc-paper :global(.algorithm-line-content) { padding-left: calc(var(--algorithm-indent, 0) * 1.1em); }
</style>
'''

def export(args):
    paper, blog = args.paper_dir.resolve(), args.blog_root.resolve()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        raise ValueError('slug must be lowercase words separated by hyphens')
    if not (blog / 'src/content/blog').is_dir(): raise ValueError('Expected a Hana/Astro blog')
    run([sys.executable, Path(__file__).with_name('validate_output.py'), '--paper-dir', paper], paper)
    document = Document((paper / 'article.html').read_text(encoding='utf-8'))
    main = next((n for n in descendants(document.root) if n.tag == 'main'), None)
    if main is None: raise ValueError('article.html has no main element')
    meta = {n.attrs.get('name'): n.attrs.get('content', '') for n in descendants(document.root) if n.tag == 'meta'}
    title = args.title or plain(next(n for n in descendants(document.root) if n.tag == 'title'))
    if len(title) > 60 or len(args.description) > 160: raise ValueError('Title limit 60; description limit 160')
    post = Path('src/content/blog') / ('paper-deep-dive-' + args.slug)
    assets = Path('public/papers') / args.slug
    manifest_path = blog / post / 'export-manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if (blog / post).exists() and not previous: raise ValueError('Post exists and was not generated by this exporter')
    for relative, old_hash in previous.get('files', {}).items():
        path = blog / relative
        path.resolve().relative_to(blog)
        if path.exists() and content_digest(relative, path.read_bytes()) != old_hash:
            raise ValueError('Generated file has local edits; merge into article.html first: ' + relative)
    files = {}
    base = '/' + args.base.strip('/') if args.base.strip('/') else ''
    prefix = base + '/papers/' + args.slug + '/'
    def resource(value):
        parsed = urlsplit(value)
        if parsed.scheme in ('http', 'https', 'mailto') or value.startswith(('#', '//')): return value
        if parsed.scheme or value.startswith(('/', '\\')): raise ValueError('Expected relative asset or web URL: ' + value)
        target = (paper / unquote(parsed.path)).resolve()
        asset = target.relative_to(paper)
        if asset.as_posix() != 'article.pdf' and asset.parts[0] != 'figures':
            raise ValueError('Publishable assets: figures/* and article.pdf; found ' + value)
        files[(assets / asset).as_posix()] = target.read_bytes()
        return prefix + quote(asset.as_posix()) + (('?' + parsed.query) if parsed.query else '') + (('#' + parsed.fragment) if parsed.fragment else '')
    def serialize(node):
        if isinstance(node, str): return escape(node)
        if node.tag in ('script', 'iframe', 'object', 'embed', 'form', 'style'): raise ValueError('Unsupported active HTML: ' + node.tag)
        attrs = dict(node.attrs)
        if node.tag == 'img':
            attrs['class'] = ((attrs.get('class') or '') + ' zoomable').strip()
            attrs.setdefault('loading', 'lazy')
        for key, value in attrs.items():
            if key.lower().startswith('on') or key == 'srcdoc': raise ValueError('Unsupported script attribute: ' + key)
            if key in ('src', 'href', 'poster') and value: attrs[key] = resource(value)
            if key == 'srcset': raise ValueError('Use a single src for paper figures')
        attr = ''.join(' ' + k + (('="' + escape(v, quote=True) + '"') if v is not None else '') for k, v in attrs.items())
        result = '<' + node.tag + attr + '>'
        if node.tag not in VOID: result += ''.join(serialize(c) for c in node.children) + '</' + node.tag + '>'
        return '<div class="table-scroll">' + result + '</div>' if node.tag == 'table' else result
    blocks, body = [], []
    def add_block(html):
        if html.strip():
            blocks.append(html)
            body.append('<PaperBlock html={blocks[' + str(len(blocks)-1) + ']} />')
    headings = ('h2', 'h3', 'h4', 'h5', 'h6')
    def emit(node):
        if isinstance(node, Element) and node.tag in headings:
            if node.attrs.get('id'): add_block('<span id="' + escape(node.attrs['id'], quote=True) + '"></span>')
            heading = re.sub(r'([\\`*_{}\[\]<>#!|])', r'\\\1', plain(node).strip())
            body.append('#' * int(node.tag[1]) + ' ' + heading)
        elif isinstance(node, Element) and any(n.tag in headings for n in descendants(node)):
            if node.attrs.get('id'): add_block('<span id="' + escape(node.attrs['id'], quote=True) + '"></span>')
            for child in node.children: emit(child)
        else: add_block(serialize(node))
    for child in main.children: emit(child)
    pdf_url = resource('article.pdf')
    published = previous.get('publishDate', args.date or date.today().isoformat())
    from paper_common import read_json_yaml
    paper_identity = read_json_yaml(paper / 'sources.yaml')['paper']
    front = {'title': title, 'description': args.description, 'publishDate': published, 'paperBody': 'content.json',
             'tags': ['paper deep dive', 'pqc', *args.tag], 'category': 'research', 'language': 'zh', 'draft': args.draft,
             'paper': {'title': meta['paper-title'], 'authors': paper_identity['authors'], 'year': int(meta['paper-year'])}}
    if paper_identity.get('venue'): front['paper']['venue'] = paper_identity['venue']
    if previous: front['updatedDate'] = args.date or date.today().isoformat()
    if meta.get('code-url'): front['paper']['code'] = meta['code-url']
    mdx = '---\n' + '\n'.join(k + ': ' + json.dumps(v, ensure_ascii=False) for k, v in front.items()) + '\n---\n\n'
    mdx += "import PaperBlock from './PaperBlock.astro'\nimport blocks from './content.json'\n\n"
    mdx += '[原论文](' + meta['paper-url'] + ') · [下载解读 PDF](' + pdf_url + ')\n\n' + '\n\n'.join(body) + '\n'
    files[(post / 'index.mdx').as_posix()] = mdx.encode('utf-8')
    files[(post / 'content.json').as_posix()] = (json.dumps(blocks, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    files[(post / 'PaperBlock.astro').as_posix()] = COMPONENT.encode('utf-8')
    for relative, data in files.items():
        destination = blog / relative
        if destination.exists() and relative not in previous.get('files', {}) and destination.read_bytes() != data:
            raise ValueError('Destination contains a different asset: ' + relative)
    manifest = {'generator': 'pqc-hardware-paper-deep-dive', 'publishDate': published,
                'source_html_sha256': digest((paper / 'article.html').read_bytes()),
                'files': {p: content_digest(p, d) for p, d in files.items()}}
    files[(post / 'export-manifest.json').as_posix()] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    for relative, data in files.items():
        destination = blog / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print('Exported: ' + str(blog / post / 'index.mdx'))
    return list(files)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper-dir', type=Path, required=True)
    parser.add_argument('--blog-root', type=Path, required=True)
    parser.add_argument('--slug', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--title')
    parser.add_argument('--tag', action='append', default=[])
    parser.add_argument('--date', help='ISO date; existing publication date is preserved')
    parser.add_argument('--base', default='', help='Astro base path, if configured')
    parser.add_argument('--draft', action='store_true')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--publish', action='store_true', help='Build, commit exported files and push')
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--branch', default='main')
    args = parser.parse_args()
    blog = args.blog_root.resolve()
    try:
        if args.date: date.fromisoformat(args.date)
        if args.publish:
            if git(blog, 'branch', '--show-current') != args.branch: raise ValueError('Checkout the requested branch before publishing')
            if git(blog, 'diff', '--cached', '--name-only'): raise ValueError('Commit or unstage existing staged changes before publishing')
        files = export(args)
        if args.build or args.publish:
            node = shutil.which('node')
            if not node: raise ValueError('Node.js is required')
            if (blog / 'scripts/deploy.mjs').is_file(): run([node, 'scripts/deploy.mjs', '--dry-run'], blog)
            else:
                import os
                env = dict(os.environ, DEPLOYMENT_PLATFORM='github')
                for task in ('check', 'build'):
                    subprocess.run([node, 'node_modules/astro/astro.js', task], cwd=str(blog), env=env, check=True)
        if args.publish:
            run(['git', 'add', '--', *files], blog)
            if git(blog, 'diff', '--cached', '--name-only'): run(['git', 'commit', '-m', 'docs: publish paper deep dive ' + args.slug], blog)
            run(['git', 'push', args.remote, 'HEAD:refs/heads/' + args.branch], blog)
            print('Pushed ' + git(blog, 'rev-parse', 'HEAD'))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__': raise SystemExit(main())
