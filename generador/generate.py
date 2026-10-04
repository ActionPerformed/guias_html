#!/usr/bin/env python3
"""
Generador de guías interactivas — MiniMax
Uso:
  python generate.py --title "Titulo" --sig "DAM" --yaml contenido.yaml --theme paper_cream --output guia.html
  python generate.py --title "Titulo" --sig "DAW" --interactive
"""

import argparse
import json
import sys
import os
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
    return text.lower().replace(" ", "-").replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("¿", "").replace("?", "").replace("¡", "").replace("!", "").replace(":", "").replace(",", "").replace(".", "").strip("-")


def build_code_array(code_snippets):
    """Genera el objeto CODE de JavaScript."""
    lines = ["var CODE = {"]
    for key, entry in code_snippets.items():
        lang = entry.get("lang", "text")
        title = entry.get("title", key)
        code = entry.get("code", "")
        safe = code.replace("\\", "\\\\").replace("`", "\\`").replace("${", "${")
        lines.append(f'  "{key}": {{ title: "{title}", lang: "{lang}", code: `{safe}` }},')
    lines.append("};")
    return "\n".join(lines)


def build_nav_items(bloques):
    """Genera los items de navegación del sidebar."""
    navs = []
    for i, b in enumerate(bloques):
        num = b.get("numero", str(i + 1))
        titulo = b.get("titulo", f"Bloque {i+1}")
        anchor = b.get("anchor") or slug(titulo)
        tag = b.get("tag", num)
        navs.append(f'  <a class="nav-link" href="#{anchor}"><span class="tag">{tag}</span> {titulo}</a>')
    return "\n".join(navs)


def build_content(bloques):
    """Genera el HTML de los bloques de contenido."""
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

        # Cabecera de sección
        head_parts = [f'<span class="sec-num">{sec_num}</span>']
        if titulo:
            head_parts.append(f"<h2>{icono} {titulo}</h2>")
        if tiempo:
            head_parts.append(f'<span class="time-badge">⏱ {tiempo}</span>')
        html_parts.append(f'  <div class="sec-head">{"".join(head_parts)}</div>')

        # Contenido según tipo
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
            # Componente pre-hecho incluido inline
            comp_name = b.get("nombre", "")
            html_parts.append(f"  <!-- componente: {comp_name} -->")
            html_parts.append(b.get("html", ""))

        else:
            html_parts.append(f"  {contenido}")

        html_parts.append("</section>")

    return "\n".join(html_parts)


def generate(theme, title, sig, yaml_file, output_file):
    # Cargar plantilla y tema
    template = load_file(TEMPLATE_FILE)
    tema_file = TEMAS_DIR / f"{theme}.css"
    if not tema_file.exists():
        print(f"ERROR: Tema '{theme}' no encontrado en {TEMAS_DIR}")
        print(f"Temas disponibles: {[t.name for t in TEMAS_DIR.glob('*.css')]}")
        sys.exit(1)
    css_theme = load_file(tema_file)

    # Cargar contenido JSON
    if yaml_file:
        yaml_path = str(yaml_file)
        if yaml_path.endswith(".json"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            # Intentar YAML si está disponible
            try:
                import yaml
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except ImportError:
                print("ERROR: Este script necesita PyYAML para archivos .yaml.")
                print("   Instálalo con: pip install pyyaml")
                print("   O usa un archivo .json en su lugar.")
                sys.exit(1)
    else:
        data = {"bloques": []}

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
                        choices=["paper_cream", "dark_modern", "blueprint", "matrix"],
                        help="Tema visual")
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
