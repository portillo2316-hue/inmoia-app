# Botón de Generación
    if st.button("🚀 Generar Todo el Contenido Comercial", type="primary"):
        if not gemini_api_key:
            st.error("⚠️ Por favor ingresa tu Clave API de Gemini en la barra lateral para continuar.")
        else:
            try:
                # Inicializar el cliente oficial de Gemini
                client = genai.Client(api_key=gemini_api_key.strip())
                
                # Construcción del prompt
                prompt = f"""
                Actúa como un experto copywriter inmobiliario y especialista en marketing digital.
                Genera contenido comercial persuasivo y profesional para el siguiente inmueble:
                - Tipo: {tipo_propiedad}
                - Ubicación: {ubicacion}
                - Precio: {precio_moneda}
                - Área: {area}
                - Distribución: {habitaciones_banos}
                - Estacionamiento: {garajes}
                - Amenidades y detalles: {detalles_adicionales}
                - Idioma de salida: {idioma_contenido}

                Estructura la respuesta clara con secciones para:
                1. Ficha Técnica / Descripción Web persuasiva.
                2. Copy para Redes Sociales (Instagram / Facebook con hashtags).
                3. Mensaje corto y vendedor para WhatsApp.
                4. Guion atractivo para un Reel o TikTok de 30 segundos.
                """

                with st.spinner("Generando contenido inmobiliario con inteligencia artificial..."):
                    # Usamos directamente el modelo actual y compatible
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt,
                    )
                    resultado_ia = response.text

                # Mostrar resultado
                st.success("¡Contenido generado con éxito!")
                st.markdown("---")
                st.markdown(resultado_ia)
                
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
                st.info("Verifica que tu clave API de Gemini sea correcta e intenta de nuevo.")
