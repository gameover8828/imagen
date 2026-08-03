import streamlit as st
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os
import math
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Generador de Ofertas Pro",
    page_icon="🛒",
    layout="wide",
)

# --- INICIALIZAR ESTADO DE SESIÓN ---
keys_texto = ["prod_name", "prod_price", "prod_link", "prod_orig_price", "desc_txt"]
for key in keys_texto:
    if key not in st.session_state:
        st.session_state[key] = ""

if "prod_cat" not in st.session_state:
    st.session_state.prod_cat = "General / Cualquiera"
if "reset_uploader" not in st.session_state:
    st.session_state.reset_uploader = 0
if "texto_descripcion" not in st.session_state:
    st.session_state.texto_descripcion = ""

def limpiar_datos():
    for k in keys_texto:
        st.session_state[k] = ""
    st.session_state.prod_cat = "General / Cualquiera"
    st.session_state.texto_descripcion = ""
    st.session_state.reset_uploader += 1 

# --- FUNCIONES DE UTILIDAD ---
@st.cache_resource  
def cargar_fuentes(tamano_personalizado=40):
    try:
        font_principal = ImageFont.truetype("arialbd.ttf", 150)
        font_general = ImageFont.truetype("arial.ttf", 50)   
        font_precios = ImageFont.truetype("arialbd.ttf", 130)
        font_tachado = ImageFont.truetype("arialbd.ttf", 70) 
        font_titulo = ImageFont.truetype("arialbd.ttf", 90)   
        # Nueva fuente dinámica para la descripción
        font_desc = ImageFont.truetype("arialbd.ttf", tamano_personalizado)
        return font_principal, font_general, font_precios, font_tachado, font_titulo, font_desc
    except:
        font_defecto = ImageFont.load_default()
        return font_defecto, font_defecto, font_defecto, font_defecto, font_defecto, font_defecto

def draw_scalloped_badge(draw, cx, cy, r_outer, r_inner, points, fill, outline, width):
    poly = []
    for i in range(points * 2):
        angle = i * math.pi / points
        r = r_outer if i % 2 == 0 else r_inner
        poly.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(poly, fill=fill)
    poly.append(poly[0])
    if width > 0:
        draw.line(poly, fill=outline, width=width, joint="curve")

