#!/usr/bin/env python3
"""
Genera una guia HTML interactiva a partir de markdown,
con tema blueprint y simuladores inyectados.

Uso:
  python generate_http.py --input temp/guia_http.md --output guia_http.html
  python generate_http.py --theme blueprint
  python generate_http.py --help
"""
import argparse, json, re, html as h
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_MD = SCRIPT_DIR.parent / "temp" / "guia http.md"
DEFAULT_OUT = SCRIPT_DIR.parent / "guia_http.html"
BLUEPRINT = SCRIPT_DIR / "temas" / "blueprint.css"
SIM_URL = SCRIPT_DIR / "componentes" / "sim-url.html"
SIM_REQ = SCRIPT_DIR / "componentes" / "sim-request.html"
SIM_CODES = SCRIPT_DIR / "componentes" / "sim-codes.html"

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_code_blocks(md):
    """Extrae bloques ```lenguaje y devuelve {id: {title, lang, code}}"""
    blocks = {}
    idx = 0
    # Bloques con especificador de lenguaje
    pattern = re.compile(r'^```(\w+)?\s*\n(.*?)```', re.MULTILINE | re.DOTALL)
    for m in pattern.finditer(md):
        lang = m.group(1) or "text"
        code = m.group(2).rstrip("\n")
        key = f"code-{idx}"
        idx += 1
        blocks[key] = {"title": f"codigo-{key}", "lang": lang, "code": code}
    # Limpiar los bloques del markdown (se renderizan via CODE dict)
    return blocks

def md_to_html_inline(text):
    """Convierte inline markdown a HTML (bold, italic, code, links)."""
    # Code inline
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text

def parse_section(raw_lines, start, code_blocks):
    """Parse una seccion desde start hasta la siguiente seccion o fin."""
    content_lines = []
    i = start
    while i < len(raw_lines):
        line = raw_lines[i]
        # Nueva seccion?
        if re.match(r'^##? \d+\.', line):
            break
        content_lines.append(line)
        i += 1
    content = "\n".join(content_lines).strip()
    return i, convert_block(content, code_blocks)

