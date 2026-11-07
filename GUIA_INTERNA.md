# Guía interna del proyecto — `guias_html`

> **Qué es este documento.** Mapa interno para agentes que trabajan en este repositorio: qué
> contiene cada guía, cómo se relacionan, a quién apuntan y con qué nivel, qué convenciones se
> repiten y cómo se verifica el trabajo. Escrito el 2026-11-08 a partir de la lectura de las 40
> guías publicadas, el `generador/`, el `readme.md`, el `index.html` y el histórico de git.
>
> **Compañero:** `.claude/skills/guide-from-md/SKILL.md` es el recetario técnico de autoría
> (plantilla, componentes, JS mínimo). Este documento explica **por qué** el repo es como es; el
> skill explica **cómo** escribir una guía nueva.

---

## 0. TL;DR — lo que hay que saber en 10 líneas

1. **40 guías** catalogadas: 22 de módulo (ASETE 9, IAW 6, PMDM 7) + 18 generales en la raíz.
   Cada una es **un HTML único autocontenido** (CSS + JS dentro, 0 scripts externos, 0 hojas de
   estilo propias: la única petición externa es Google Fonts).
2. **La portabilidad manda sobre la limpieza**: el HTML se duplica en cada fichero a propósito.
   No propongas extraer CSS/JS a ficheros compartidos: rompe el formato.
3. **No hay hoja de estilo compartida.** Cada guía tiene su propia paleta, su nomenclatura de
   clases y su JS. Lo que se comparte es el *patrón conceptual* (callout, acordeón, reveal,
   pestañas, reto con checkbox, código con copiar, progreso, glosario), no el código.
4. **El repo tiene tres módulos** con públicos y niveles distintos (ASETE, IAW, PMDM) más un
   bloque de guías generales transversales.
5. **El alienaje del alumno es Java** (viene de 1º DAW/DAM). Las guías hacen de puente explícito
   Java → PHP y Java → Kotlin. Es el recurso pedagógico más rentable del repo.
6. **El generador (`generador/`)** es un camino de autoría alternativo a la redacción manual.
   Solo una guía publicada tiene sus huellas, y probablemente se escribió a mano con ese estilo.
7. **`index.html` + `readme.md` son el catálogo** y el único grafo de navegación: entre guías no
   hay ni un `href` interno.
8. **Reglas duras**: push solo con confirmación explícita; nada fuera de la carpeta del repo sin
   permiso; pedir acceso si hace falta una carpeta temporal del sistema.
9. **Antes de dar algo por bueno hay que verificarlo**: compilador oficial de Kotlin + Chrome
   headless, y comprobar que los bloques de código **no han cambiado** si el trabajo era de
   maquetación.
10. **Deuda conocida**: `index.html` enlaza a `README.md` pero el fichero es `readme.md` → 404 en
    GitHub Pages; el contador de guías del hero está desfasado; `utilidades/` no está enlazada;
    las versiones de Docker divergen entre guías; el andamiaje de `.claude/` es heredado de otro
    proyecto y engaña.

---

## 1. Propósito y filosofía

Definidos en `readme.md` y repetidos en el pie de `index.html`:

- **El conocimiento es un derecho.** Las guías son «cápsulas informativas portables»: un
  archivo que lleva todo lo necesario para funcionar sin servidor, sin instalación y sin
  dependencias.
- **No son textos que se leen, son espacios que se exploran.** El diseño visual busca invitar a
  manipular código, romper cosas y observar qué cambia. *Aprender haciendo*.
- **Libre y gratuito**: sin muros de pago, sin cuentas. Se invita a compartir, crear nuevas guías
  y adaptarlas a otros niveles, contextos o idiomas.
- **Autoría asistida por IA con revisión humana**:
  1. *Outline* estructurado con un modelo de IA.
  2. HTML completo con CSS/JS embebidos aplicando el diseño visual.
  3. **Revisión manual** de errores técnicos (HTML/CSS/JS) y de concepto (contenido, coherencia
     pedagógica, claridad expositiva).

### Consecuencias prácticas

| Decisión | Motivo | Qué implica para el agente |
|---|---|---|
| Un solo `.html` por guía | Portabilidad: se puede enviar por correo, abrir sin internet, archivar | No dividas en `style.css`/`app.js` aunque «suene más limpio» |
| CSS y JS embebidos | Mismo motivo | Duplica el código; es aceptable y buscado |
| Sin framework ni build | Cero dependencias, cero mantenimiento | Nada de React/Vite/npm en las guías |
| Google Fonts como única petición externa | Legibilidad sin romper la portabilidad | Mantener: con `system-ui` la guía sigue leyéndose |
| Estética oscura con acentos | «Alta carga visual» como objetivo didáctico | Es requisito de marca, no decoración |

---

## 2. Mapa del repositorio

