Aquí tienes el código modificado con exactamente lo que pediste.

He realizado los siguientes cambios clave:

1. **Eliminé el cuadro de descripción** que dibujaba el texto largo sobre la imagen.
2. **Agregué controles de tamaño (sliders)** específicos para: el *Texto del Descuento* (listón), el *Precio Original Tachado* y el texto de *MÁS VENDIDO*.
3. **Cambié la pestaña de WhatsApp por una de TikTok**. Ahora genera un texto optimizado para la descripción de TikTok (incluyendo hashtags basados en tu producto) y lo pone en un formato fácil de copiar.

### Código Actualizado:

```python
import streamlit as st
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

def limpiar_datos():
    for k in keys_texto:
        st.session_state[k] = ""
    st.session_state.prod_cat = "General / Cualquiera"
    st.session_state.reset_uploader += 1 

# --- FUNCIONES DE UTILIDAD ---
def cargar_fuentes_estaticas():
    """Carga solo las fuentes que no cambian de tamaño"""
    try:
        font_titulo = ImageFont.truetype("arialbd.ttf", 90)   
        font_precios = ImageFont.truetype("arialbd.ttf", 130)
        return font_titulo, font_precios
    except:
        font_defecto = ImageFont.load_default()
        return font_defecto, font_defecto

def cargar_fuentes_dinamicas(size_liston, size_tachado, size_sello):
    """Carga las fuentes que el usuario puede ajustar"""
    try:
        f_liston = ImageFont.truetype("arialbd.ttf", size_liston)
        f_tachado = ImageFont.truetype("arialbd.ttf", size_tachado)
        f_sello_mas = ImageFont.truetype("arialbd.ttf", size_sello)
        f_sello_vendido = ImageFont.truetype("arialbd.ttf", max(10, size_sello - 15)) # Ligeramente más pequeño
        return f_liston, f_tachado, f_sello_mas, f_sello_vendido
    except:
        f_defecto = ImageFont.load_default()
        return f_defecto, f_defecto, f_defecto, f_defecto

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

tab1, tab2 = st.tabs(["🖼️ Creador de Imagen", "🎵 Descripción para TikTok"])

with tab1:
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.markdown("### 🎛️ Elementos de Imagen")
        imagen_subida = st.file_uploader("Sube la foto de tu producto", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.reset_uploader}")
        precio_original_txt = st.text_input("Precio Original Tachado", placeholder="Ej. 500", key="prod_orig_price")
        porcentaje_desc_txt = st.text_input("Texto del Descuento", value="¡ÚLTIMOS PARES!", key="desc_txt")
        
        st.markdown("### 🎚️ Ajuste de Tamaños (Letras)")
        # Sliders específicos para los elementos que pediste
        tamano_liston = st.slider("Tamaño: Texto del Descuento", min_value=30, max_value=150, value=90)
        tamano_tachado = st.slider("Tamaño: Precio Tachado", min_value=30, max_value=120, value=70)
        tamano_sello = st.slider("Tamaño: MÁS VENDIDO", min_value=20, max_value=100, value=45)

    with col_der:
        if imagen_subida and precio and precio_original_txt:
            
            ancho, alto = 1080, 1920 
            banner_base = Image.new("RGBA", (ancho, alto), (255, 255, 255, 255))
            draw = ImageDraw.Draw(banner_base)
            
            # Confeti de fondo
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

            # Cargar fuentes estáticas y dinámicas (controladas por sliders)
            font_titulo, font_precios = cargar_fuentes_estaticas()
            f_liston, f_tachado, f_sello_mas, f_sello_vendido = cargar_fuentes_dinamicas(tamano_liston, tamano_tachado, tamano_sello)
            
            # Título Superior Fijo
            texto_oferta = "OFERTA RELÁMPAGO"
            draw.text((ancho//2 + 4, 134), texto_oferta, fill=(210, 210, 210, 255), font=font_titulo, anchor="mm")
            draw.text((ancho//2, 130), texto_oferta, fill=(50, 50, 50), font=font_titulo, anchor="mm", stroke_width=3, stroke_fill=(200, 200, 200))

            # Renderizar Imagen del producto
            img_prod = Image.open(imagen_subida).convert("RGBA")
            w_orig, h_orig = img_prod.size
            nuevo_alto = 750 
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

            # Sello "MÁS VENDIDO" (con fuentes ajustables)
            pos_sello_x, pos_sello_y = 820, 280
            draw_scalloped_badge(draw, pos_sello_x+8, pos_sello_y+8, 150, 130, 16, (230, 230, 230, 255), (0,0,0,0), 0) 
            draw_scalloped_badge(draw, pos_sello_x, pos_sello_y, 150, 130, 16, (148, 230, 255, 255), (255, 255, 255, 255), 10)
            draw.ellipse([(pos_sello_x - 110, pos_sello_y - 110), (pos_sello_x + 110, pos_sello_y + 110)], outline=(255, 255, 255, 255), width=5)
            
            draw.text((pos_sello_x, pos_sello_y - (tamano_sello//2)), "MÁS", fill=(72, 155, 230), font=f_sello_mas, anchor="mm")
            draw.text((pos_sello_x, pos_sello_y + (tamano_sello//2) + 5), "VENDIDO", fill=(72, 155, 230), font=f_sello_vendido, anchor="mm")

            # Listón Inclinado (con fuente ajustable)
            liston = crear_liston_inclinado(950, 220, porcentaje_desc_txt, f_liston)
            liston_rotado = liston.rotate(8, expand=True) 
            pos_liston_x = (ancho - liston_rotado.width) // 2
            pos_liston_y = 1180
            banner_base.paste(liston_rotado, (pos_liston_x, pos_liston_y), liston_rotado)

            # PRECIOS
            precio_orig_y = 1580
            precio_final_y = 1750
            
            # Precio Tachado (con fuente ajustable)
            texto_original_str = f"${precio_original_txt}"
            w_tachado = draw.textlength(texto_original_str, font=f_tachado)
            draw.text((ancho//2, precio_orig_y), texto_original_str, fill=(120, 120, 120), font=f_tachado, anchor="mm")
            # Ajuste de grosor de la línea roja dependiendo del tamaño de la fuente
            grosor_linea = max(4, tamano_tachado // 10)
            draw.line([(ancho//2 - w_tachado//2 - 15, precio_orig_y), (ancho//2 + w_tachado//2 + 15, precio_orig_y)], fill=(255, 0, 0), width=grosor_linea)
            
            # Precio Oferta (Fijo y Gigante)
            texto_oferta_str = f"${precio} MXN"
            draw.text((ancho//2 + 4, precio_final_y + 4), texto_oferta_str, fill=(0, 80, 0, 120), font=font_precios, anchor="mm")
            draw.text((ancho//2, precio_final_y), texto_oferta_str, fill=(100, 230, 0), font=font_precios, anchor="mm", stroke_width=3, stroke_fill=(30, 130, 30))

            buffered = BytesIO()
            banner_base.save(buffered, format="PNG")
            
            st.image(buffered.getvalue(), caption="Diseño Listo", use_container_width=True)
            st.download_button(label="📥 Descargar Imagen", data=buffered.getvalue(), file_name=f"banner_{producto.replace(' ', '_')}.png", mime="image/png", use_container_width=True)
        else:
            st.info("👆 Sube la imagen y asegúrate de llenar Precio y Precio Original en la barra izquierda para generar el diseño.")

with tab2:
    if producto and precio and link_ml:
        st.subheader("📱 Copia esta descripción para tu video de TikTok")
        
        # Generar hashtags automáticamente basados en el nombre del producto
        hashtag_producto = f"#{producto.replace(' ', '').lower()}"
        
        texto_tiktok = f"""🔥 ¡OFERTA RELÁMPAGO! 🔥\n\n¡No dejes pasar esta oportunidad! El {producto} que buscabas.\n\n💰 Llevátelo por solo $ {precio} MXN. 😱\n\n👉 Cómpralo de forma segura aquí: \n{link_ml}\n\n#ofertas #descuentos #promocion {hashtag_producto} #comprasonline"""
        
        # st.code genera un bloque de texto que incluye automáticamente un botón de "Copiar" en la esquina superior derecha
        st.code(texto_tiktok, language="text")
        
        st.info("💡 Consejo: En TikTok, los links en la descripción a veces no son clicables. Considera poner el link también en tu perfil (Bio) o en un comentario fijado.")
    else:
        st.info("Llena el Nombre del Producto, Precio y Link en la parte superior para generar la descripción de TikTok.")
