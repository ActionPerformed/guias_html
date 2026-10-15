#!/usr/bin/env python3
"""
Generador de guías interactivas — MiniMax
Uso:
  python generate.py --title "Titulo" --sig "DAM" --yaml contenido.yaml --theme paper_cream --output guia.html
  python generate.py --title "Titulo" --sig "DAW" --interactive
"""

import argparse
import html as h
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
TEMPLATE_FILE = SCRIPT_DIR / "plantilla_base.html"
TEMAS_DIR = SCRIPT_DIR / "temas"
COMPONENTES_DIR = SCRIPT_DIR / "componentes"


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def slug(text):
    """Convierte texto a id para anclas."""
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    import re as _re
    text = _re.sub(r"[^a-z0-9\s-]", "", text)
    text = _re.sub(r"[\s_]+", "-", text).strip("-")
    return text


# ---------------------------------------------------------------------------
# Simulators — carga y extracción de CSS/JS/HTML desde componentes/
# ---------------------------------------------------------------------------
_SIMULATORS = {}  # name -> {css, js, html}


def _extract_component(content):
    """Extrae CSS, JS y HTML de un archivo de componente."""
    css = ""
    js = ""
    body = content
    # Extraer <style>...</style>
    m = re.search(r'<style>([\s\S]*?)</style>', content)
    if m:
        css = m.group(1).strip()
        body = body[:m.start()] + body[m.end():]
    # Extraer <script>...</script> (solo el primero, el del componente)
    m = re.search(r'<script>\s*\(function\(\)\s*\{([\s\S]*?)\}\)\(\)\s*;\s*</script>', body)
    if m:
        js = m.group(1).strip()
    # Quitar comentarios HTML
    body = re.sub(r'<!--[\s\S]*?-->', '', body)
    body = body.strip()
    return css, js, body


def load_simulators():
    """Carga todos los componentes de simulador desde COMPONENTES_DIR."""
    global _SIMULATORS
    _SIMULATORS = {}
    if not COMPONENTES_DIR.exists():
        return
    for f in COMPONENTES_DIR.glob("sim-*.html"):
        name = f.stem  # "sim-url", "sim-request", ...
        try:
            content = load_file(f)
            css, js, body = _extract_component(content)
            _SIMULATORS[name] = {"css": css, "js": js, "html": body}
        except Exception as e:
            print(f"  [WARN] No se pudo cargar {f.name}: {e}")


def get_simulator(name):
    """Devuelve el dict {css, js, html} de un simulador o None."""
    return _SIMULATORS.get(name)


def build_simulators_css():
    """Concats todo el CSS de simuladores en un solo <style>."""
    css_parts = []
    for sim in _SIMULATORS.values():
        if sim["css"]:
            css_parts.append(sim["css"])
    if not css_parts:
        return ""
    return "<style>\n" + "\n\n".join(css_parts) + "\n</style>"


def build_simulators_js():
    """Envuelve todo el JS de simuladores en un <script> autocontenido."""
    js_parts = []
    for name, sim in _SIMULATORS.items():
        if sim["js"]:
            js_parts.append(f"/* === {name} === */\n{sim['js']}")
    if not js_parts:
        return ""
    return "<script>\n(function(){\n" + "\n\n".join(js_parts) + "\n})();\n</script>"


# ---------------------------------------------------------------------------
# Code array
# ---------------------------------------------------------------------------
def build_code_array(code_snippets):
    def safe(code):
        code = code.replace("\\", "\\\\").replace("`", "\\`")
        code = code.replace("${", "${''+")
        return code
    lines = ["var CODE = {"]
    for key, entry in code_snippets.items():
        lang = entry.get("lang", "text")
        title = entry.get("title", key)
        title_esc = title.replace("\\", "\\\\").replace('"', '\\"')
        code = safe(entry.get("code", ""))
        lines.append(f'  "{key}": {{ title: "{title_esc}", lang: "{lang}", code: `{code}` }},')
    lines.append("};")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Nav items