```
guias_html/
├── index.html            Catálogo con buscador y filtros (punto de entrada público)
├── readme.md             Índice completo + manifiesto del proyecto (GitHub Pages)
├── CLAUDE.md             Instrucciones de trabajo para el agente (gitignored)
├── GUIA_INTERNA.md       ← este documento
├── .claude/              Configuración, skills, hooks, commands (gitignored)
│   ├── skills/guide-from-md/   Recetario de autoría (plantilla + componentes + JS)
│   └── skills/add-simulator/   Recetario para añadir simuladores interactivos
├── PMDM/   ASETE/   IAW/  Guías de módulo (7 + 9 + 6)
├── guia_*.html           18 guías generales transversales
├── generador/            Pipeline de autoría por plantillas (temas + componentes)
├── utilidades/           cv-form.html, cv-pdf.html (herramientas de alumno, no guías)
├── assets/               pizarra.png
└── temp/                 Zona de trabajo gitignored (informes, scripts, toolchain)
```

### Reglas de nombres

- Guías de módulo: `MODULO - UTn.html`, `MODULO - ACT n.m.html`, con prefijo de módulo
  (`PMDM`, `ASETE`, `IAW`).
- Guías generales: convención **mixta** e inconsistente — `guia_tema.html` (subrayado:
  `guia_git`, `guia_sql`, `guia_php`…) frente a `guia-tema.html` (guion: `guia-ia-fp`,
  `guia-que-ia-usar`). **No asumas un patrón** al escribir scripts que las enumeren.
- `utilidades/` y `generador/` son carpetas de apoyo; no son guías.

---

## 3. Los tres módulos y el bloque general

| Módulo | Siglas | Ciclo | Eje tecnológico | Nº |
|---|---|---|---|---|
| **ASETE** | Arquitectura de Servidor en Entornos de Trabajo Estructurados | 2º DAM / 2º ASIR | PHP 8, Docker, Composer, Laravel 12, MariaDB | 9 |
| **IAW** | Implantación de Aplicaciones Web | 2º ASIR | Docker, Nginx/Apache, MariaDB, WordPress, Nextcloud | 6 |
| **PMDM** | Programación Multimedia y Dispositivos Móviles | 2º DAM | Android Studio, Kotlin, Jetpack Compose, Room, DataStore | 7 |
| **Generales** | — | 1º/2º DAW, 2º ASIR, Bachillerato | CSS, redes, Linux, Git, SQL, PHP, LaTeX, IA | 18 |

### Niveles pedagógicos que se manejan

| Nivel | Ejemplos | Tono |
|---|---|---|
| **Iniciación absoluta** | `guia_linux`, `guia_batch_windows`, `guia-ia-*` | Sin suponer nada; se explica desde el qué |
| **Refuerzo de 1º** | `guia_redes_daw`, `guia_css_daw`, `guia_responsive_bootstrap` | Repaso y ampliación de lo ya visto |
| **Puente desde Java** | `ASETE ACT 2.1/2.2`, `PMDM UT1 Kotlin` | Compara con Java explícitamente |
| **Aplicación autónoma** | `IAW ACT 1.1–4.1`, `ASETE ACT 1.2/3.1`, `PMDM ACT 2.1–4.1` | El alumno ejecuta, se equivoca y depura |
| **Autonomía total** | `IAW ACT 3.1` (niveles «Guiado/Semilibre/Libre»), `guia_proyecto_asir` | Entrega libre con criterios de evaluación |
| **Divulgativo / andamiaje** | `guia-que-ia-usar`, `guia_prompts`, `guia-ia-*` | Decisiones, matrices, plantillas |

---

## 4. Catálogo: guías de módulo

### ASETE (2º DAM / ASIR — PHP y Laravel)

| Fichero | Propósito | Formato | Tiempo |
|---|---|---|---|
| `ASETE - UT0.html` | Teoría de guiones de servidor (PHP 8.x) + seguridad transversal | Unidad con test diagnóstico, proyecto integrador y evaluación final | 40 h |
| `ASETE - UT1.html` | Versión **ejecutable** del mismo temario: intérprete PHP reducido en JS + 6 actividades | Banco de pruebas en el navegador | — |
| `ASETE - ACT 1.1.html` | Mini-Biblioteca PHP en playground online (login simulado) | Actividad evaluable por bloques | 4 h |
| `ASETE - ACT 1.2.html` | Despliegue de un stack LAMP con Docker Compose | Guía práctica + simulador del ciclo de vida | 1 h |
| `ASETE - ACT 1.3.html` | MiniApp de Tareas (login, roles, PDO, sesiones) sobre el stack de 1.2 | Actividad por bloques con checklist final | 4 h / 2 sesiones |
| `ASETE - ACT 2.1.html` | Salto a POO en PHP: clases, herencia, interfaces, traits, repositorio | Actividad con rúbrica y glosario Java→PHP | 6 h / 3 sesiones |
| `ASETE - ACT 2.2.html` | Namespaces/PSR-4/Composer, excepciones propias, `strict_types`, PSR-12 | Actividad «profesionalizar» antes de Laravel | 4 h / 2 sesiones |
| `ASETE - ACT 3.1 - PUENTE.html` | Traducción código-a-código de la MiniApp a Laravel (rutas, controladores, Eloquent, Blade) | **Documento de lectura**: sin entrega, sin cronómetro | — |
| `ASETE - ACT 3.1.html` | Taller: montar Laravel 12 + Apache + PHP 8.4 + MariaDB 11.4 en Docker | Taller de 7 pasos con checklist y «SOS» | 4 h / 8 h (ver §12) |