def convert_block(text, code_blocks):
    """Convierte un bloque de markdown a HTML."""
    lines = text.split("\n")
    out = []
    i = 0
    pending_code = []
    in_code = False
    code_lang = None

    while i < len(lines):
        line = lines[i]

        # Bloque de codigo con lenguaje
        if line.strip().startswith("```") and not in_code:
            in_code = True
            code_lang = line.strip()[3:].strip() or "text"
            pending_code = []
            i += 1
            continue
        elif line.strip() == "```" and in_code:
            in_code = False
            # Registrar bloque
            key = f"code-{len(code_blocks)}"
            code_blocks[key] = {"title": "codigo", "lang": code_lang, "code": "\n".join(pending_code).rstrip()}
            out.append(f'<div class="code" data-code="{key}"></div>')
            i += 1
            continue
        elif in_code:
            pending_code.append(line)
            i += 1
            continue

        # Tabla
        if "|" in line and line.strip().startswith("|"):
            # Recolectar filas de tabla
            table_lines = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(build_table(table_lines))
            continue

        # Listas
        if re.match(r'^(\d+\.|[-*])\s', line):
            items, i = collect_list(lines, i)
            out.append(items)
            continue

        # Headers
        if line.startswith("#### "):
            out.append(f'<h4>{md_to_html_inline(line[5:])}</h4>')
            i += 1
        elif line.startswith("### "):
            out.append(f'<h3>{md_to_html_inline(line[4:])}</h3>')
            i += 1
        elif line.startswith("## "):
            out.append(f'<h2>{md_to_html_inline(line[3:])}</h2>')
            i += 1
        elif line.startswith("# "):
            out.append(f'<h1>{md_to_html_inline(line[2:])}</h1>')
            i += 1

        # Blockquotes (Tips, Avisos, etc.)
        elif line.startswith(">"):
            bq_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                bq_lines.append(lines[i][1:].strip())
                i += 1
            content_bq = " ".join(bq_lines)
            # Detectar tipo
            if "**Tip**" in content_bq or "Tip" in content_bq and ":" in content_bq:
                m = re.search(r'\*\*Tip\*\*[:\s]*(.*)', content_bq)
                inner = m.group(1) if m else content_bq
                out.append(f'<div class="tip"><p>{md_to_html_inline(inner)}</p></div>')
            elif "**Aviso**" in content_bq:
                m = re.search(r'\*\*Aviso\*\*[:\s]*(.*)', content_bq)
                inner = m.group(1) if m else content_bq
                out.append(f'<div class="note"><p>{md_to_html_inline(inner)}</p></div>')
            elif "**Recurso**" in content_bq:
                m = re.search(r'\*\*Recurso\*\*[:\s]*(.*)', content_bq)
                inner = m.group(1) if m else content_bq
                out.append(f'<div class="tip"><p>{md_to_html_inline(inner)}</p></div>')
            elif "**PIENSA" in content_bq:
                m = re.search(r'\*\*PIENSA[^*]*\*\*[:\s]*(.*)', content_bq)
                inner = m.group(1) if m else content_bq
                out.append(f'<div class="piensa"><div class="ptitle">PIENSA UN MOMENTO</div><p>{md_to_html_inline(inner)}</p></div>')
            else:
                out.append(f'<blockquote>{md_to_html_inline(content_bq)}</blockquote>')
            continue

        # Linea vacia
        elif line.strip() == "":
            i += 1
            continue

        # Preformatted / ascii art (lineas que empiezan con espacios o son puramente texto)
        elif line.startswith("   ") or (line.startswith("│") or line.startswith("  ") or re.match(r'^\s+[└├┌┐│─]', line)):
            # Bloque preformatted
            pre_lines = []
            while i < len(lines) and (lines[i].startswith("   ") or lines[i].startswith("│") or lines[i].startswith("  ") or re.match(r'^\s+[└├┌┐│─]', lines[i]) or lines[i].strip() == ""):
                pre_lines.append(lines[i].rstrip())
                i += 1
            text = "\n".join(pre_lines).rstrip()
            if text:
                out.append(f'<pre style="white-space:pre">{h.escape(text)}</pre>')
            continue

        # Reto
        elif "### Reto" in line or "### Retos" in line or "🧩 Reto" in line:
            out.append(f'<h3>{md_to_html_inline(line)}</h3>')
            i += 1

        # Prueba
        elif "### Prueba" in line or "🔬 Prueba" in line:
            out.append(f'<h3>{md_to_html_inline(line)}</h3>')
            i += 1

        # Objetivo
        elif "**Objetivo**" in line or "🎯 Objetivo" in line:
            m = re.search(r'\*\*Objetivo\*\*[:\s]*(.*)', line)
            inner = m.group(1) if m else line
            out.append(f'<div class="tip"><p>{md_to_html_inline(inner)}</p></div>')
            i += 1

        # Parrafos normales
        else:
            if line.strip():
                out.append(f'<p>{md_to_html_inline(line)}</p>')
            i += 1

    return "\n".join(out)

def build_table(table_lines):
    """Construye una tabla HTML desde lineas markdown con |."""
    rows = []
    for l in table_lines:
        # Skip separator row (|---|---|)
        if re.match(r'^\|[\s\-:|]+\|$', l):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return ""

    header = rows[0] if rows else []
    body = rows[1:] if len(rows) > 1 else []

    th = "".join(f"<th>{md_to_html_inline(c)}</th>" for c in header)
    tbody = ""
    for row in body:
        td = "".join(f"<td>{md_to_html_inline(c)}</td>" for c in row)
        tbody += f"<tr>{td}</tr>"

    return f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table></div>'

def collect_list(lines, i):
    """Recolecta elementos de lista y devuelve HTML + siguiente indice."""
    items = []
    while i < len(lines) and re.match(r'^(\d+\.|[-*])\s', lines[i]):
        m = re.match(r'^(\d+\.|[-*])\s(.*)', lines[i])
        items.append(f"<li>{md_to_html_inline(m.group(2))}</li>")
        i += 1
    tag = "ol" if items and re.match(r'^\d+\.', lines[i-1] if i > 0 else "") else "ul"
    return f"<{tag}>{''.join(items)}</{tag}>", i

