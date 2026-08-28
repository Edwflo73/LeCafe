# Guía de Configuración: Google Analytics 4 y Search Console

## 🔧 Paso 1: Configurar Google Analytics 4 (GA4)

### Crear Property en Google Analytics:

1. Ve a [Google Analytics](https://analytics.google.com/)
2. Haz clic en **"Admin"** (parte inferior izquierda)
3. En "Propiedad", haz clic en **"Crear propiedad"**
4. Completa:
   - **Nombre de la propiedad**: "Le Café - lecafe.mx"
   - **Zona horaria de informes**: "América/México_City"
   - **Moneda**: "MXN"
5. Selecciona tu industria: **"Alimentos y Bebidas"**
6. Haz clic en **"Crear"**

### Obtener el Google Tag ID:

1. En la propiedad creada, ve a **"Flujos de datos"** (en Admin)
2. Haz clic en tu sitio web para crear un flujo
3. Ingresa:
   - **URL del sitio web**: https://lecafe.mx
   - **Nombre del flujo**: "lecafe.mx"
4. Haz clic en **"Crear flujo"**
5. **COPIA tu "Google Tag ID"** (empieza con G-)

### Agregar Google Tag al index.html:

En la etiqueta `<head>` de tu index.html, JUSTO DESPUÉS de la línea `<meta charset="UTF-8" />`, agrega:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**REEMPLAZA "G-XXXXXXXXXX" con tu Google Tag ID real**

---

## 🔍 Paso 2: Configurar Google Search Console

### Verificar el dominio:

1. Ve a [Google Search Console](https://search.google.com/search-console)
2. Haz clic en **"+ Agregación"** en la esquina superior izquierda
3. Selecciona **"Propiedad de dominio"**
4. Ingresa: `lecafe.mx` (sin https://)
5. Google te dará opciones de verificación

### Método de verificación recomendado (Registro DNS):

1. Accede a tu proveedor de hosting/dominio (GoDaddy, Namecheap, SiteGround, etc.)
2. Ve a "Configuración de DNS" o "DNS Management"
3. **Agrega un registro TXT** con el valor que Google Search Console te proporciona
4. Espera 5-30 minutos para que se propague
5. Regresa a Search Console y haz clic en **"Verificar"**

### Alternativamente (si tienes acceso al servidor):

1. En Search Console, elige **"Fichero HTML"**
2. Descarga el archivo HTML que te proporciona
3. Súbelo a la raíz de tu sitio (mismo nivel que index.html)
4. Haz clic en **"Verificar"**

---

## 📋 Paso 3: Enviar Sitemap a Search Console

1. Una vez verificado el dominio, ve a **"Sitemaps"** en el menú izquierdo
2. Haz clic en **"Agregar un nuevo sitemap"**
3. Ingresa: `https://lecafe.mx/sitemap.xml`
4. Haz clic en **"Enviar"**

---

## ⚙️ Paso 4: Configurar Parameters y Excluir URLs

En Search Console:

1. Ve a **"Configuración"** → **"Parámetros de URL"**
2. No agreges nada por ahora (no tienes parámetros problemáticos)

---

## 📊 Paso 5: Monitorear Posiciones y Tráfico

### En Google Analytics:

- Ve a **"Informes"** → **"Adquisición"** para ver de dónde viene el tráfico
- Ve a **"Informes"** → **"Participación"** para ver comportamiento de usuarios
- Ve a **"Conversiones"** para rastrear las reservas (ver paso 6)

### En Search Console:

- Ve a **"Rendimiento"** para ver:
  - **Clics**: personas que han hecho clic en tu sitio
  - **Impresiones**: veces que apareces en resultados
  - **CTR**: porcentaje de personas que hacen clic
  - **Posición promedio**: dónde apareces en promedio

---

## 🎯 Paso 6: Rastrear Conversiones (Reservas por WhatsApp)

### En Google Analytics 4:

1. Ve a **"Admin"** → **"Eventos personalizados"**
2. Haz clic en **"Crear evento"**
3. Configura un evento "form_submission":
   - Cuando se envíe el formulario de reserva, dispara este evento
   - En tu `script.js`, agrega en el submit del formulario:

```javascript
// Cuando se envía el formulario correctamente
gtag('event', 'form_submission', {
  'event_category': 'engagement',
  'event_label': 'reserva_whatsapp'
});
```

---

## 🚀 Paso 7: Verificar que Todo Funciona

1. **En Google Analytics**:
   - Ve a tu sitio en una pestaña privada/incógnito
   - Espera 5-10 minutos
   - Ve a **"Informes"** → **"Usuarios en tiempo real"**
   - Deberías verte como un usuario

2. **En Google Search Console**:
   - Ve a **"Rendimiento"**
   - En 2-3 días empezarás a ver impressiones
   - En ~2 semanas verás clics

3. **Prueba el formulario**:
   - Completa el formulario de reserva
   - Verifica que recibas el WhatsApp
   - En GA4, ve a "Conversiones" para confirmarlo

---

## 📈 Próximos Pasos para Mejorar Ranking

Al tener GA4 y Search Console configurados, podrás:

1. **Analizar keywords**: En Search Console "Rendimiento", ve qué queries te traen tráfico
2. **Optimizar CTR**: Títulos/descriptions de meta tags para keywords que no clikean
3. **Mejorar contenido**: Basado en búsquedas reales de usuarios
4. **Crear contenido local**: Blog/posts sobre "Café en Boca del Río", "Dónde trabajar en Veracruz", etc.

---

## ✅ Checklist Final

- [ ] Google Tag ID agregado al HTML
- [ ] GA4 verificado con "Usuarios en tiempo real"
- [ ] Dominio verificado en Search Console
- [ ] Sitemap enviado a Search Console
- [ ] Robots.txt accesible en lecafe.mx/robots.txt
- [ ] Schema Markup validado en [Schema.org Validator](https://validator.schema.org/)
- [ ] Meta tags (Open Graph) probados en [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)

---

## 🔗 Recursos Útiles

- [Google Analytics 4 Documentación](https://support.google.com/analytics/answer/10089681)
- [Search Console Guía de Inicio](https://support.google.com/webmasters/answer/9128668)
- [Validador de Schema Markup](https://validator.schema.org/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly)