### IAW (2º ASIR — LEMP y autoaloja)

| Fichero | Propósito | Formato | Tiempo |
|---|---|---|---|
| `IAW - UT1.html` | Teoría: servidores de aplicaciones web y arquitectura LEMP | Unidad teórica + mapa concepto→práctica | 4–6 h |
| `IAW - UT4.html` | Ofimática web: clasificación por 3 ejes, catálogo interactivo, ODF vs OOXML | Teoría + autoevaluación con selectores | 2 h |
| `IAW - ACT 1.1.html` | Despliegue del stack LEMP (Nginx + MariaDB + phpMyAdmin) | Práctica paso a paso + 8 preguntas sin solución | 6–8 h |
| `IAW - ACT 2.1.html` | Instalación y securización de WordPress sobre el LEMP previo | Práctica + 10 autochecks con solución oculta | 5–6 h |
| `IAW - ACT 3.1.html` | Personalización integral de WordPress (9 actividades) | Proyecto con **3 niveles de libertad** + hitos de captura | 8 h |
| `IAW - ACT 4.1.html` | Nextcloud sobre LEMP: intranet, usuarios, backups, cron | Práctica en 4 sesiones + entregable de documentación | 8 h / 4 sesiones |

### PMDM (2º DAM — Android y Kotlin)

| Fichero | Propósito | Formato | Tiempo |
|---|---|---|---|
| `PMDM - UT1 - Kotlin.html` | Kotlin desde cero, para Android y para quien viene de Java | 13 secciones, 86 bloques de código, 10 actividades con solución, glosario, buscador, hoja de impresión | ≈ 11 h |
| `PMDM - UT1 - Android.html` | Android Studio panel a panel: instalación, emulador, Logcat, estructura de proyecto | 19 capítulos, atajos, glosario | — |
| `PMDM - ACT 1.1.html` | Introductoria: explorar el IDE, personalizar, depurar y documentar | Actividad con rúbrica y reflexión | 4 h |
| `PMDM - ACT 2.1.html` | Pantalla de Login en Compose: proyecto, UI, estado, foco, accesibilidad | Actividad con simulador de pantalla y autoevaluación | — |
| `PMDM - ACT 2.2.html` | Registro + NavHost + Scaffold + Diálogos, sobre la 2.1 | Actividad con simulador de grafo de navegación y rúbrica | — |
| `PMDM - ACT 3.1.html` | CRUD con Room, DataStore, ViewModel, notificaciones, APK firmado | Actividad en 7 pasos + laboratorio de persistencia | — |
| `PMDM - ACT 4.1.html` | Conectividad avanzada: API REST con errores, Bluetooth, SMS, Wi-Fi Direct | Actividad por fases con tiempos + laboratorio | ≈ 6 h |

---

## 5. Catálogo: guías generales (18)

| Fichero | Tema | Público | Nivel |
|---|---|---|---|
| `guia_linux.html` | Sistema de ficheros, permisos, terminal | 1º DAW | básico |
| `guia_batch_windows.html` | Scripts `.BAT`/`.CMD`, actividades resueltas | 1º DAW | básico |
| `guia_redes_daw.html` | OSI, TCP/IP, IPv4, subredes, VLSM + calculadoras | 1º DAW | medio |
| `guia_css_daw.html` | Selectores, box-model, flexbox, animaciones | 2º DAW | medio |
| `guia_responsive_bootstrap.html` | De web fija a responsive (Bootstrap) | DAW | básico-medio |
| `guia_react_encuesta.html` | App de votaciones en React (hooks, `useState`) | DAW | medio |
| `guia_git.html` | Git línea a línea + simulador de terminal y grafo | DAM/DAW/ASIR | básico |
| `guia_sql.html` | SQL progresivo, joins, subconsultas + consola SQL en vivo | 1º ASIR/DAM/DAW | medio-avanzado |
| `guia_php.html` | Referencia rápida: PDO, formularios, seguridad | 2º DAM/ASIR | medio-avanzado |
| `guia_valor_vs_referencia.html` | Valor vs referencia en Java y PHP + simulador de memoria | DAM/ASIR | medio |
| `guia_php_vulnerabilidad.html` | Parchear PHP-FPM y WordPress en Docker | perfil admin | avanzado |
| `guia_proyecto_asir.html` | Apoyo al proyecto de fin de ciclo (fases, roles, actas) | 2º ASIR | organizativo |
| `guia_latex.html` | Composición tipográfica, fórmulas, taller de redacción | público general | iniciación |
| `guia_lean.html` | Lean 4: tipos, Curry-Howard, tácticas, Mathlib | matemáticas / CS | avanzado |
| `guia_prompts.html` | Metaprompt: entrenamiento de 4 semanas en ingeniería de prompts | cualquier FP | transversal |
| `guia-que-ia-usar.html` | Qué IA usar para cada tarea (herramientas, privacidad) | docentes y estudiantes | transversal |
| `guia-ia-bachillerato.html` | IA como herramienta de estudio para la EBAU | 2º Bachillerato | básico |
| `guia-ia-fp.html` | IA como herramienta de estudio en FP (SMR/ASIR/DAM/DAW) | 2º FP | básico |

