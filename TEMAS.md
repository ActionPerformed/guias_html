# Sistema de Temas — Guías Didácticas

Cada tema es un archivo CSS autocontenido que define todos los tokens visuales de una guía. Se inyecta en `plantilla_base.html` como `{{CSS_THEME}}`.

---

## Tokens CSS obligatorios

Todo tema **debe** definir estas variables en `:root`:

```css
:root {
  /* Fondos */
  --paper:   #xxxxxx;  /* Fondo de la página */
  --card:    #xxxxxx;  /* Fondo de tarjetas y paneles */
  --card-2:  #xxxxxx;  /* Fondo secundario (tabs, inset) */

  /* Texto */
  --ink:     #xxxxxx;  /* Texto principal */
  --muted:   #xxxxxx;  /* Texto secundario, etiquetas */

  /* Bordes */
  --line:      #xxxxxx;  /* Borde principal */
  --line-soft: #xxxxxx;  /* Borde secundario */

  /* Acentos */
  --accent:   #xxxxxx;  /* Color principal de interacción */
  --accent-2: #xxxxxx;  /* Hover/active del acento */

  /* Estados semánticos */
  --green:  #xxxxxx;  /* Éxito, hecho, correcto */
  --yellow:  #xxxxxx;  /* Aviso, atención, en progreso */
  --red:     #xxxxxx;  /* Error, peligro */

  /* Código */
  --code-bg:  #xxxxxx;  /* Fondo de bloques de código */
  --code-ink: #xxxxxx;  /* Texto en bloques de código */

  /* Syntax highlighting */
  --k: #xxxxxx;  /* Keywords  (reservadas)  */
  --s: #xxxxxx;  /* Strings   (cadenas)     */
  --v: #xxxxxx;  /* Variables ($ PHP, {{ }} ) */
  --c: #xxxxxx;  /* Comments  (comentarios)  */
  --n: #xxxxxx;  /* Numbers   (numéricos)    */
  --f: #xxxxxx;  /* Functions (nombres fn)   */
  --t: #xxxxxx;  /* Tags      (<etiquetas>)  */

  /* Layout */
  --sidebar: 262px;  /* Ancho de la barra lateral */
  --shadow:  0 8px 32px rgba(0,0,0,.5);  /* Sombra de tarjetas */
}
```

### Tokens opcionales

| Token | Uso | Recomendación |
|-------|-----|---------------|
| `--amber` | Acento secundario (banner, highlights) | Define un color cálido de soporte |
| `--blue` | Links informativos, tips | Evitar si `--accent` ya es azul |
| `prefers-reduced-motion` | Anula transiciones/animaciones | Min: `transition-duration: .001ms` |

---

## Tokens de sombras escalables (añadido)

Usa este sistema en todos los temas nuevos o actualizados:

```css
:root {
  /* ... */
  --shadow-sm: 0 2px 8px  rgba(0,0,0,.25);
  --shadow:    0 4px 16px rgba(0,0,0,.35);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.50);
}
```

> Los temas legacy (`blueprint`, `dark_modern`, `paper_cream`, `matrix`) mantienen `--shadow` como valor único por compatibilidad. Los nuevos temas deben usar el sistema `sm/md/lg`.

---

## Componentes disponibles

### Estructurales

| Clase | Descripción |
|-------|-------------|
| `.topbar` | Cabecera sticky con blur — logo, título, progreso |
| `.shell` | Contenedor grid `sidebar + main` |
| `.sidebar` | Navegación lateral sticky |
| `.main` | Área de contenido |
| `.foot` | Pie de página |

### Texto

| Clase | Descripción |
|-------|-------------|
| `.banner` | Caja de aviso con borde izquierdo coloreado |
| `.note` | Nota/advertencia en rojo |
| `.tip` | Consejo/práctica recomendada en azul |
| `.piensa` | Reflexión en amarillo/ámbar con `.ptitle` |
| `.eyebrow` | Etiqueta superior (materia, nivel, tiempo) |
| `.time-badge` | Badge monoespaciado para tiempo estimado |
| `.sec-head` | Cabecera de sección con número + título |
| `.sec-num` | Número de sección en recuadro |

### Código