# ---------------------------------------------------------------------------
def build_nav_items(bloques):
    navs = []
    for i, b in enumerate(bloques):
        num = b.get("numero", str(i + 1))
        titulo = b.get("titulo", f"Bloque {i+1}")
        anchor = b.get("anchor") or slug(titulo)
        tag = b.get("tag", num)
        navs.append(f'  <a class="nav-link" href="#{anchor}"><span class="tag">{h.escape(tag)}</span> {h.escape(titulo)}</a>')
    return "\n".join(navs)


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------
def build_content(bloques):
    html_parts = []
    for b in bloques:
        tipo = b.get("tipo", "texto")
        anchor = b.get("anchor") or slug(b.get("titulo", ""))
        titulo = b.get("titulo", "")
        icono = b.get("icono", "📋")
        tiempo = b.get("tiempo", "")
        contenido = b.get("contenido", "")
        sec_num = b.get("sec_num", "")

        html_parts.append(f'<section id="{anchor}">')

        head_parts = [f'<span class="sec-num">{sec_num}</span>']
        if titulo:
            head_parts.append(f"<h2>{icono} {titulo}</h2>")
        if tiempo:
            head_parts.append(f'<span class="time-badge">⏱ {tiempo}</span>')
        html_parts.append(f'  <div class="sec-head">{"".join(head_parts)}</div>')

        if tipo == "texto":
            html_parts.append(f"  {contenido}")

        elif tipo == "texto_codigo":
            html_parts.append(f"  {contenido}")
            for snippet_id in b.get("codigo", []):
                html_parts.append(f'  <div class="code" data-code="{snippet_id}"></div>')

        elif tipo == "reto":
            html_parts.append(f'  <div class="reto" data-reto>')
            html_parts.append(f'    <div class="reto-head">')
            html_parts.append(f'      <button class="reto-check" type="button" aria-pressed="false"><span class="box"></span>{b.get("enunciado", "")}</button>')
            html_parts.append(f"    </div>")
            html_parts.append(f"    {contenido}")
            for snippet_id in b.get("codigo", []):
                html_parts.append(f'    <div class="code" data-code="{snippet_id}"></div>')
            html_parts.append(f"  </div>")

        elif tipo == "piensa":
            html_parts.append(f'  <div class="piensa">')
            if b.get("titulo"):
                html_parts.append(f'    <div class="ptitle">{b["titulo"]}</div>')
            html_parts.append(f"    {contenido}")
            html_parts.append(f"  </div>")

        elif tipo == "callout":
            cls = b.get("variante", "tip")
            html_parts.append(f'  <div class="{cls}">')
            html_parts.append(f"    {contenido}")
            html_parts.append(f"  </div>")

        elif tipo == "tabla":
            html_parts.append(f'  <div class="tw">')
            html_parts.append(f"    {contenido}")
            html_parts.append(f"  </div>")

        elif tipo == "componente":
            comp_name = b.get("nombre", "")
            sim = get_simulator(comp_name)
            if sim:
                html_parts.append(f"  <!-- simulador: {comp_name} -->")
                html_parts.append(f"  {sim['html']}")
            else:
                html_parts.append(f"  <!-- componente: {comp_name} (no encontrado) -->")
                html_parts.append(b.get("html", ""))

        else:
            html_parts.append(f"  {contenido}")

        html_parts.append("</section>")

    return "\n".join(html_parts)


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------
def generate(theme, title, sig, yaml_file, output_file, data=None):
    # Cargar plantilla y tema
    template = load_file(TEMPLATE_FILE)
    # Acepta nombre de tema (busca en temas/) o ruta directa a archivo CSS
    if theme and (theme.startswith("/") or theme.startswith("\\") or ":" in theme or "\\" in theme or theme.endswith(".css")):
        tema_file = Path(theme)
    else:
        tema_file = TEMAS_DIR / f"{theme}.css"
    if not tema_file.exists():
        print(f"ERROR: Tema '{theme}' no encontrado.")
        print(f"Temas disponibles en {TEMAS_DIR}:")
        for t in sorted(TEMAS_DIR.glob("*.css")):
            print(f"  - {t.stem}")
        sys.exit(1)
    css_theme = load_file(tema_file)

    # Cargar contenido JSON/YAML
    if yaml_file:
        yaml_path = str(yaml_file)
        if yaml_path.endswith(".json"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            try:
                import yaml
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except ImportError:
                print("ERROR: Este script necesita PyYAML para archivos .yaml.")
                print("   Instálalo con: pip install pyyaml")
                print("   O usa un archivo .json en su lugar.")
                sys.exit(1)
    elif data is None:
        data = {"bloques": []}

    # Validar esquema mínimo del contenido
    if not isinstance(data, dict):
        print("ERROR: El archivo de contenido debe ser un objeto JSON/YAML válido.")
        sys.exit(1)
    if "bloques" not in data and not data.get("meta", {}).get("title"):
        print("ERROR: El contenido debe tener 'meta.title' o 'bloques'.")
        sys.exit(1)

    # Metadatos
    meta = data.get("meta", {})
    title = meta.get("title", title)
    sig = meta.get("sig", sig)
    description = meta.get("description", "")
    intro = meta.get("introduccion", "")
    h1 = meta.get("h1", title)
    eyebrow = meta.get("eyebrow", "Guía interactiva del alumnado")
    intro_anchor = meta.get("intro_anchor", "Inicio")
    sec_num_checklist = meta.get("sec_num_checklist", str(len(data.get("bloques", [])) + 1))
    sec_num_ampliaciones = meta.get("sec_num_ampliaciones", str(len(data.get("bloques", [])) + 2))

    # Simulators (carga componentes sim-*.html de componentes/)
    load_simulators()

    # Contenido
    bloques = data.get("bloques", [])
    content_html = build_content(bloques)

    # Nav items
    nav_items = build_nav_items(bloques)

    # CODE array
    code_snippets = data.get("code_snippets", {})
    code_js = build_code_array(code_snippets)

    # CHECKLIST
    checklist = data.get("checklist", [])
    checklist_js = json.dumps(checklist, ensure_ascii=False)

    # AMPLIACIONES
    ampliaciones = data.get("ampliaciones", [])
    ampliaciones_js = json.dumps(ampliaciones, ensure_ascii=False)

    # Custom JS
    custom_js = data.get("custom_js", "")

    # Calcular total de retos para la barra de progreso
    total_rets = sum(1 for b in bloques if b.get("tipo") == "reto")
    total_check = len(checklist)
    total = total_rets + total_check

    # Simulators CSS y JS
    simulators_css = build_simulators_css()
    simulators_js = build_simulators_js()
    simulators_html = simulators_css + "\n" + simulators_js

    # Reemplazar placeholders
    replacements = {
        "{{TITLE}}": title,
        "{{DESCRIPTION}}": description,
        "{{SIG}}": sig,
        "{{TITLE_SHORT}}": title,
        "{{TOTAL}}": str(total),
        "{{INTRO_ANCHOR}}": intro_anchor,
        "{{NAV_ITEMS}}": nav_items,
        "{{EYEBROW}}": eyebrow,
        "{{H1}}": h1,
        "{{INTRO}}": intro,
        "{{CONTENT}}": content_html,
        "{{SEC_NUM_CHECKLIST}}": sec_num_checklist,
        "{{SEC_NUM_AMPLIACIONES}}": sec_num_ampliaciones,
        "{{CSS_THEME}}": css_theme,
        "{{CODE_ARRAY}}": code_js,
        "{{CHECKLIST}}": checklist_js,
        "{{AMPLIACIONES}}": ampliaciones_js,
        "{{CUSTOM_JS}}": custom_js,
        "{{SIMULATORS}}": simulators_html,
    }

    output = template
    for placeholder, value in replacements.items():
        output = output.replace(placeholder, value)

    # Guardar
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"[OK] Guia generada: {output_file}")
    print(f"     Tema: {theme}")
    print(f"     Bloques: {len(bloques)}")
    print(f"     Code snippets: {len(code_snippets)}")
    print(f"     Checklist: {len(checklist)}")
    print(f"     Ampliaciones: {len(ampliaciones)}")
    print(f"     Total progreso: {total}")