`guia-ia-bachillerato.html` y `guia-ia-fp.html` son **gemelos**: mismo CSS, mismas 4 secciones
(`01 Prompting / 02 Proyectos / 03 Ideas / 04 Uso responsable`); solo cambian los ejemplos.

---

## 6. Cómo se relacionan las guías

### 6.1 Mapa de secuencia

```
ASETE (2º DAM)
  UT0 (teoría 40 h) ─┬─► UT1 (banco de pruebas ejecutable)
                      └─► ACT 1.1 (biblioteca en playground)
                             ACT 1.2 (stack LAMP con Docker) ──► ACT 1.3 (MiniApp Tareas)
                                                    ACT 2.1 (POO) ──► ACT 2.2 (Composer/PSR)
                                                                          │
                                              ACT 3.1 - PUENTE (lectura) ───┤
                                              ACT 3.1 (taller Laravel) ◄─────┘
                                              ✗ falta la actividad 3.2

IAW (2º ASIR)
  UT1 (teoría LEMP) ──► ACT 1.1 (LEMP) ──► ACT 2.1 (WordPress) ──► ACT 3.1 (personalización)
  UT4 (ofimática web) ───────────────────────────────► ACT 4.1 (Nextcloud)
  (UT2/UT3 no existen como guía; el temario sí las tiene)

PMDM (2º DAM)
  UT1 Kotlin ──┬──► UT1 Android (hermano: el IDE)
               └──► ACT 1.1 (IDE y Logcat)
                     ACT 2.1 (Login Compose) ──► ACT 2.2 (NavHost/Registro)
                                                    ACT 3.1 (Room/DataStore/ViewModel)
                                                    ACT 4.1 (Red/Bluetooth/SMS)

Generales: transversal, sin secuencia interna (se citan por tema, no por módulo)
```

### 6.2 Reglas de prerrequisito reales

- **ASETE**: `UT0/UT1` → `1.1` → **`1.2` (Docker) → `1.3`** → `2.1` → `2.2` → `3.1`.
  `1.2` es infraestructura y `1.3` la da por hecha (habla de «la configuración base que te ha
  dado tu profesor»), así que el orden natural es `1.1 → 1.2 → 1.3`.
- **IAW**: la numeración de las ACT es la del temario, no una secuencia lineal: `1.1` → `2.1` →
  `3.1` forman la línea WordPress; `4.1` (Nextcloud) es otra línea, que se apoya en `UT4`.
- **PMDM**: `UT1 Kotlin` y `UT1 Android` son **paralelos** (uno el lenguaje, otro el IDE), y
  `ACT 1.1` los presupone. A partir de `2.1` cada ACT **amplía la anterior**: 2.2 añade
  navegación, 3.1 añade persistencia, 4.1 añade conectividad.
- **Cross-módulo**: `PMDM ACT 3.1` reutiliza los patrones de `ACT 2.2` (DataStore + ViewModel +
  corrutinas) y conecta con `ACT 4.1` por la arquitectura Android. Aun así, **no hay ni un solo
  `href` entre guías de módulos distintos**.

### 6.3 El alienaje pedagógico: Java

El primer curso es Java (1º DAW/DAM). Las guías lo asumen y lo aprovechan:

- `ASETE ACT 2.1` tiene un bloque *«POO en PHP vs Java: las diferencias que te van a morder»*,
  un *«Puente Java → PHP»* y un *«Glosario rápido PHP para gente que viene de Java»*.
- `ASETE ACT 2.2` traduce `package com.app.classes;` → `namespace App\Classes;`.
- `PMDM UT1 Kotlin` contrasta Kotlin↔Java en todo el temario (propiedades, `final` por defecto,
  `null` vs nullability, `when` vs `switch`).
- `guia_valor_vs_referencia.html` existe para eso: comparar los dos lenguajes.

**Es el recurso más rentable del repo. Cualquier guía nueva de un lenguaje de servidor o de
Android debería incluir el puente desde Java.**

---

## 7. El «estilo de casa»: qué se comparte y qué no

### 7.1 Lo que sí es una convención compartida

Patrones interactivos presentes en distinta medida según el módulo (frecuencia medida sobre los
ficheros con guía):