def crear_liston_inclinado(ancho, alto, texto, fuente):
    img_liston = Image.new("RGBA", (ancho, alto), (0,0,0,0))
    d = ImageDraw.Draw(img_liston)
    
    x, y, w, h = 30, 30, ancho - 60, alto - 60
    zigzags = 8
    
    # Capa Sombra
    puntos_sombra = [(x-10, y+20), (x+w+10, y-20)]
    y_step = h / zigzags
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-12, 12) if i < zigzags else 0
        puntos_sombra.append((x+w+10 + x_offset, y-20 + (i * y_step)))
    puntos_sombra.append((x-10, y+h+20))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-12, 12)
        puntos_sombra.append((x-10 + x_offset, y+20 + (i * y_step)))
    d.polygon(puntos_sombra, fill=(255, 200, 0, 255)) 

    # Capa Principal
    puntos = [(x, y), (x+w, y-40)]
    for i in range(1, zigzags + 1):
        x_offset = random.randint(-12, 12) if i < zigzags else 0
        puntos.append((x+w + x_offset, y-40 + (i * y_step)))
    puntos.append((x, y+h))
    for i in range(zigzags - 1, 0, -1):
        x_offset = random.randint(-12, 12)
        puntos.append((x + x_offset, y + (i * y_step)))
    d.polygon(puntos, fill=(255, 50, 0, 255)) 
    
    texto_mostrar = texto if texto else "¡OFERTA!"
    d.text((ancho//2, alto//2 - 10), texto_mostrar, fill=(255, 235, 0), font=fuente, anchor="mm", stroke_width=4, stroke_fill=(180, 0, 0))
    return img_liston

def create_sale_tag():
    tag = Image.new("RGBA", (220, 90), (0,0,0,0))
    d = ImageDraw.Draw(tag)
    d.polygon([(40, 10), (200, 10), (200, 80), (40, 80), (10, 45)], fill=(255, 85, 50, 255))
    d.ellipse([(20, 35), (32, 47)], fill=(255, 255, 255, 255))
    try:
        f = ImageFont.truetype("arialbd.ttf", 45)
    except:
        f = ImageFont.load_default()
    d.text((120, 45), "sale", fill=(255, 255, 255, 255), font=f, anchor="mm")
    return tag

# --- INTERFAZ PRINCIPAL ---
st.title("🛒 Generador de Ofertas Pro")

st.header("1. Datos Generales del Producto")
col1, col2, col3, col4 = st.columns([3, 2, 3, 2])
with col1:
    producto = st.text_input("Nombre del Producto", placeholder="Ej. Tenis Deportivos", key="prod_name")
with col2:
    precio = st.text_input("Precio de Oferta", placeholder="Ej. 268.68", key="prod_price")
with col3:
    link_ml = st.text_input("Link de Compra", placeholder="https://meli.la/...", key="prod_link")
with col4:
    st.write("") 
    st.button("🧹 Limpiar Todo", on_click=limpiar_datos, type="primary", use_container_width=True)

st.divider()

# Generación centralizada del texto descriptivo
mensaje_default = ""
if producto and precio and link_ml:
    mensaje_default = f"¡OFERTA RELÁMPAGO!\n\n¡No dejes pasar esta oportunidad! El {producto} que buscabas.\n\nLlevátelo por solo $ {precio} MXN.\n\nCómpralo de forma segura aquí:\n{link_ml}"

st.subheader("📝 Descripción del Producto")
mensaje_final = st.text_area("Edita el texto que aparecerá en WhatsApp y en la Imagen:", value=mensaje_default, height=150)

st.divider()

tab1, tab2 = st.tabs(["🖼️ Generador de Banner Multiredes", "💬 Enviar por WhatsApp"])

with tab1:
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.markdown("### 🎛️ Controles de Imagen")
        imagen_subida = st.file_uploader("Sube la foto de tu producto", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_uploader}")
        precio_original_txt = st.text_input("Precio Original Tachado", placeholder="Ej. 500", key="prod_orig_price")
        porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡ÚLTIMOS PARES!", key="desc_txt")
        
        st.markdown("### 🎚️ Ajustes de Texto en Imagen")
        # Barras ajustables para posicionar el texto descriptivo
        pos_x = st.slider("Posición Horizontal (X)", min_value=0, max_value=1080, value=100)
        pos_y = st.slider("Posición Vertical (Y)", min_value=0, max_value=1920, value=1350)
        tamano_fuente = st.slider("Tamaño de Letra", min_value=20, max_value=100, value=45)
        color_texto = st.color_picker("Color del texto", "#000000")
        alineacion = st.selectbox("Alineación del texto", ["left", "center", "right"], index=1)

    with col_der:
        if imagen_subida and precio and precio_original_txt:
            
            ancho, alto = 1080, 1920 
            banner_base = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
            draw = ImageDraw.Draw(banner_base)
            
            # Confeti
            colores_confeti = [(255, 70, 70), (255, 215, 0), (70, 150, 255)]
            for _ in range(120):
                x = random.randint(50, ancho-50)
                y = random.randint(50, alto-50)
                tam = random.randint(20, 35)
                color = random.choice(colores_confeti)
                angle = random.uniform(0, math.pi)
                p1 = (x, y)
                p2 = (x + tam * math.cos(angle), y + tam * math.sin(angle))
                p3 = (x + tam * math.cos(angle) - (tam/2) * math.sin(angle), y + tam * math.sin(angle) + (tam/2) * math.cos(angle))
                p4 = (x - (tam/2) * math.sin(angle), y + (tam/2) * math.cos(angle))
                draw.polygon([p1, p2, p3, p4], fill=color)

            # Fuentes (Pasamos el tamaño del slider a la función)
            fuente_script, fuente_sec, fuente_precios, fuente_tachado, font_titulo, font_desc = cargar_fuentes(tamano_fuente)
            
            # Título Superior
            texto_oferta = "OFERTA RELÁMPAGO"
            draw.text((ancho//2 + 4, 134), texto_oferta, fill=(210, 210, 210, 255), font=font_titulo, anchor="mm")
            draw.text((ancho//2, 130), texto_oferta, fill=(50, 50, 50), font=font_titulo, anchor="mm", stroke_width=3, stroke_fill=(200, 200, 200))

            # Imagen del producto
            img_prod = Image.open(imagen_subida).convert("RGBA")
            w_orig, h_orig = img_prod.size
            nuevo_alto = 650 # Reducido un poco para dar espacio al texto
            nuevo_ancho = int((nuevo_alto / h_orig) * w_orig)
            if nuevo_ancho > ancho * 0.80:
                nuevo_ancho = int(ancho * 0.80)
                nuevo_alto = int((nuevo_ancho / w_orig) * h_orig)
                
            img_prod = img_prod.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            pos_prod_x = (ancho - nuevo_ancho) // 2
            pos_prod_y = 350 
            
            sombra_prod = Image.new("RGBA", (nuevo_ancho, nuevo_alto), (0,0,0,0))
            sombra_draw = ImageDraw.Draw(sombra_prod)
            sombra_draw.ellipse([(50, nuevo_alto-60), (nuevo_ancho-50, nuevo_alto+20)], fill=(0,0,0,80))
            sombra_prod = sombra_prod.filter(ImageFilter.GaussianBlur(20))
            banner_base.paste(sombra_prod, (pos_prod_x, pos_prod_y), sombra_prod)
            banner_base.paste(img_prod, (pos_prod_x, pos_prod_y), img_prod)

            # Sello "MÁS VENDIDO"
            pos_sello_x, pos_sello_y = 820, 280
            draw_scalloped_badge(draw, pos_sello_x+8, pos_sello_y+8, 150, 130, 16, (230, 230, 230, 255), (0,0,0,0), 0) 
            draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 150, 130, 16, (148, 230, 255, 255), (255, 255, 255, 255), 10)
            draw.ellipse([(pos_sello_x - 110, pos_sello_y - 110), (pos_sello_x + 110, pos_sello_y + 110)], outline=(255, 255, 255, 255), width=5)
            try:
                font_s = ImageFont.truetype("arialbd.ttf", 45)
                font_sp = ImageFont.truetype("arialbd.ttf", 30)
            except:
                font_s, font_sp = fuente_sec, fuente_sec
            draw.text((pos_sello_x, pos_sello_y - 25), "MÁS", fill=(72, 155, 230), font=font_s, anchor="mm")
            draw.text((pos_sello_x, pos_sello_y + 25), "VENDIDO", fill=(72, 155, 230), font=font_sp, anchor="mm")

            # Listón Inclinado
            liston = crear_liston_inclinado(950, 220, porcentaje_desc_txt, font_titulo) # Ajustado tamaño
            liston_rotado = liston.rotate(8, expand=True) 
            pos_liston_x = (ancho - liston_rotado.width) // 2
            pos_liston_y = 1000
            banner_base.paste(liston_rotado, (pos_liston_x, pos_liston_y), liston_rotado)

            # Convertir HEX color a RGB para Pillow
            color_rgb = tuple(int(color_texto.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

            # DIBUJAR EL TEXTO DESCRIPTIVO (Usando los sliders)
            if mensaje_final:
                draw.multiline_text(
                    (pos_x, pos_y), 
                    mensaje_final, 
                    fill=color_rgb, 
                    font=font_desc, 
                    align=alineacion,
                    spacing=10
                )

            # PRECIOS (Ajustados al fondo)
            precio_orig_y = 1750
            precio_final_y = 1830
            
            # Precio Tachado
            texto_original_str = f"${precio_original_txt}"
            w_tachado = draw.textlength(texto_original_str, font=fuente_tachado)
            draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(120, 120, 120), font=fuente_tachado, anchor="mm")
            draw.line([(ancho//2 - w_tachado//2 - 15, precio_orig_y), (ancho//2 + w_tachado//2 + 15, precio_orig_y)], fill=(255, 0, 0), width=8)
            
            # Precio Oferta 
            texto_oferta_str = f"${precio} MXN"
            draw.text((ancho//2 + 4, precio_final_y + 4), texto_oferta_str, fill=(0, 80, 0, 120), font=fuente_precios, anchor="mm")
            draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 230, 0), font=fuente_precios, anchor="mm", stroke_width=3, stroke_fill=(30, 130, 30))

            buffered = BytesIO()
            banner_base.save(buffered, format="PNG")
            
            st.image(buffered.getvalue(), caption="Diseño Listo para Redes", use_container_width=True)
            st.download_button(label="📥 Descargar Imagen", data=buffered.getvalue(), file_name=f"banner_{producto.replace(' ', '_')}.png", mime="image/png", use_container_width=True)
        else:
            st.info("👆 Sube la imagen y asegúrate de llenar Precio y Precio Original en la barra izquierda para generar el diseño.")

with tab2:
    if mensaje_final:
        st.success("Este es el texto que se enviará por WhatsApp:")
        st.write(mensaje_final)
        st.link_button("📲 Enviar mensaje por WhatsApp", f"https://wa.me/?text={urllib.parse.quote(mensaje_final)}", type="primary")
    else:
        st.info("Llena los datos del producto para generar el mensaje.")
