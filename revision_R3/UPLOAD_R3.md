# Reenvio JBCB-1505: R3

Actualizacion del 23 de septiembre: los paquetes reconstruidos incorporan la
refutacion de igualdad global de trazas basales. Sustituir cualquier copia
anterior de R3; no mezclar el manuscrito corregido con respuesta o suplemento
anteriores. El resultado condicionado al estado compartido no cambia.

## Archivos recomendados

1. Manuscript: `JBCB-1505-R3-manuscript-only.zip`.
2. Reply to Referee's Comments: `revision_R3/response_to_reviewer_R3.pdf`.
3. Supplemental Material: `revision_R3/Supplementary_Validation_R3.pdf`.
4. Codigo/datos suplementarios, si la plataforma admite el archivo: `JBCB-1505-R3-reproducibility.zip`.

El cuarto archivo es importante si R3 aun no se ha publicado en el repositorio:
contiene el codigo, los datos y el cuaderno ejecutado de esta revision. Tiene
directorios porque es un suplemento de reproducibilidad, NO un archivo LaTeX.
No se debe clasificar como Manuscript ni enviarlo al compilador LaTeX. Si el
portal no admite ZIP de codigo, debera publicarse esa version del repositorio
antes de afirmar que todo R3 esta accesible remotamente.

## Evitar los errores anteriores

- Desmarcar o retirar todos los archivos de R1/R2 antes de cargar R3; no conservar
  el maestro anterior ni figuras con nombres duplicados.
- El ZIP del manuscrito contiene exactamente seis archivos en la raiz:
  `main_jbcb_R3.tex`, `ws-jbcb.cls`, `R3_Fig1.pdf`, `R3_Fig2.pdf`,
  `R3_Fig3.pdf`, `R3_Fig4.pdf`. No tiene carpetas ni archivos ocultos.
- Si el portal descomprime el ZIP, identificar `main_jbcb_R3.tex` como el unico
  maestro Manuscript. Las cuatro figuras deben seguir disponibles para LaTeX;
  no son cuatro articulos distintos. La clase `ws-jbcb.cls` es una dependencia
  obligatoria, no una figura ni texto suplementario para convertir a PDF.
- No hay bibliografia externa: el maestro contiene `thebibliography` y todas
  las tablas. No requiere `.bib`, `.bbl`, `.bst`, BibTeX ni archivos `.md`.
- No subir simultaneamente el ZIP combinado y el ZIP manuscript-only: eso
  duplicaria el maestro, la clase y las figuras.
- Construir la vista previa y revisar que aparezcan titulo R3, Figura 1 de
  compromiso celular, tablas, redes de Petri y referencias sin `??`.
- No aprobar el envio si el portal informa nombres duplicados, fuentes faltantes
  o referencias no resueltas. La compilacion local verificada no garantiza
  configuraciones identicas en el servidor editorial.

## Alternativas

`JBCB-1505-R3.zip` es el paquete combinado plano: los seis archivos del
manuscrito mas los PDF del suplemento y la respuesta. Solo tiene un maestro
TeX. Puede usarse en lugar del conjunto anterior si el portal permite
clasificar correctamente cada archivo extraido.

`JBCB-1505-R3-supplement.zip` contiene el maestro del suplemento, la clase y sus
dos figuras. Usarlo solo si se solicitan sus fuentes; no clasificar ese maestro
como segundo manuscrito principal.

Los paquetes se verifican con tres pasadas de pdfLaTeX desde directorios vacios.
Las fuentes archivadas coinciden byte a byte con las finales. Los hashes y
resultados estan en `package_validation_R3.json`. No se ha realizado ningun
envio editorial ni push a GitHub en esta tarea.