| Patrón | Ficheros | Para qué sirve |
|---|---|---|
| Callout (aviso / consejo / trampa) | 33 | Separar la explicación del matiz: `key` (idea), `tip` (recomendación), `warn` (trampa) |
| Bloque de código con botón copiar | 28 | El alumno pega el código en su editor |
| Checklist de comprobación | 20 | «¿lo he terminado?» — típico de las actividades |
| Actividad / reto con checkbox | 19 | Progreso real, no decorativo |
| Barra de progreso | 19 | Refleja el avance (retos marcados) |
| Pestañas | 14 | Comparativas lado a lado (Java↔Kotlin) |
| Reveal (solución oculta) | 14 | Que el alumno intente antes de ver |
| Glosario | 14 | Equivalente del término en el otro lenguaje |
| Acordeón | 12 | Detalle plegable (apartados, troubleshooting) |
| Impresión (`@media print`) | 10 | El alumno imprime o exporta a PDF |
| Simulador interactivo | 9 | Laboratorios: HTTP, URL, SQL, shell |
| Buscador | 5 | Localizar un concepto en una guía larga |

**La regla que se deduce:** el *qué* (callout, reto, reveal) es de casa; el *cómo* (nombres de
clase, paleta, markup) es de cada guía. Al tocar una guía existente, usa **sus** clases; al
escribir una nueva, elige las tuyas pero cumple el patrón.

### 7.2 Lo que NO se comparte (y por qué no lo «arregles» sin permiso)

- **Ni una hoja de estilo común.** 40 guías, 40 conjuntos de tokens CSS. Solo la más reciente
  (`PMDM UT1 Kotlin`) tiene un vocabulario estructurado y completo; el resto usa convenciones
  parciales (`codeblock__bar`, `cb-head`, `code-head`… son tres nombres distintos para lo mismo).
- **Ni una nomenclatura de clases común.** Cada guía inventa la suya: no hay un `.callout`
  compartido, hay `callout`, `tip`, `note`, `warn`, `box`, `piensa`, `banner`… según la guía.
- **Ni una paleta común.** Cada una define sus `--bg/--text/--accent`. Hay 5 combinaciones
  distintas de tipografías.
- **Ni un JS común.** Cada guía implementa su propio scrollspy, su propio copiador, su propio
  progreso.

**Consecuencia práctica:** cualquier refactor que intente unificar estilos es un cambio de
arquitectura, no una limpieza. Es legítimo, pero es una decisión del profesor, no tuya.

### 7.3 Las cuatro «generaciones» que conviven

| Generación | Guías | Rasgos |
|---|---|---|
| **Manual temprana** (jun–oct 2025) | `guia_batch_windows`, `guia_css_daw`, `guia_git`, `guia_linux`, `guia_redes_daw`, `guia_react_encuesta` | Clases sueltas, sin sistema de tokens maduro |
| **Generativa con plantilla** | `guia-ia-*`, `guia_prompts`, `index.html`, `utilidades/` | Sistema de diseño unificado (`--paper/--card/--cyan`; Instrument Serif + Work Sans + JetBrains Mono) |
| **Módulo por módulo** | `IAW/*`, `ASETE/*` | Cada módulo tiene su propia «casa» (IAW: 3 familias; ASETE: `sec-head`/`reto`/`reveal-box`) |
| **Madurada** (referencia) | `PMDM - UT1 - Kotlin`, `PMDM - ACT 2.1/2.2/3.1` | Tokens + JS con nombre + buscador + glosario + índice + imprimible + `.activity-meta` + menú lateral |

La cuarta es **el estándar al que deberían converger las nuevas guías**. Copia su estructura
(sin copiar sus clases, salvo que convenga) y añade lo que le falte: buscador, glosario, índice,
hoja de impresión.

### 7.4 El modelo PMDM (el esqueleto más repetido del repo)

`PMDM ACT 2.1`, `2.2`, `3.1` y `4.1` comparten casi literalmente este esqueleto de 20 bloques:

```
¿Qué vamos a construir? → Glosario mínimo → Estructura del proyecto → Conceptos fundamentales
→ Pasos numerados (con código y tiempos) → Simulador/Laboratorio interactivo
→ Pruebas en el emulador → Errores comunes y soluciones → Accesibilidad
→ Entregables → Checklist de autoevaluación → Rúbrica de evaluación
→ Estimación de tiempos → Recursos adicionales → Retos adicionales
```

Si quieres que una guía nueva se sienta del repo, usa **este** esqueleto.

---

## 8. Recetario de autoría

### 8.1 El recetario que ya existe (úsalo antes de inventar)

| Fichero | Qué te da |
|---|---|
| `.claude/skills/guide-from-md/SKILL.md` | Pipeline markdown → HTML: 4 temas visuales, esqueleto base, componentes (`reto`, `tip`, `piensa`, `reveal`, `grid/mini`), JS mínimo obligatorio (copiador, realce, retos, checklist, barra, scrollspy, toast) y checklist de salida |
| `.claude/skills/add-simulator/SKILL.md` | Cómo construir un simulador: qué conceptos se simulan, estructura `.sim-controls/.sim-output/.sim-state`, criterios de calidad |
| `generador/TEMAS.md` | Sistema de tokens CSS obligatorio (30 variables), clases de componentes, highlighter por lenguaje, accesibilidad (skip-link, `prefers-reduced-motion`) |

