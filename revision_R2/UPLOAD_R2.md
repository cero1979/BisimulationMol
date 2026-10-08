# JBCB-1505 R2: instrucciones de carga

## Archivos recomendados para la plataforma

1. **Manuscript:** JBCB-1505-R2-manuscript-only.zip.
   Contiene un solo archivo principal (main_jbcb_R2.tex), ws-jbcb.cls y
   R2_Fig1.pdf a R2_Fig4.pdf, todos en la raiz.
2. **Supplemental Material:** revision_R2/Supplementary_Validation_R2.pdf.
3. **Reply to Referee's Comments:** revision_R2/response_to_reviewer_R2.pdf.

La version actual del articulo tiene 22 paginas y una nueva Tabla 4 en la
seccion 7 con cinco comprobaciones, sus procedimientos y resultados. Reemplaza
el ZIP del manuscrito por el actualizado. Reemplaza tambien el PDF de respuesta
(7 paginas): sus puntos R2.2 y R2.9 reflejan la nueva tabla y numeracion.
La respuesta sigue siendo autocontenida, sin remitir a documentos locales.
El suplemento no cambio de contenido. No es necesario adjuntar informes .md.

El ZIP completo JBCB-1505-R2.zip conserva fuentes de articulo y suplemento.
No lo cargues junto con el ZIP manuscript-only: duplicaria archivos.
Usa el completo solo si la plataforma permite identificar y clasificar por
separado los dos archivos maestros. El ZIP JBCB-1505-R2-supplement.zip permite
entregar las fuentes suplementarias si las solicita la revista.

## Evitar los errores anteriores

- Desmarca los archivos R1 que no deban trasladarse a la nueva revision.
- Retira las versiones actuales reemplazadas antes de cargar R2. Conserva una
  copia local; esta tarea no ha retirado nada de la plataforma.
- Debe existir una sola copia del manuscrito y de ws-jbcb.cls.
- Si el ZIP se descomprime en la plataforma, main_jbcb_R2.tex es Manuscript.
  Conserva ws-jbcb.cls como archivo de apoyo LaTeX; usa la categoria de fuente
  que ofrezca el portal. Las cuatro figuras corresponden a Figure.
- No clasifiques Supplementary_Validation_R2.tex como segundo Manuscript.
- No hace falta archivo externo de bibliografia: ambos TeX contienen
  thebibliography. Tampoco hay input, include, bbl, bib ni bst externos.
- El manuscrito usa Figures 1-2 en el texto y Figures 3-4 para las redes completas
  en el apendice. El suplemento contiene Figures S1-S2.
- Reconstruye el PDF de la plataforma y revisalo antes de aprobarlo. La prueba
  local no garantiza la configuracion del servidor editorial.

## Comprobacion local

make package genera y prueba los tres ZIP en directorios vacios con tres pasadas
de pdflatex por maestro, sin BibTeX ni auxiliares preexistentes. Los resultados
estan en package_validation_R2.json. El articulo, suplemento y respuesta se
entregan tambien como PDF para compararlos con el resultado del portal.

No se ha efectuado el reenvio editorial ni se ha hecho push al repositorio remoto.