def main():
    parser = argparse.ArgumentParser(description="Generador de guías interactivas MiniMax")
    parser.add_argument("--title", default="Nueva Guía", help="Título de la guía")
    parser.add_argument("--sig", default="DAM", help="Sigla del ciclo (DAM, DAW, ASIR...)")
    parser.add_argument("--theme", default="paper_cream",
                        help="Nombre de tema (paper_cream, dark_modern, blueprint, matrix, light_academic) o ruta a archivo CSS")
    parser.add_argument("--yaml", type=Path, help="Fichero YAML con el contenido")
    parser.add_argument("--output", type=Path, default=Path("guia.html"), help="Fichero de salida")
    parser.add_argument("--list-themes", action="store_true", help="Lista los temas disponibles")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo (preguntas por CLI)")

    args = parser.parse_args()

    if args.list_themes:
        print("Temas disponibles:")
        for t in sorted(TEMAS_DIR.glob("*.css")):
            print(f"  - {t.stem}")
        return

    if args.interactive:
        print("\n[CLI] Generador interactivo de guias\n")
        title = input("Título de la guía: ").strip()
        sig = input("Sigla (DAM/DAW/ASIR): ").strip() or "DAM"
        theme = input("Tema [paper_cream/dark_modern/blueprint/matrix]: ").strip() or "paper_cream"
        eyebrow = input("Eyebrow (descripcion corta): ").strip()

        # Generar YAML mínimo
        data = {
            "meta": {
                "title": title,
                "sig": sig,
                "introduccion": input("Introducción (1-2 frases): ").strip(),
                "h1": title,
                "eyebrow": eyebrow,
                "description": eyebrow
            },
            "bloques": [],
            "checklist": [],
            "ampliaciones": [],
            "code_snippets": {}
        }

        # Preguntar bloques
        print("\n[*] Bloques (enter para terminar):")
        while True:
            titulo = input("  Bloque - Título (o vacío para terminar): ").strip()
            if not titulo:
                break
            bloque = {
                "titulo": titulo,
                "tipo": input("  Tipo [texto/texto_codigo/reto/piensa/callout]: ").strip() or "texto",
                "sec_num": input("  Número de sección: ").strip() or "1",
                "contenido": input("  Contenido HTML: ").strip(),
            }
            data["bloques"].append(bloque)

        output = Path(f"{slug(title)}.html")
        with open("guia_content_temp.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
        args.yaml = Path("guia_content_temp.yaml")
        args.theme = theme
        args.output = output
        args.sig = sig
        args.title = title
        print()

    if not args.yaml and not args.interactive:
        parser.print_help()
        print("\nERROR: Indica --yaml o usa --interactive")
        sys.exit(1)

    generate(args.theme, args.title, args.sig, args.yaml, args.output)


if __name__ == "__main__":
    main()