def split_sections(md):
    """Divide el markdown en secciones por ## [num]. titulo."""
    # Quitar frontmatter (--- ... ---)
    md = re.sub(r'^---\n[\s\S]*?---\n', '', md)
    # Quitar todo antes del primer ## (indice, etc.)
    first_sec = re.search(r'^## \d+\.', md, re.MULTILINE)
    if first_sec:
        md = md[first_sec.start():]

    sections = []
    # Patron: ## [num] titulo\n o ### [num] titulo\n
    pattern = re.compile(r'^(#{2,3}) ([\d]+)\. (.+)$', re.MULTILINE)
    prev_end = 0
    for m in pattern.finditer(md):
        if prev_end > 0:
            content = md[prev_end:m.start()].strip()
            if content:
                sections.append(content)
        prev_end = m.end()
    # Ultima seccion
    if prev_end < len(md):
        sections.append(md[prev_end:].strip())
    return sections

def build_sections(md):
    """Construye el HTML de todas las secciones."""
    code_blocks = {}
    sections = split_sections(md)
    html_sections = []

    # Parsear cada seccion
    for sec_content in sections:
        html = convert_block(sec_content, code_blocks)
        html_sections.append(html)

    return html_sections, code_blocks

def build_nav_items(sections_html):
    """Construye los enlaces de navegacion desde el markdown."""
    nav = []
    i = 0
    for html in sections_html:
        i += 1
        # Extraer titulo h2 o h3
        m = re.search(r'<h[23]>([^<]+)</h[23]>', html)
        if m:
            title = re.sub(r'[\d]+\.\s*', '', m.group(1)).strip()
            nav.append(f'  <a class="nav-link" href="#sec-{i}">{h.escape(title)}</a>')
    return "\n".join(nav)

def build_checklist(md):
    """Extrae los items de checklist del final."""
    checklist = []
    for line in md.split("\n"):
        m = re.match(r'^\s*-\s*\[\s*\]\s*(.+)', line)
        if m:
            checklist.append(m.group(1).strip())
    return checklist

def build_ampliaciones(md):
    """Extrae recursos de ampliaciones del markdown buscando lines con [texto](url)."""
    amps = []
    for line in md.split("\n"):
        m = re.search(r'\[([^\]]+)\]\((https?://[^\)]+)\)', line)
        if m:
            texto = m.group(1).strip()
            url = m.group(2).strip()
            if texto and url:
                amps.append({"t": texto, "d": url})
    return amps

def inject_simulator(html_content, sim_html, marker_after):
    """Inyecta HTML de simulador despues del marker."""
    if marker_after in html_content:
        return html_content.replace(marker_after, marker_after + "\n" + sim_html)
    return html_content + "\n" + sim_html