### 8.2 Los dos caminos de autoría

**A) Manual (el habitual).** Escribes el HTML a mano o con un modelo, con CSS y JS embebidos.
Es lo que se ha hecho con las 40 guías publicadas.

**B) Generador (`generador/`).** `generate.py` toma un JSON/YAML y produce un HTML único
combando `plantilla_base.html` + un tema CSS (`generador/temas/*.css`: `paper_cream`,
`dark_modern`, `blueprint`, `matrix`, `light_academic`); `generate_http.py` hace Markdown → HTML.

```bash
python generador/generate.py --title "Título" --sig "DAM" --yaml contenido.yaml \
       --theme paper_cream --output guia.html
python generador/generate_http.py --input guia.md --output guia.html --theme temas/blueprint.css
```

Entrada (JSON o YAML): `meta{}`, `bloques[]` (`tipo` ∈ texto | texto_codigo | reto | piensa |
callout | tabla | componente), `code_snippets{}`, `checklist[]`, `ampliaciones[]`, `custom_js`.
Los simuladores se inyectan con `tipo: componente, nombre: sim-url|sim-request|sim-codes`.

> **Trampas del generador** (verificadas): el bundle de simuladores concatena varios `var sim`
> en la misma IIFE (colisión real de ámbito y un `return` prematuro aborta los siguientes);
> `_extract_component` deja el `<script>` del componente pegado en el contenido, así que corre dos
> veces; `sim-quiz` se carga automáticamente pese a documentarse como legado; `--interactive` está
> roto (usa `yaml.dump` sin importar `yaml`); la nav de la plantilla enlaza `#objetivos`, sección
> que el generador nunca emite (enlace roto por defecto); el `str.replace` de los `{{TOKEN}}` puede
> pisar un placeholder que aparezca en el contenido.

### 8.3 Esqueleto de una guía nueva

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Título · Subtítulo · MÓDULO</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=…&display=swap" rel="stylesheet">
  <style>/* tokens en :root + componentes */</style>
</head>
<body>
  <a class="skip-link" href="#main">Saltar al contenido</a>
  <header class="topbar">… marca, navegación, progreso …</header>
  <div class="shell">
    <nav class="sidebar">… anclas …</nav>
    <main id="main">
      <section id="…">…</section>
    </main>
  </div>
  <script>/* vanilla, IIFE, "use strict" */</script>
</body>
</html>
```

Requisitos mínimos (síntesis de `guide-from-md` + `TEMAS.md`):

- Tokens CSS como variables en `:root`; nada de colores sueltos.
- `skip-link` y `prefers-reduced-motion`.
- Copiador en cada bloque de código; realce con clases por token (`.kw`, `.fn`, `.str`, `.cmt`…).
- Navegación con anclas + scrollspy (`IntersectionObserver`).
- Callout con variantes (idea / consejo / trampa).
- JS en IIFE con `"use strict"`, sin librerías.
- `pre.code` con `white-space: pre` y scroll horizontal; `&lt;`/`&gt;`/`&amp;` escapados.
- Cierre del documento: **actualizar `readme.md` y el array `GUIAS` de `index.html`** con la entrada
  nueva (el contador del hero está escrito a mano en `index.html:562`).

### 8.4 Checklist de verificación (el que uso yo)

1. **Sintaxis**: `<script>` sin errores en la consola (Chrome headless `--dump-dom`).
2. **Estructura**: contadores coherentes (`section`, `pre.code`, `tab-btn`, `acc-item`, `activity`).
3. **Balance de etiquetas**: `<div>`, `<p>`, `<li>`, `<a>`, `<dl>` abiertos = cerrados.
4. **Anclas**: todo `href="#…"` tiene destino; todo `id` es único.
5. **Código real compilado** (ver §10), no solo «parece correcto».
6. **Byte-a-byte**: si el cambio era de maquetación, los bloques de código deben salir idénticos
   (se extraen y se comparan contra la versión anterior).
7. **Print**: emular `media: print` y comprobar que se ocultan nav/buscador/progreso y se abren
   acordeones, pestañas y soluciones.
8. **Responsive**: comprobación a 1400 px (escritorio), 960 px y 760 px (móvil).
9. **Enlaces externos**: que devuelvan 200.

---

## 9. Taxonomía de auditoría pedagógica (reutilizable)

Es el esquema que uso para los informes de `temp/informe_*.md` (Laravel, Kotlin, Nextcloud). Sirve
para auditar cualquier guía nueva y produce un informe accionable:

| Apartado | Qué busca | Gravedad |
|---|---|---|
| **2.1 Errores reales de código o de salida** | Fragmentos que no compilan, salidas comentadas falsas | ALTA |
| **2.2 Conceptos mal explicados o afirmaciones inexactas** | Metáforas que engañan («inmutable», «evita NPE», «100 % interoperable») | ALTA |
| **2.3 Conceptos usados sin definir** | Términos que aparecen sin explicar (`field`, smart cast, `Flow`) | ALTA |
| **2.4 Rupturas cognitivas desde Java** | Donde el modelo mental de Java engaña | ALTA |
| **2.5 Encuadre y evaluación** | Objetivos, tiempos, entregables, rúbrica, autoevaluación | MEDIA |
| **2.6 Autonomía del documento** | Índice, glosario, buscador, ritmo, imprimible | MEDIA |
| **2.7 Vigencia del contenido** | Versiones desfasadas, enlaces archivados, APIs obsoletas | MEDIA |
| **2.8 Coherencia con el resto del módulo** | Terminología, stack y versiones divergentes entre guías | MEDIA |

Formato de la entrega: `temp/informe_<tema>.md` (gitignored), con la plantilla de
`temp/informe_laravel.md`: *0 Metodología · 1 Lo que ya funciona bien · 2 Carencias · 3
Priorización · 4 Plan por fases · 5 Verificación*. Al final, una tabla **«Correcciones
aplicadas (X1–Xn)»** que mapea cada hallazgo con su arreglo, para que el profesor pueda
auditarlo.

---

## 10. Cómo verificar (herramientas)

### 10.1 Compilar el código de ejemplo

- **Compilador**: JetBrains oficial **Kotlin 2.0.21**, ya descargado en `temp/kt-tool/`
  (`https://github.com/JetBrains/kotlin/releases/download/v2.0.21/kotlin-compiler-2.0.21.zip`),
  con **JDK 17** (`C:/Program Files/Java/jdk-17`) y `coroutines.jar` (kotlinx-coroutines
  1.8.1) en el classpath.
