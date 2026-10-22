"""
Importaciones · lotes, costos landed y catálogo
Streamlit + SQLite + Pandas · estilo minimalista claro/oscuro · responsivo (móvil)
"""

import os
import re
import sqlite3
from datetime import date, timedelta
from html import escape

import pandas as pd
import streamlit as 
# CSS Ultra-Limpio: Elimina totalmente la marca de agua, cabeceras y footers de Streamlit
hide_streamlit_style = """
    <style>
    /* Ocultar barra superior, menú de hamburguesa y botón Deploy */
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    
    /* Eliminar el margen/espacio blanco superior que deja la barra al ocultarse */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Ocultar marca de agua en el pie de página */
    #stDecoration {display: none !important;}
    footer:after {content: "";}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
DB_PATH = os.getenv("DB_PATH", "data/inventario.db")
ESTADOS = ["En Origen", "En Tránsito", "Listo", "Entregado"]
EN_CAMINO = ["En Origen", "En Tránsito"]
DISPONIBLE = ["Listo", "Entregado"]
TIPOS = ["Marítimo", "Aéreo"]
ICONOS = ["📦", "👟", "👕", "🎧", "📱", "⌚", "🎒", "🧴", "🪑", "🔧", "🧸", "💡"]
EXTRAS = ["Empaque reforzado", "Reembalaje", "Consolidación", "Flete interno (origen)", "Seguro (opcional)"]
MODOS_CBM = ["Por medidas (cm)", "CBM directo por unidad", "CBM por caja"]
TAGS = {"En Origen": "#e8a317", "En Tránsito": "#2f8fef", "Listo": "#9b6bff",
        "Entregado": "#22b573", "Marítimo": "#16a6a0", "Aéreo": "#e0507d"}

st.set_page_config(page_title="Importaciones", page_icon="🚢", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------------------------------------------------------
# TEMAS Y ESTILO MINIMALISTA (variables por modo + CSS común)
# ---------------------------------------------------------------------------
THEMES = {
    "dark": dict(bg="#0e1014", s1="#15181e", s2="#1b1f27", tx="#eceef2", mu="#8b93a1", ac="#3ddcc4", ac2="#2bb8a2",
                 on="#04201b", hi="transparent", lo="#252a35", sd="rgba(0,0,0,.35)", sl="transparent",
                 gd="#232833", gl="transparent", cs="dark"),
    "light": dict(bg="#f5f6f8", s1="#ffffff", s2="#eef0f4", tx="#12161f", mu="#667085", ac="#0f9d8a", ac2="#0b7f70",
                  on="#ffffff", hi="transparent", lo="#e3e6eb", sd="rgba(16,24,40,.06)", sl="transparent",
                  gd="#e8ebf0", gl="transparent", cs="light"),
}

BASE_CSS = """
html,body,.stApp,[data-testid="stAppViewContainer"]{font-family:Inter,system-ui,sans-serif;font-variant-numeric:tabular-nums}
.stApp{background:var(--bg)!important}
.stApp,.stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp span,.stApp [data-testid="stMarkdownContainer"]{color:var(--tx)}
.stApp [data-testid="stCaptionContainer"],.stApp small{color:var(--mu)!important}
/* Ocultar barra lateral, header, footer y menú nativo de Streamlit */
[data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"],[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
#MainMenu{visibility:hidden}footer{visibility:hidden}header{visibility:hidden}
/* Aprovechar todo el ancho */
.block-container{padding-top:1.5rem!important;padding-bottom:2rem!important;max-width:95%!important}
.hero h1{font-size:28px;font-weight:700;letter-spacing:-.03em;margin:0;padding:0}
.hero p{color:var(--mu)!important;margin:4px 0 0;font-size:14px}
h5{font-weight:600;letter-spacing:-.01em}
/* Pestañas: subrayado simple */
[data-baseweb="tab-list"]{gap:6px;overflow-x:auto}
button[data-baseweb="tab"]{min-height:46px;padding:0 14px;color:var(--mu);white-space:nowrap;background:transparent}
button[data-baseweb="tab"][aria-selected="true"] p{color:var(--tx)!important;font-weight:600}
[data-baseweb="tab-highlight"]{background:var(--ac)!important;height:2px}
[data-baseweb="tab-border"]{background:var(--lo)!important}
/* Campos */
div[data-baseweb="input"],div[data-baseweb="base-input"],div[data-baseweb="select"]>div,textarea{background:var(--s1)!important;border:1px solid var(--lo)!important;border-radius:10px!important;min-height:44px}
div[data-baseweb="input"]:focus-within,div[data-baseweb="select"]>div:focus-within{border-color:var(--ac)!important}
input,textarea{color:var(--tx)!important;-webkit-text-fill-color:var(--tx)!important;font-size:16px!important}
[data-testid="stNumberInput"] button{background:var(--s2)!important;color:var(--tx)!important;min-width:42px}
span[data-baseweb="tag"]{background:var(--ac)!important}span[data-baseweb="tag"] *{color:var(--on)!important}
div[data-baseweb="popover"] ul,div[data-baseweb="popover"]>div,div[data-baseweb="calendar"]{background:var(--s1)!important;color:var(--tx)!important}
li[role="option"],div[data-baseweb="calendar"] *{color:var(--tx)!important}li[role="option"]:hover{background:var(--s2)!important}
[data-testid="stAlert"]{background:var(--s2);border:1px solid var(--lo);border-radius:12px}
/* Botones */
.stButton>button{min-height:46px;border-radius:10px;border:1px solid var(--lo);font-weight:600;color:var(--tx);background:var(--s1);transition:border-color .15s,transform .05s}
.stButton>button p{color:inherit!important}
.stButton>button:hover{border-color:var(--ac);color:var(--ac)}
.stButton>button:active{transform:scale(.98)}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{background:var(--ac);border-color:var(--ac);color:var(--on)}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{color:var(--on);filter:brightness(1.06)}
[data-testid="stExpander"]{background:var(--s1);border:1px solid var(--lo)!important;border-radius:14px;box-shadow:0 1px 2px var(--sd)}
[data-testid="stExpander"] summary{min-height:50px}[data-testid="stExpander"] summary p{font-weight:600}
/* Tarjetas bento */
.bento{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:16px;margin:14px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:12px 0}
.card,.kpi{background:var(--s1);border:1px solid var(--lo);border-radius:16px;box-shadow:0 1px 2px var(--sd)}
.card{padding:18px}.kpi{padding:14px 16px}
.kpi small{display:block;font-size:12px;color:var(--mu)}.kpi b{display:block;font-size:clamp(18px,4.6vw,24px);font-weight:700;letter-spacing:-.02em;margin-top:2px}
.kpi i{display:block;font-style:normal;font-size:11px;color:var(--mu);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.between{justify-content:space-between;margin-top:10px}.grow{flex:1;min-width:120px}
.ico{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;font-size:22px;background:var(--s2)}
.ttl{font-weight:600;font-size:15px;overflow:hidden;text-overflow:ellipsis}.sub{color:var(--mu);font-size:12px}
.tag{font-size:11px;font-weight:600;padding:3px 10px;border-radius:999px;border:1px solid;white-space:nowrap}
.bar{height:6px;background:var(--s2);border-radius:9px;margin-top:16px;overflow:hidden}
.bar span{display:block;height:100%;border-radius:9px;background:var(--ac)}
.eta{font-weight:600;font-size:14px}.late{color:#e5484d!important}.ok{color:#22b573!important}
.kv{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px;padding-top:14px;border-top:1px solid var(--gd)}
.kv small{display:block;color:var(--mu);font-size:11px;margin-bottom:2px}.kv b{font-size:13px;font-weight:600}.price{color:var(--ac)!important;font-size:15px!important}
/* Tablas con scroll horizontal táctil */
.tbl{overflow-x:auto;-webkit-overflow-scrolling:touch;border-radius:14px;border:1px solid var(--lo);margin:10px 0;background:var(--s1)}
.tbl table{border-collapse:collapse;width:100%;min-width:560px;font-size:13px}
.tbl th{text-align:left;padding:11px 14px;color:var(--mu);font-weight:600;background:var(--s2)}
.tbl td{padding:11px 14px;white-space:nowrap;border-top:1px solid var(--gd)}
@media(max-width:640px){
 .block-container{padding:1rem .75rem 4rem!important;max-width:100%!important}.hero h1{font-size:24px}
 .card{padding:14px}.kv{grid-template-columns:repeat(2,1fr)}.bento{gap:12px}
 .stButton>button{width:100%}
}
"""


def css(mode: str) -> str:
    t = THEMES[mode]
    root = ";".join(f"--{k}:{v}" for k, v in t.items() if k != "cs") + f";color-scheme:{t['cs']}"
    return ("<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');"
            f":root{{{root}}}{BASE_CSS}</style>")


# ---------------------------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------------------------
def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with get_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL UNIQUE, nombre TEXT NOT NULL,
            icono TEXT NOT NULL DEFAULT '📦', largo_cm REAL, ancho_cm REAL, alto_cm REAL,
            peso_kg REAL NOT NULL DEFAULT 0, cbm_unitario REAL NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, producto_id INTEGER NOT NULL, fecha_compra TEXT NOT NULL,
            courier TEXT NOT NULL, tipo_envio TEXT NOT NULL, eta TEXT NOT NULL, unidades INTEGER NOT NULL,
            fob_total REAL NOT NULL, envio REAL NOT NULL, extras REAL NOT NULL,
            estado TEXT NOT NULL DEFAULT 'En Origen', cbm_real REAL NOT NULL DEFAULT 0)""")
        c.execute("CREATE TABLE IF NOT EXISTS couriers (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS ajustes (clave TEXT PRIMARY KEY, valor TEXT)")
        # Migración: bases creadas con la versión anterior no tenían cbm_real
        if "cbm_real" not in [r[1] for r in c.execute("PRAGMA table_info(lotes)")]:
            c.execute("ALTER TABLE lotes ADD COLUMN cbm_real REAL NOT NULL DEFAULT 0")


def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_conn() as c:
        return pd.read_sql_query(sql, c, params=params)


def ex(sql: str, params: tuple = ()) -> None:
    with get_conn() as c:
        c.execute(sql, params)


def get_setting(k: str, default: str) -> str:
    df = q("SELECT valor FROM ajustes WHERE clave=?", (k,))
    return df["valor"][0] if len(df) else default


def set_setting(k: str, v) -> None:
    ex("INSERT INTO ajustes (clave, valor) VALUES (?,?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor", (k, str(v)))


def couriers() -> list:
    return q("SELECT nombre FROM couriers ORDER BY nombre")["nombre"].tolist()


def lotes_df() -> pd.DataFrame:
    df = q("""SELECT l.*, c.nombre, c.sku, c.icono, c.cbm_unitario, c.peso_kg
              FROM lotes l JOIN catalogo c ON c.id = l.producto_id ORDER BY l.eta""")
    df["total"] = df["fob_total"] + df["envio"] + df["extras"]           # Costo total del lote
    df["landed"] = df["total"] / df["unidades"]                           # Landed unitario
    df["cbm_total"] = df["cbm_real"].where(df["cbm_real"] > 0, df["cbm_unitario"] * df["unidades"])
    df["dias"] = df["eta"].apply(lambda e: (date.fromisoformat(e) - date.today()).days)
    return df


def gen_sku(nombre: str) -> str:
    pref = re.sub(r"[^A-Z]", "", nombre.upper())[:3].ljust(3, "X")
    n = int(q("SELECT COALESCE(MAX(id), 0) + 1 AS n FROM catalogo")["n"][0])
    return f"{pref}-{n:04d}"


def flash(msg: str) -> None:
    st.session_state["flash"] = msg
    st.rerun()


# ---------------------------------------------------------------------------
# COMPONENTES HTML
# ---------------------------------------------------------------------------
def tag(txt: str) -> str:
    c = TAGS.get(txt, "#8991a3")
    return f'<span class="tag" style="color:{c};background:{c}22;border-color:{c}66">{escape(txt)}</span>'


def kpis(items) -> str:
    """items: (etiqueta, valor[, nota])"""
    return '<div class="kpis">' + "".join(
        f'<div class="kpi"><small>{a}</small><b>{b}</b>{f"<i>{escape(c[0])}</i>" if len(c) else ""}</div>'
        for a, b, *c in items) + "</div>"


def tabla(headers, rows) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def kv_grid(pairs) -> str:
    return '<div class="kv">' + "".join(f"<div><small>{k}</small><b>{v}</b></div>" for k, v in pairs) + "</div>"


def card_lote(r) -> str:
    f_compra, f_eta = date.fromisoformat(r.fecha_compra), date.fromisoformat(r.eta)
    if r.estado == "Entregado":
        eta_txt, cls, pct = "Recibido", "ok", 100
    else:
        eta_txt, cls = ((f"{abs(r.dias)} días de retraso", "late") if r.dias < 0 else
                        ("Llega hoy", "") if r.dias == 0 else (f"Faltan {r.dias} días", ""))
        pct = min(max((date.today() - f_compra).days / max((f_eta - f_compra).days, 1) * 100, 0), 100)
    grid = kv_grid([("Courier", escape(r.courier)), ("Unidades", f"{r.unidades:,}"), ("CBM total", f"{r.cbm_total:.3f} m³"),
                    ("Costo del lote", f"${r.total:,.2f}"), ("Landed unitario", f"${r.landed:,.2f}"), ("FOB", f"${r.fob_total:,.2f}")])
    return (f'<div class="card"><div class="row"><div class="ico">{r.icono}</div>'
            f'<div class="grow"><div class="ttl">{escape(r.nombre)}</div><div class="sub">{r.sku} · Lote #{r.id}</div></div>'
            f'{tag(r.tipo_envio)}{tag(r.estado)}</div><div class="bar"><span style="width:{pct:.0f}%"></span></div>'
            f'<div class="row between"><span class="eta {cls}">{eta_txt}</span>'
            f'<span class="sub">Compra {f_compra:%d/%m} → ETA {f_eta:%d/%m/%Y}</span></div>{grid}</div>')


def card_producto(r, s: dict, margen: float) -> str:
    landed = s.get("landed")
    grid = kv_grid([("CBM unitario", f"{r.cbm_unitario:.5f}"),
                    ("Costo real puesto en mano", f"${landed:,.2f}" if landed else "Sin lotes"),
                    ("Precio sugerido", f'<span class="price">{f"${landed * (1 + margen / 100):,.2f}" if landed else "—"}</span>')])
    return (f'<div class="card"><div class="row"><div class="ico">{r.icono}</div>'
            f'<div class="grow"><div class="ttl">{escape(r.nombre)}</div><div class="sub">{r.sku} · {r.peso_kg:g} kg</div></div></div>'
            f'{grid}<div class="row between"><span class="sub">🚢 {s.get("camino", 0)} en camino</span>'
            f'<span class="sub">📍 {s.get("stock", 0)} disponibles</span></div></div>')


# ---------------------------------------------------------------------------
# PESTAÑA 1: CARGAS ACTIVAS
# ---------------------------------------------------------------------------
def tab_cargas() -> None:
    df = lotes_df()
    if df.empty:
        st.info("Todavía no hay cargas. Crea la primera en «Nuevo lote».")
        return
    activas, camino = df[df["estado"] != "Entregado"], df[df["estado"].isin(EN_CAMINO)]
    prox = ("—",)
    if len(camino):
        n = camino.sort_values("dias").iloc[0]
        prox = (f"{n['dias']} días" if n["dias"] >= 0 else "Retrasada", n["nombre"])
    st.markdown(kpis([("Cargas activas", len(activas)), ("Unidades en camino", f"{int(camino['unidades'].sum()):,}"),
                      ("Capital en curso", f"${activas['total'].sum():,.0f}"), ("Próxima llegada", *prox)]), unsafe_allow_html=True)

    sel = st.multiselect("Mostrar", ESTADOS, default=ESTADOS[:3])
    shown = df[df["estado"].isin(sel)]
    if shown.empty:
        st.caption("No hay cargas con esos estados.")
    else:
        st.markdown('<div class="bento">' + "".join(card_lote(r) for r in shown.itertuples()) + "</div>", unsafe_allow_html=True)

    with st.expander("Vista de tabla"):
        st.markdown(tabla(["Lote", "Producto", "Courier", "Envío", "Estado", "ETA", "Unid.", "CBM", "Total", "Landed"],
                          [[f"#{r.id}", escape(r.nombre), escape(r.courier), tag(r.tipo_envio), tag(r.estado), r.eta, r.unidades,
                            f"{r.cbm_total:.3f}", f"${r.total:,.2f}", f"${r.landed:,.2f}"] for r in df.itertuples()]),
                    unsafe_allow_html=True)

    with st.expander("Actualizar estado, ETA o eliminar una carga"):
        rows = {int(r.id): r for r in df.itertuples()}
        lid = st.selectbox("Carga", list(rows), format_func=lambda i: f"#{i} · {rows[i].nombre} · {rows[i].estado}")
        r = rows[lid]
        c1, c2 = st.columns(2)
        estado = c1.selectbox("Estado", ESTADOS, index=ESTADOS.index(r.estado), key=f"ue{lid}")
        eta = c2.date_input("ETA", value=date.fromisoformat(r.eta), key=f"ud{lid}")
        b1, b2 = st.columns(2)
        if b1.button("Guardar cambios", type="primary", key=f"us{lid}"):
            ex("UPDATE lotes SET estado=?, eta=? WHERE id=?", (estado, eta.isoformat(), lid))
            flash(f"Lote #{lid} actualizado")
        if b2.button("Eliminar carga", key=f"ux{lid}"):
            ex("DELETE FROM lotes WHERE id=?", (lid,))
            flash(f"Lote #{lid} eliminado")


# ---------------------------------------------------------------------------
# PESTAÑA 2: NUEVO LOTE
# ---------------------------------------------------------------------------
def tab_nuevo_lote() -> None:
    cat, lista = q("SELECT * FROM catalogo ORDER BY nombre"), couriers()
    if cat.empty:
        st.info("Primero registra un producto en «Catálogo».")
        return
    if not lista:
        st.info("Aún no tienes couriers. Agrégalos en «Ajustes».")
        return
    prods = {int(r.id): r for r in cat.itertuples()}
    v = st.session_state.setdefault("vl", 0)

    st.markdown("##### Compra y envío")
    a, b = st.columns([3, 1])
    pid = a.selectbox("Producto", list(prods), format_func=lambda i: f"{prods[i].icono} {prods[i].sku} · {prods[i].nombre}", key=f"lp{v}")
    unidades = b.number_input("Unidades", min_value=1, step=1, key=f"lu{v}")
    c, d = st.columns(2)
    f_compra = c.date_input("Fecha de compra / pago", value=date.today(), key=f"lf{v}")
    courier = d.selectbox("Courier / consolidador", lista, key=f"lc{v}")
    e, f = st.columns(2)
    tipo = e.radio("Tipo de envío", TIPOS, horizontal=True, key=f"lt{v}")
    eta = f.date_input("ETA (llegada estimada)", value=date.today() + timedelta(days=45 if tipo == "Marítimo" else 10), key=f"le{v}")

    p = prods[pid]
    peso_total = p.peso_kg * unidades
    cbm_cat = p.cbm_unitario * unidades
    st.markdown("##### Carga y costos")
    g, h = st.columns(2)
    cbm_real = g.number_input("CBM total medido por el courier (opcional)", min_value=0.0, step=0.01, format="%.4f", key=f"lcr{v}",
                              help=f"Si lo dejas en 0 se usa el del catálogo: {cbm_cat:.4f} m³")
    fob = h.number_input("Compra FOB del lote ($)", min_value=0.0, step=10.0, key=f"lb{v}")
    cbm_total = cbm_real if cbm_real > 0 else cbm_cat
    base = st.radio("Cómo cobra el courier", ["Por CBM", "Por kg", "Monto fijo"], horizontal=True, key=f"lbase{v}")
    tarifa = st.number_input(f"Tarifa acordada ({ {'Por CBM': '$ por m³', 'Por kg': '$ por kg', 'Monto fijo': '$ total'}[base] })",
                             min_value=0.0, step=1.0, key=f"lr{v}")
    envio = tarifa * cbm_total if base == "Por CBM" else tarifa * peso_total if base == "Por kg" else tarifa

    st.caption("Gastos extras")
    cols = st.columns(3)
    extras = sum(cols[i % 3].number_input(n, min_value=0.0, step=1.0, key=f"lx{i}{v}") for i, n in enumerate(EXTRAS))

    total, margen = fob + envio + extras, st.session_state["margen"]
    landed = total / unidades
    st.markdown(kpis([("Costo total del lote", f"${total:,.2f}"), ("Landed unitario", f"${landed:,.2f}"),
                      ("Precio sugerido", f"${landed * (1 + margen / 100):,.2f}", f"Margen {margen}%"),
                      ("Envío", f"${envio:,.2f}"), ("CBM total", f"{cbm_total:.3f} m³"), ("Peso total", f"{peso_total:,.1f} kg")]),
                unsafe_allow_html=True)

    if st.button("Registrar lote", type="primary", key=f"lsave{v}"):
        if eta < f_compra:
            st.error("La ETA no puede ser anterior a la fecha de compra.")
        else:
            ex("""INSERT INTO lotes (producto_id, fecha_compra, courier, tipo_envio, eta, unidades, fob_total, envio, extras, estado, cbm_real)
                  VALUES (?,?,?,?,?,?,?,?,?, 'En Origen', ?)""",
               (pid, f_compra.isoformat(), courier, tipo, eta.isoformat(), int(unidades), fob, envio, extras, cbm_real))
            st.session_state["vl"] += 1
            flash("Lote registrado")


# ---------------------------------------------------------------------------
# PESTAÑA 3: CATÁLOGO
# ---------------------------------------------------------------------------
def tab_catalogo() -> None:
    cat, margen = q("SELECT * FROM catalogo ORDER BY id DESC"), st.session_state["margen"]

    with st.expander("Nuevo producto", expanded=cat.empty):
        v = st.session_state.setdefault("vp", 0)
        c1, c2 = st.columns([4, 1])
        nombre = c1.text_input("Nombre del producto", key=f"pn{v}")
        icono = c2.selectbox("Icono", ICONOS, key=f"pi{v}")
        peso = st.number_input("Peso unitario (kg)", min_value=0.0, step=0.1, key=f"pw{v}")
        modo = st.radio("¿Cómo ingresas el CBM?", MODOS_CBM, horizontal=True, key=f"pm{v}")
        largo = ancho = alto = None
        if modo == MODOS_CBM[0]:
            d = st.columns(3)
            largo = d[0].number_input("Largo (cm)", min_value=0.0, step=1.0, key=f"pl{v}")
            ancho = d[1].number_input("Ancho (cm)", min_value=0.0, step=1.0, key=f"pa{v}")
            alto = d[2].number_input("Alto (cm)", min_value=0.0, step=1.0, key=f"ph{v}")
            cbm = largo * ancho * alto / 1_000_000
        elif modo == MODOS_CBM[1]:
            cbm = st.number_input("CBM por unidad (m³)", min_value=0.0, step=0.001, format="%.6f", key=f"pc{v}")
        else:
            d = st.columns(2)
            cbm_caja = d[0].number_input("CBM de la caja (m³)", min_value=0.0, step=0.01, format="%.6f", key=f"pcc{v}")
            por_caja = d[1].number_input("Unidades por caja", min_value=1, step=1, key=f"ppc{v}")
            cbm = cbm_caja / por_caja
        sku = gen_sku(nombre) if nombre.strip() else "—"
        st.markdown(kpis([("SKU automático", sku), ("CBM unitario (m³)", f"{cbm:.6f}")]), unsafe_allow_html=True)
        if st.button("Guardar producto", type="primary", key=f"pb{v}"):
            if not nombre.strip():
                st.error("Escribe el nombre del producto.")
            elif cbm <= 0:
                st.error("El CBM debe ser mayor a 0: ingresa las medidas o el CBM.")
            else:
                try:
                    ex("INSERT INTO catalogo (sku, nombre, icono, largo_cm, ancho_cm, alto_cm, peso_kg, cbm_unitario) VALUES (?,?,?,?,?,?,?,?)",
                       (sku, nombre.strip(), icono, largo, ancho, alto, peso, cbm))
                except sqlite3.IntegrityError:
                    st.error("Ese SKU ya existe. Vuelve a intentarlo.")
                else:
                    st.session_state["vp"] += 1
                    flash(f"Producto {sku} guardado")

    if cat.empty:
        st.info("Tu catálogo está vacío. Registra el primer producto arriba.")
        return

    # Costo landed real = promedio ponderado de todos los lotes del producto
    stats = {int(pid): {"landed": g["total"].sum() / g["unidades"].sum(),
                        "camino": int(g[g["estado"].isin(EN_CAMINO)]["unidades"].sum()),
                        "stock": int(g[g["estado"].isin(DISPONIBLE)]["unidades"].sum())}
             for pid, g in lotes_df().groupby("producto_id")}

    buscar = st.text_input("Buscar por nombre o SKU", key="buscar")
    vista = cat[cat["nombre"].str.contains(buscar, case=False) | cat["sku"].str.contains(buscar, case=False)] if buscar else cat
    st.markdown('<div class="bento">' + "".join(card_producto(r, stats.get(int(r.id), {}), margen) for r in vista.itertuples()) + "</div>",
                unsafe_allow_html=True)

    with st.expander("Vista de tabla"):
        rows = []
        for r in vista.itertuples():
            s = stats.get(int(r.id), {})
            ld = s.get("landed")
            rows.append([r.sku, f"{r.icono} {escape(r.nombre)}", f"{r.cbm_unitario:.5f}", f"{r.peso_kg:g}",
                         f"${ld:,.2f}" if ld else "—", f"${ld * (1 + margen / 100):,.2f}" if ld else "—",
                         s.get("camino", 0), s.get("stock", 0)])
        st.markdown(tabla(["SKU", "Producto", "CBM unit.", "Kg", "Landed", "Sugerido", "En camino", "Disponibles"], rows), unsafe_allow_html=True)

    with st.expander("Editar CBM o eliminar productos"):
        prods = {int(r.id): r for r in cat.itertuples()}
        pid = st.selectbox("Producto", list(prods), format_func=lambda i: f"{prods[i].sku} · {prods[i].nombre}", key="ed_p")
        nuevo = st.number_input("CBM unitario (m³)", min_value=0.0, value=float(prods[pid].cbm_unitario), step=0.001,
                                format="%.6f", key=f"ecbm{pid}")
        b1, b2 = st.columns(2)
        if b1.button("Guardar CBM", type="primary", key=f"ecs{pid}"):
            if nuevo <= 0:
                st.error("El CBM debe ser mayor a 0.")
            else:
                ex("UPDATE catalogo SET cbm_unitario=? WHERE id=?", (nuevo, pid))
                flash("CBM actualizado")
        if b2.button("Eliminar producto", key=f"edel{pid}"):
            if pid in stats:
                st.error("No se puede eliminar: tiene lotes registrados.")
            else:
                ex("DELETE FROM catalogo WHERE id=?", (pid,))
                flash("Producto eliminado")


# ---------------------------------------------------------------------------
# PESTAÑA 4: AJUSTES (couriers y margen)
# ---------------------------------------------------------------------------
def tab_ajustes() -> None:
    st.markdown("##### Margen de ganancia")
    st.slider("Margen sobre el costo landed (%)", min_value=0, max_value=300, step=5, key="margen",
              on_change=lambda: set_setting("margen", st.session_state["margen"]))

    st.markdown("##### Mis couriers")
    lista, v = couriers(), st.session_state.setdefault("vc", 0)
    nuevo = st.text_input("Nombre del courier o consolidador", key=f"cn{v}")
    if st.button("Agregar courier", type="primary"):
        if not nuevo.strip():
            st.error("Escribe el nombre del courier.")
        else:
            try:
                ex("INSERT INTO couriers (nombre) VALUES (?)", (nuevo.strip(),))
            except sqlite3.IntegrityError:
                st.error("Ese courier ya existe.")
            else:
                st.session_state["vc"] += 1
                flash(f"Courier «{nuevo.strip()}» agregado")
    if lista:
        st.markdown('<div class="row" style="margin:10px 0">' + "".join(
            f'<span class="tag" style="color:var(--ac);border-color:var(--ac)">{escape(n)}</span>' for n in lista) + "</div>",
            unsafe_allow_html=True)
        quitar = st.multiselect("Quitar couriers", lista, key=f"cq{v}")
        if quitar and st.button("Quitar seleccionados"):
            with get_conn() as c:
                c.executemany("DELETE FROM couriers WHERE nombre=?", [(n,) for n in quitar])
            st.session_state["vc"] += 1
            flash("Courier(s) eliminado(s). Los lotes existentes conservan su nombre.")
    else:
        st.caption("Aún no has agregado couriers.")


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA
# ---------------------------------------------------------------------------
def main() -> None:
    init_db()
    st.session_state.setdefault("dark", get_setting("dark", "1") == "1")
    st.session_state.setdefault("margen", int(float(get_setting("margen", "40"))))
    st.markdown(css("dark" if st.session_state["dark"] else "light"), unsafe_allow_html=True)

    h1, h2 = st.columns([4, 1])
    h1.markdown('<div class="hero"><h1>Importaciones</h1>'
                '<p>Qué viene en camino, cuánto cuesta realmente y a qué precio venderlo.</p></div>', unsafe_allow_html=True)
    h2.toggle("🌙 Modo oscuro", key="dark", on_change=lambda: set_setting("dark", int(st.session_state["dark"])))

    if "flash" in st.session_state:
        st.toast(st.session_state.pop("flash"), icon="✅")

    t1, t2, t3, t4 = st.tabs(["Cargas", "Nuevo lote", "Catálogo", "Ajustes"])
    with t1:
        tab_cargas()
    with t2:
        tab_nuevo_lote()
    with t3:
        tab_catalogo()
    with t4:
        tab_ajustes()


main()
