// Inyecta el bloque "Sigue tu ruta" (red de enlaces entre guías) en cada HTML.
// El HTML resultante sigue siendo autocontenido: el <style> va embebido y usa
// las variables CSS que el propio fichero ya declara.
//
// Uso:  node generador/inyectar-red.js            (inyecta)
//       node generador/inyectar-red.js --check    (solo comprueba, no escribe)
//
// Es idempotente: si el fichero ya tiene el marcador <!-- red-guias -->, no se toca.

const fs = require('fs');
const path = require('path');

const RAIZ = path.resolve(__dirname, '..');
const DATA = path.join(__dirname, 'red-guias.data.json');
const MARCA = '<!-- red-guias -->';
const FIN_MARCA = '<!-- /red-guias -->';
const MARCA_ESTILO = '/* red-guias:estilo */';

const soloComprobar = process.argv.includes('--check');
const verbose = process.argv.includes('--verbose');

const ETIQUETAS = {
  continua: 'Continúa',
  anterior: 'Vuelve',
  tema: 'También te sirve',
};

// ---------------------------------------------------------------- utilidades

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// Codifica el espacio como %20, como ya hace index.html y las guías del repo.
function hrefRelativo(desde, destino) {
  const dir = path.dirname(desde).replace(/\\/g, '/');
  const prefijo = dir === '.' ? '' : '../';
  return prefijo + destino.replace(/ /g, '%20');
}

function rutaRaiz(f) {
  return f.replace(/\\/g, '/');
}

// Devuelve la ruta relativa desde la guía hasta el índice.
function hrefIndice(desde) {
  const dir = path.dirname(desde).replace(/\\/g, '/');
  return (dir === '.' ? '' : '../') + 'index.html';
}

// Comprueba que la variable existe en el :root del fichero.
function tieneVariable(html, nombre) {
  return new RegExp('(^|[{;\\s])' + nombre.replace(/[-]/g, '\\-') + '\\s*:', 'm').test(html);
}

// --------------------------------------------------------- análisis del HTML

// Marca como "opaco" todo lo que no es HTML real:
//   - el interior de <script>, <textarea>, <pre> y <style>
//   - los valores de atributo que contienen plantillas HTML (onclick="...`...`...")
function mapaOpaco(s) {
  const mapa = new Array(s.length).fill(false);
  const marcar = (desde, hasta) => {
    for (let k = desde; k < hasta && k < s.length; k++) mapa[k] = true;
  };
  for (const tag of ['script', 'textarea', 'pre', 'style']) {
    let i = 0;
    while (i < s.length) {
      const abre = s.indexOf('<' + tag, i);
      if (abre === -1) break;
      const cierra = s.indexOf('</' + tag + '>', abre);
      const fin = cierra === -1 ? s.length : cierra;
      marcar(abre, fin);
      i = fin + 1;
    }
  }
  const re = /="[^"]*[<>][^"]*"/g;
  let m;
  while ((m = re.exec(s)) !== null) marcar(m.index, m.index + m[0].length);
  return mapa;
}

// Posiciones reales (fuera de las zonas opacas) de un texto.
function reales(s, mapa, texto) {
  const res = [];
  let i = 0;
  while (true) {
    const p = s.indexOf(texto, i);
    if (p === -1) break;
    if (!mapa[p]) res.push(p);
    i = p + 1;
  }
  return res;
}

// Lista de etiquetas reales con su posición.
function etiquetas(s, mapa) {
  const res = [];
  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^>"'])*)>/g;
  let m;
  while ((m = re.exec(s)) !== null) {
    if (mapa[m.index]) continue;
    res.push({
      pos: m.index,
      fin: m.index + m[0].length,
      cierra: m[1] === '/',
      tag: m[2].toLowerCase(),
      attrs: m[3] || '',
      autoCierra: /\/>$/.test(m[0]),
    });
  }
  return res;
}