def main():
    parser = argparse.ArgumentParser(
        description="Genera una guía HTML interactiva a partir de markdown "
                    "con tema blueprint y simuladores inyectados."
    )
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_MD,
                        help="Archivo markdown de entrada")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUT,
                        help="Archivo HTML de salida")
    parser.add_argument("--theme", "-t", type=Path, default=BLUEPRINT,
                        help="Ruta al archivo CSS del tema")
    args = parser.parse_args()

    md = read(args.input)
    tema_css = read(args.theme)
    sim_url = read(SIM_URL)
    sim_req = read(SIM_REQ)
    sim_codes = read(SIM_CODES)
    sim_url = read(SIM_URL)
    sim_req = read(SIM_REQ)
    sim_codes = read(SIM_CODES)

    # Extraer solo el CSS+HTML+JS de cada simulador
    def extract_body(html):
        # Quitar comentarios版权
        html = re.sub(r'<!--[\s\S]*?-->', '', html)
        return html.strip()

    sim_url_body = extract_body(sim_url)
    sim_req_body = extract_body(sim_req)
    sim_codes_body = extract_body(sim_codes)

    # Construir secciones
    sections_html, code_blocks = build_sections(md)

    # Checklist
    checklist = build_checklist(md)
    if not checklist:
        # Generar desde seccion 22
        checklist = [
            "Se descomponer una URL en sus 6 partes",
            "Entender el ciclo DNS - TCP - TLS - HTTP",
            "Distinguir GET/POST/PUT/PATCH/DELETE",
            "Saber cuando usar query string y cuando body",
            "Elegir el Content-Type correcto",
            "Interpretar cualquier codigo de estado",
            "Leer y escribir cabeceras comunes",
            "Entender como funcionan cookies y sesiones",
            "Saber que es la cache HTTP",
            "Entender CORS y diagnosticar el error clasico",
            "Conocer las diferencias HTTP/1.1 /2 y /3",
            "Reconocer amenazas tipicas (XSS, CSRF, MITM)",
            "Diagnosticar errores comunes por sintoma",
        ]

    # Generar secciones HTML finales
    sections_out = []
    for idx, sec_html in enumerate(sections_html, 1):
        sections_out.append(f'<section id="sec-{idx}">\n{sec_html}\n</section>')

    # Inyectar simuladores en secciones 2, 4, 9
    if len(sections_out) >= 2:
        sections_out[1] = sections_out[1] + "\n" + sim_url_body
    if len(sections_out) >= 4:
        sections_out[3] = sections_out[3] + "\n" + sim_req_body
    if len(sections_out) >= 9:
        sections_out[8] = sections_out[8] + "\n" + sim_codes_body

    content_html = "\n".join(sections_out)

    # CODE array para JS — con escape para ${} y backticks
    def safe_code(code):
        # Neutraliza ${} para que no se interprete como template literal
        code = code.replace("\\", "\\\\").replace("`", "\\`")
        code = code.replace("${", "${''+")
        return code

    code_js = "var CODE = " + "{\n"
    for k, v in code_blocks.items():
        title_esc = v["title"].replace("\\", "\\\\").replace('"', '\\"')
        lang_esc = v["lang"]
        code_esc = safe_code(v["code"])
        code_js += f'  "{k}": {{title: "{title_esc}", lang: "{lang_esc}", code: `{code_esc}`}},\n'
    code_js += "};\n"

    # Checklist JS
    checklist_js = "var CHECKLIST = " + str(checklist).replace("'", '"') + ";"

    # Ampliaciones — extraídas del markdown si existen
    amps = build_ampliaciones(md)
    ampliaciones_js = "var AMPLIACIONES = " + json.dumps(amps, ensure_ascii=False) + ";" if amps else "var AMPLIACIONES = [];"

    # Nav items — extraídos de las secciones con HTML escapado
    nav_links = []
    for idx in range(len(sections_html)):
        m = re.search(r'<h[23]>([^<]+)</h[23]>', sections_html[idx])
        if m:
            title = re.sub(r'^[\d]+\.\s*', '', m.group(1)).strip()
            nav_links.append(f'  <a class="nav-link" href="#sec-{idx+1}">{h.escape(title)}</a>')
    nav_html = "\n".join(nav_links)

    # Template base
    tmpl = read(str(SCRIPT_DIR / "plantilla_base.html"))

    # Placeholders
    replacements = {
        "{{TITLE}}": "Guia HTTP",
        "{{DESCRIPTION}}": "Protocolo HTTP interactivo con simuladores",
        "{{CSS_THEME}}": tema_css,
        "{{SIG}}": "HTTP",
        "{{TITLE_SHORT}}": "Protocolo HTTP",
        "{{TOTAL}}": str(len(checklist) + 10),
        "{{NAV_ITEMS}}": nav_html,
        "{{INTRO_ANCHOR}}": "Introduccion",
        "{{EYEBROW}}": "DAM · DAW · ASIR · Nivel avanzado",
        "{{H1}}": "Guia del Protocolo HTTP",
        "{{INTRO}}": "Todo lo que necesitas saber sobre HTTP: metodos, codigos de estado, cabeceras, seguridad y mas. Con laboratorios y simuladores interactivos.",
        "{{CONTENT}}": content_html,
        "{{SEC_NUM_CHECKLIST}}": str(len(sections_html) + 1),
        "{{SEC_NUM_AMPLIACIONES}}": str(len(sections_html) + 2),
        "{{CODE_ARRAY}}": code_js,
        "{{CHECKLIST}}": checklist_js,
        "{{AMPLIACIONES}}": ampliaciones_js,
        "{{CUSTOM_JS}}": "",
    }

    html = tmpl
    for k, v in replacements.items():
        html = html.replace(k, v)

    write(args.output, html)
    print(f"[OK] Generado: {args.output}")
    print(f"     Secciones: {len(sections_html)}")
    print(f"     Bloques de codigo: {len(code_blocks)}")
    print(f"     Checklist: {len(checklist)}")

if __name__ == "__main__":
    main()