| Clase | Descripción |
|-------|-------------|
| `.code` | Bloque de código con header y copiar |
| `.code-head` | Barra superior del bloque |
| `.cbtn` | Botón copiar |
| `pre.src` | El `<pre>` que contiene el código |
| `.tok-k/s/v/c/n/f/t` | Clases de syntax highlighting |
| `.inline` | Texto monoespaciado inline |

### Interactivos

| Clase | Descripción |
|-------|-------------|
| `.reto` | Reto/desafío expandable (con `data-reto`) |
| `.reto-check` | Botón de marcar reto |
| `.check` | Checklist final del tema |
| `.reveal` | Contenido oculto con botón mostrar/ocultar |
| `.reveal-btn` | Botón del reveal |
| `.reveal-box` | Caja del contenido oculto |
| `.mem-q` | Pregunta de memoria con textarea |

### Navegación

| Clase | Descripción |
|-------|-------------|
| `.nav-link` | Enlace en la sidebar |
| `.menu-toggle` | Botón hamburguesa (móvil) |
| `.active` | Estado activo de un nav-link |

### Feedback

| Clase | Descripción |
|-------|-------------|
| `.toast` | Notificación emergente inferior |
| `.toast.show` | Visible |
| `.bar` | Barra de progreso |

### Grids y tarjetas

| Clase | Descripción |
|-------|-------------|
| `.grid` | Grid responsive de tarjetas |
| `.mini` | Tarjeta compacta para ampliaciones |

---

## Highlighting de código

La plantilla base soporta estos lenguajes:

| Lang | Función | Keywords/Soporte |
|------|---------|-----------------|
| `php` | `hlPHP()` | PHP 8.x keywords, variables `$`, tags `<?php` |
| `html` | `hlHTML()` | Atributos, valores, tags |
| `sql` | `hlGeneric({keywords: SQL_KW})` | SQL keywords |
| `yaml` | `hlYAML()` | Keys, values, comentarios |
| `bash` | `hlGeneric({lineComment:"#"})` | Scripts shell |
| `text` | `hlText()` | Texto con marcadores `←` |
| `js` | `hlGeneric({...})` | JavaScript (añadido) |
| `css` | `hlGeneric({...})` | Selectores, propiedades |
| `kotlin` | `hlGeneric({...})` | Kotlin keywords |
| `python` | `hlGeneric({...})` | Python keywords |
| `json` | `hlGeneric({...})` | JSON nativo |

### Cómo añadir un nuevo highlighter

En `plantilla_base.html`, sección `/* === SYNTAX HIGHLIGHTING ===`:

```javascript
// 1. Definir keywords si aplica
var PY_KW = ["def","class","import","from","return","if","else","for","in","True","False","None"];

// 2. Añadir al switch de hl()
function hl(code, lang) {
  switch (lang) {
    // ...
    case "python": return hlGeneric(code, { keywords: PY_KW, lineComment: "#" });
    case "kotlin": return hlGeneric(code, { keywords: KOTLIN_KW, lineComment: "//" });
  }
}
```

---

## Accesibilidad

### Skip-link
Todo tema debe incluir en el `<body>` justo después de abrir:
```html
<a class="skip-link" href="#main">Saltar al contenido principal</a>
```

Y en el CSS:
```css
.skip-link {
  position: fixed; top: -100px; left: 16px; z-index: 9999;
  background: var(--accent); color: #000; padding: 8px 16px;
  font-weight: 700; text-decoration: none; border-radius: 0 0 4px 4px;
  transition: top .2s;
}
.skip-link:focus { top: 0; }
```

### prefers-reduced-motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: .001ms !important;
    animation-duration: .001ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## Cómo crear un tema nuevo

1. Copia `blueprint.css` como plantilla base
2. Cambia los 8+12+7 tokens de color en `:root`
3. Ajusta `--accent` / `--accent-2` para hover y active
4. Adapta `--code-bg` / `--code-ink` para contraste del código
5. Revisa `--shadow` (o usa `--shadow-sm/md/lg`)
6. Verifica `prefers-reduced-motion`
7. Prueba en móvil (sidebar colapsa a menu ☰)

---

## Temas existentes

| Archivo | Estética | Light/Dark |
|---------|----------|-------------|
| `blueprint.css` | Azul oscuro técnico, grid de líneas | Dark |
| `dark_modern.css` | Negro GitHub-like | Dark |
| `paper_cream.css` | Cuaderno crema, líneas horizontales | Light |
| `matrix.css` | Terminal verde `matrix` | Dark |