- **Dos modos**: fichero `.kt` (multi-fichero, con `package` reales) y `kotlinc -script f.kts`
  (equivalente al Playground: en este modo los `import` deben ir **primero**).
- Scripts en `temp/kt-check/`: `check4.sh` (compila y **ejecuta** cada fragmento, con timeout de
  60 s para detectar bucles infinitos), `extract.js` (extrae los bloques `<pre class="code">`).

### 10.2 Chrome headless

```bash
chrome --headless --dump-dom file:///…              # DOM y errores de JS
chrome --headless --print-to-pdf=<ruta ABSOLUTA> …   # la ruta debe ser absoluta
```

- `--print-to-pdf` exige **ruta absoluta** en Windows.
- La extracción de texto del PDF falla (fuentes subconjuntadas): para validar la hoja de
  impresión hay que **emular `media: print` por CDP** (`Emulation.setEmulatedMedia`) y leer
  `getComputedStyle`.
- CDP también sirve para el scrollspy: `Runtime.evaluate` + `window.scrollTo` y leer la clase
  `.active` del enlace activo.
- **Los perfiles de Chrome** van en `temp/chrome-profiles/` (dentro del repo), nunca en el temp del
  sistema sin pedirlo.
- `Page.captureScreenshot` puede devolver un fotograma obsoleto: para capturas fiables, genera un
  HTML copia con un `<script>` de sondeo y usa `--screenshot` de la CLI.

### 10.3 Scripts de análisis ya escritos

`temp/kt-check/`: `navtest.js` (scrollspy), `printcheck.js` (hoja de impresión), `searchshot.js`
(captura con el buscador abierto), `structcheck.js` (balance de etiquetas y anclas rotas).
`temp/analisis/`: `inventario.js` (ficha por guía) y `patrones.js` (matriz de patrones), ambos
escriben su salida en `temp/analisis/*.txt`.

---

## 11. Reglas de operación (duras)

1. **Push solo con confirmación explícita del profesor.** Los commits están permitidos; el push
   no. «Para subir solo una solución buena».
2. **Nada fuera de la carpeta del repo** sin permiso: scripts, capturas, informes, toolchains →
   `temp/` (ya está en `.gitignore`). Si hace falta una carpeta temporal **del sistema**, se pide
   acceso en cada uso.
3. **Un commit por apartado del informe**, con prefijo `fix(scope):` / `feat(scope):`. El profesor
   revisa por partes.
4. **No toques `.claude/settings.json`** salvo que lo pida: contiene el token de autenticación en
   claro. Está gitignored (`/.claude/`), así que nunca se sube, pero tampoco se copia a otros
   sitios sin avisar.
5. **El público son los alumnos**: evita jerga interna, y comprueba que el ejemplo sea ejecutable
   por un alumno de 2º (W11, terminal, Docker Desktop).
6. **Al terminar una auditoría**, actualiza `temp/informe_*.md` con la tabla de correcciones y
   deja constancia de lo verificado.
7. **No toques `GUIA_INTERNA.md` sin motivo**: es la referencia del mapa del repo; si cambia la
   estructura, actualiza las secciones 2, 4, 5, 6 y 12.

---

## 12. Deuda técnica y oportunidades detectadas

Ordenadas por impacto. Ninguna es urgente; las tres primeras son de un minuto.