// Busca la etiqueta de apertura que encaja con un selector simple.
// Admite "body", "div.wrap", "div#id".
function buscarApertura(lista, selector) {
  const m = /^([a-zA-Z][a-zA-Z0-9-]*)?(?:[.#]([A-Za-z0-9_-]+))?$/.exec(selector.trim());
  if (!m) return null;
  const tag = m[1] ? m[1].toLowerCase() : null;
  const clase = m[2] && selector.includes('.') ? m[2] : null;
  const id = m[2] && selector.includes('#') ? m[2] : null;
  for (const t of lista) {
    if (t.cierra || t.autoCierra) continue;
    if (tag && t.tag !== tag) continue;
    if (clase && !new RegExp('class="[^"]*\\b' + clase + '\\b').test(t.attrs)) continue;
    if (id && !new RegExp('id="' + id + '"').test(t.attrs)) continue;
    return t;
  }
  return null;
}

// Devuelve la etiqueta de cierre que corresponde a la apertura indicada.
function cierreDe(lista, apertura) {
  let nivel = 0;
  for (const t of lista) {
    if (t.pos < apertura.pos) continue;
    if (t.tag !== apertura.tag) continue;
    if (t.cierra) {
      nivel--;
      if (nivel === 0) return t;
    } else if (!t.autoCierre) {
      nivel++;
    }
  }
  return null;
}

function lineaDe(s, idx) {
  return s.slice(0, idx).split('\n').length;
}

// ----------------------------------------------------- puntos de anclaje

// Retrocede el punto de inserción al inicio de su línea, si lo que precede
// en esa línea es solo espacio. Así el bloque entra en una línea nueva y la
// etiqueta original conserva su indentación.
function alInicioDeLinea(s, pos) {
  let ini = s.lastIndexOf('\n', pos - 1) + 1;
  if (ini <= 0) ini = 0;
  return /^[ \t]*$/.test(s.slice(ini, pos)) ? ini : pos;
}

// Dónde se mete el bloque <nav class="red-guias">.
//
// Reglas (en este orden), para que el bloque quede siempre dentro del
// contenido y antes del pie:
//   1. "main"   → justo antes del </main> real.
//   2. "marca"  → justo antes del </div> que cierra el contenedor marcado
//                 (<!-- /wrap -->, <!-- /content -->).
//   3. "envoltura" → justo antes del cierre de la envoltura indicada
//                 (div.wrap, body…).
//   4. "footer" → justo antes del <footer> real.
// La opción explícita por guía vive en el JSON ("anclaje").
function puntoAnclaje(s, mapa, guia) {
  const lista = etiquetas(s, mapa);
  const opcion = guia.anclaje || { tipo: 'main' };

  if (opcion.tipo === 'marca') {
    const p = s.indexOf(opcion.marca);
    if (p === -1) return null;
    const previo = s.lastIndexOf('</div>', p);
    return alInicioDeLinea(s, previo === -1 ? p : previo);
  }

  if (opcion.tipo === 'envoltura') {
    const apertura = buscarApertura(lista, opcion.selector);
    if (!apertura) return null;
    const cierre = cierreDe(lista, apertura);
    return cierre ? alInicioDeLinea(s, cierre.pos) : null;
  }

  if (opcion.tipo === 'footer') {
    const pie = reales(s, mapa, '<footer');
    return pie.length ? alInicioDeLinea(s, pie[0]) : null;
  }

  // "fin": justo antes del último </body> real (guías paginadas sin <main>).
  if (opcion.tipo === 'fin') {
    const cuerpos = reales(s, mapa, '</body>');
    return cuerpos.length ? alInicioDeLinea(s, cuerpos[cuerpos.length - 1]) : null;
  }

  // "main": si el <footer> está dentro del <main>, el bloque va antes del pie.
  const mains = reales(s, mapa, '</main>');
  const pies = reales(s, mapa, '<footer');
  if (mains.length) {
    if (pies.length && pies[0] < mains[0]) return alInicioDeLinea(s, pies[0]);
    return alInicioDeLinea(s, mains[0]);
  }
  if (pies.length) return alInicioDeLinea(s, pies[0]);
  return null;
}

// Dónde va el <style>: antes del primer </head> real.
// Si el fichero no tiene <head> (caso de ASETE - ACT 1.3), se cuela
// detrás del </style> principal, que es donde acaba la cabecera.
function puntoEstilo(s, mapa) {
  const heads = reales(s, mapa, '</head>');
  if (heads.length) return heads[0];
  const estilos = s.indexOf('</style>');
  if (estilos === -1) return null;
  return estilos + '</style>'.length;
}

// ------------------------------------------------------------------- estilos

function construirCss(css) {
  const v = (nombre) => 'var(' + nombre + ')';
  const superficie = css.surface ? v(css.surface) : 'transparent';
  const tinta = css.ink ? v(css.ink) : 'inherit';
  const apagado = css.muted ? v(css.muted) : tinta;
  const linea = css.line ? v(css.line) : 'currentColor';
  const acento = css.accent ? v(css.accent) : tinta;
  const radio = css.radius || '10px';

  // Si la guía no tiene token "apagado", se usa la tinta con algo de
  // opacidad: el texto secundario sigue leyéndose sin inventar colores.
  const opacidad = css.mutedOpacidad ? '\n  opacity:' + css.mutedOpacidad + ';' : '';

  // Algunas guías dan ancho propio al bloque (guía Linux va a nivel de body).
  const ancho = css.ancho
    ? '\n  max-width:' + css.ancho + ';\n  margin-left:auto;\n  margin-right:auto;'
    : '';

  // El marcador va DENTRO del <style>: fuera de la etiqueta se pintaría
  // como texto suelto en la página.
  return `
<style>
${MARCA_ESTILO}
/* Bloque "Sigue tu ruta": enlaces cruzados entre guías. */
.red-guias{
  /* Reset: hay guías que estilan el <nav> genérico (sticky, fijo, oculto). */
  position:static;
  top:auto;
  right:auto;
  bottom:auto;
  left:auto;
  z-index:auto;
  float:none;
  transform:none;
  display:block;
  width:auto;
  height:auto;
  max-width:none;
  min-height:0;
  max-height:none;
  overflow:visible;
  flex-direction:row;
  flex-wrap:nowrap;
  align-items:stretch;
  gap:normal;
  backdrop-filter:none;
  border-right:none;
  border-bottom:none;
  border-top:none;
  border-left:none;
  margin:2.5rem 0 0;
  padding:1.25rem 1.4rem;
  border:1px solid ${linea};
  border-radius:${radio};
  background:${superficie};
  color:${tinta};${ancho}
}
.red-guias h2{
  display:block;
  margin:0 0 .35rem;
  font-size:1.05rem;
  line-height:1.3;
  letter-spacing:.02em;
  color:${tinta};
}
.red-guias p.red-guias-lead{
  margin:0 0 .9rem;
  font-size:.95rem;
  line-height:1.55;
  color:${apagado};${opacidad}
}
.red-guias ul.red-guias-lista{
  margin:0;
  padding:0;
  list-style:none;
  display:grid;
  gap:.55rem;
}
.red-guias li{
  display:grid;
  gap:.15rem;
  max-width:none;
  padding:.65rem .8rem;
  border-left:3px solid ${acento};
}
.red-guias li > span.red-guias-tipo{
  font-size:.68rem;
  letter-spacing:.09em;
  text-transform:uppercase;
  color:${acento};
  font-weight:700;
}
.red-guias a{
  font-weight:600;
  color:${acento};
  text-decoration:none;
  padding:0;
  border-radius:0;
  background:none;
  border-bottom:1px solid transparent;
}
.red-guias a::before{
  content:none;
}
.red-guias a:hover,
.red-guias a:focus-visible{
  border-bottom-color:${acento};
  background:none;
  color:${acento};
}
.red-guias li > span.red-guias-motivo{
  font-size:.85rem;
  line-height:1.5;
  color:${apagado};${opacidad}
}
.red-guias p.red-guias-indice{
  margin:1rem 0 0;
  font-size:.9rem;
}
.red-guias p.red-guias-indice a{
  color:${apagado};
  font-weight:500;
  border-bottom:1px dotted ${linea};
}
@media print{
  .red-guias{
    display:block !important;
    position:static !important;
    background:#fff !important;
    border-color:#bbb !important;
    color:#111 !important;
  }
  .red-guias h2{color:#111 !important}
  .red-guias p.red-guias-lead,
  .red-guias li > span.red-guias-motivo,
  .red-guias p.red-guias-indice a{color:#444 !important}
  .red-guias li{background:#f6f6f6 !important;border-left-color:#888 !important}
  .red-guias li > span.red-guias-tipo,
  .red-guias a{color:#111 !important}
}
</style>
`;
}

// -------------------------------------------------------------------- bloque

function construirBloque(guia, desde, titulos) {
  const grupos = { continua: [], anterior: [], tema: [] };
  for (const e of guia.enlaces) {
    if (!grupos[e.tipo]) throw new Error('tipo desconocido: ' + e.tipo);
    grupos[e.tipo].push(e);
  }

  const lineas = [];
  for (const tipo of ['continua', 'anterior', 'tema']) {
    for (const e of grupos[tipo]) {
      const href = hrefRelativo(desde, e.destino);
      const titulo = titulos[rutaRaiz(e.destino)] || rutaRaiz(e.destino);
      lineas.push(
        '    <li>' +
          `<span class="red-guias-tipo">${esc(ETIQUETAS[tipo])}</span>` +
          `<a href="${esc(href)}">${esc(titulo)}</a>` +
          `<span class="red-guias-motivo">${esc(e.motivo)}</span>` +
        '</li>'
      );
    }
  }

  return `
${MARCA}
<nav class="red-guias" aria-labelledby="red-guias-t">
  <h2 id="red-guias-t">Sigue tu ruta</h2>
  <p class="red-guias-lead">${esc(guia.lead)}</p>
  <ul class="red-guias-lista">
${lineas.join('\n')}
  </ul>
  <p class="red-guias-indice"><a href="${esc(hrefIndice(desde))}">← Volver al catálogo de guías</a></p>
</nav>
${FIN_MARCA}
`;
}

// ------------------------------------------------------------------- main

// El repositorio trabaja con CRLF en el working tree: el bloque insertado
// debe usar los mismos finales de línea que el fichero donde se pega.
function eolDe(html) {
  const crlf = (html.match(/\r\n/g) || []).length;
  const lf = (html.match(/\n/g) || []).length - crlf;
  return crlf > lf ? '\r\n' : '\n';
}

function conEol(texto, eol) {
  return eol === '\n' ? texto : texto.replace(/\r?\n/g, '\r\n');
}

function main() {
  const data = JSON.parse(fs.readFileSync(DATA, 'utf8'));
  const titulos = data.titulos;

  const problemas = [];
  const avisos = [];
  let inyectados = 0;
  let yaHechos = 0;

  for (const guia of data.guias) {
    const ruta = path.join(RAIZ, guia.fichero);
    if (!fs.existsSync(ruta)) {
      problemas.push('FALTA el fichero: ' + guia.fichero);
      continue;
    }
    let html = fs.readFileSync(ruta, 'utf8');

    // Comprobamos que los destinos existen de verdad.
    for (const e of guia.enlaces) {
      if (!fs.existsSync(path.join(RAIZ, e.destino))) {
        problemas.push('Destino inexistente: ' + guia.fichero + ' -> ' + e.destino);
      }
      if (!titulos[rutaRaiz(e.destino)]) {
        problemas.push('Destino sin título: ' + guia.fichero + ' -> ' + e.destino);
      }
    }

    // Comprobamos que las variables CSS existen en el fichero.
    for (const [rol, nombre] of Object.entries(guia.css)) {
      if (rol === 'dark' || rol === 'radius' || rol === 'mutedOpacidad' || rol === 'ancho') continue;
      if (!nombre) continue;
      if (!tieneVariable(html, nombre)) {
        avisos.push('CSS sin resolver [' + rol + '] ' + guia.fichero + ' -> ' + nombre);
      }
    }

    if (html.includes(MARCA)) {
      yaHechos++;
      continue;
    }

    const mapa = mapaOpaco(html);
    const posAnclaje = puntoAnclaje(html, mapa, guia);
    const posEstilo = puntoEstilo(html, mapa);
    if (posAnclaje === null) {
      problemas.push('Sin punto de anclaje: ' + guia.fichero);
      continue;
    }
    if (posEstilo === null) {
      problemas.push('Sin sitio para el estilo: ' + guia.fichero);
      continue;
    }

    if (verbose) {
      console.log('  · ' + guia.fichero +
        '  bloque@L' + lineaDe(html, posAnclaje) +
        '  estilo@L' + lineaDe(html, posEstilo));
    }

    if (soloComprobar) {
      inyectados++;
      continue;
    }

    const eol = eolDe(html);
    const bloque = conEol(construirBloque(guia, guia.fichero, titulos), eol);
    const estilo = conEol(construirCss(guia.css), eol);

    // Insertamos primero el bloque (que va más abajo en el documento) y luego
    // el estilo, para no invalidar los índices ya calculados.
    html = html.slice(0, posAnclaje) + bloque + html.slice(posAnclaje);
    html = html.slice(0, posEstilo) + estilo + html.slice(posEstilo);

    fs.writeFileSync(ruta, html, 'utf8');
    inyectados++;
    console.log('  + ' + guia.fichero);
  }

  console.log('');
  console.log('Inyectadas: ' + inyectados + (soloComprobar ? ' (simulación)' : '') +
    ' | ya tenían bloque: ' + yaHechos + ' | total en el JSON: ' + data.guias.length);

  if (avisos.length) {
    console.log('\nAvisos (' + avisos.length + '):');
    for (const a of avisos) console.log('  ! ' + a);
  }
  if (problemas.length) {
    console.log('\nProblemas (' + problemas.length + '):');
    for (const p of problemas) console.log('  x ' + p);
    process.exitCode = 1;
  } else {
    console.log('\nSin destinos rotos.');
  }
}

main();