| # | Hallazgo | Dónde | Impacto |
|---|---|---|---|
| 1 | `index.html` enlaza `README.md` pero el fichero es `readme.md` | `index.html:669` | **404 en GitHub Pages** (Linux es case-sensitive). Windows lo «tapa» |
| 2 | El hero de `index.html` fija «31 guías»; el array `GUIAS` tiene 40 y `readme.md` lista 40 | `index.html:562` | Contador mentiroso (el JS lo corrige después) |
| 3 | `utilidades/` (cv-form, cv-pdf) no está enlazada desde `index.html` ni `readme.md` | — | Herramienta huérfana |
| 4 | `index.html` construye los enlaces con una URL base absoluta a GitHub Pages | `index.html` | Al abrirlo en local, cada clic salta al remoto |
| 5 | Sin red de enlaces entre guías: 0 `href` internos de guía a guía | todo el repo | La navegación depende del catálogo; nada de «continúa en la actividad 2.2» |
| 6 | Hoja de impresión ausente en la mayoría de guías (IAW: 0 de 6) | — | El alumno no puede imprimir/exportar |
| 7 | Buscador solo en 5 de 40 | — | Las guías largas (IAW ACT 3.1) no se pueden recorrer |
| 8 | Versiones de stack divergentes: `mariadb:10.11` (IAW 1.1/2.1) vs `mariadb:11` (ASETE 1.2/1.3) vs `mariadb:11.4` (ASETE 3.1); `php:8.2-fpm-alpine` vs `php:8.4-apache` | ASETE/IAW | Un alumno que copie un compose de una guía a otra choca. ASETE 3.1 lo explica (etiquetas móviles), pero el conflicto sigue ahí |
| 9 | `ASETE ACT 3.1` se rotula «4 horas» pero su plan suma 480 min y su JS dice «plan 8h» | `ASETE - ACT 3.1.html` | Expectativas rotas |
| 10 | Falta la actividad 3.2: el PUENTE dice «va antes de la actividad en la que lo harás» y esa actividad no existe | ASETE | Hueco en la secuencia hacia Laravel |
| 11 | `readme.md` describe ASETE UT0 como «Introducción a la seguridad», pero su h1 real es «Lenguajes de guiones de servidor» (la seguridad es transversal) | `readme.md` | Desalineación catálogo/contenido |
| 12 | UT2/UT3 de IAW no tienen guía y no se explica el salto | IAW | El alumno ve una numeración rota |
| 13 | `guia-que-ia-usar.html` con badge «Actualizado · Marzo 2026» y modelos concretos | raíz | Se envejece |
| 14 | `.claude/` contiene andamiaje heredado de **otro proyecto**: hooks de `backend/services/minimax_service.py`, `commands/dev-workflow.md` con npm/uvicorn, skills `music-gen`/`video-gen`/`backend-dev`/`frontend-dev` | `.claude/` | Desorienta a un agente nuevo; `dev-workflow.md` describe un repo que no es este |
| 15 | `temp/` guarda HTML a medio terminar (`guia_http.html`, `nuevaguia_http.html`) | `temp/` | Ruido (pero gitignored) |
| 16 | `CLAUDE.md` describe el estilo pero no menciona los módulos, `utilidades/`, el generador ni el flujo outline→HTML→revisión | `CLAUDE.md` | Este documento cubre esa carencia |

**Oportunidad de fondo**: unificar el estilo de las 40 guías es el mayor proyecto posible del
repo. Si el profesor lo quiere, el orden sensato es: (1) hoja de impresión y buscador en las 6 de
IAW, que son las más largas; (2) unificar las versiones de Docker en un `STACK.md` que las guías
referencien; (3) esqueleto común de actividades («Qué vas a construir → Entregables → Rúbrica»)
como en PMDM.

---

## 13. Glosario de nombres propios

| Sigla | Significado |
|---|---|
| **UT** | Unidad de Trabajo (temario oficial). `UT1`, `UT4`…: numeración del temario, no secuencia de uso |
| **ACT** | Actividad (evaluable). `ACT n.m` = número de actividad dentro de la unidad |
| **ASETE** | Arquitectura de Servidor en Entornos de Trabajo Estructurados (2º DAM/ASIR) |
| **IAW** | Implantación de Aplicaciones Web (2º ASIR) |
| **PMDM** | Programación Multimedia y Dispositivos Móviles (2º DAM) |
| **DAM / DAW / ASIR** | Desarrollo de Aplicaciones Multiplataforma / Web / Sistemas y Redes |
| **LAMP / LEMP** | Linux + Apache/MySQL + PHP / + Nginx. El repo usa **MariaDB**, nunca MySQL |
| **EBAU** | Evaluación del Bachillerato para el Acceso a la Universidad |
| **SMR** | Sistemas Microinformáticos y Redes (otro ciclo de FP) |
| **RA** | Resultado de Aprendizaje (elementos curriculares que las actividades cubren) |
| **CP / CFGS** | Certificado de Profesionalidad / Ciclo Formativo de Grado Superior |

---

*Documento interno del repo. Si cambia la estructura, actualiza las secciones 2, 4, 5, 6 y 12.*
