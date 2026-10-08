# Informe final: segunda revision mayor JBCB-1505

## A. Auditoria matematica

- Early <=_w Late: verdadero.
- Late <=_w Early: falso.
- Bisimilitud debil: falsa.
- Igualdad exacta de trazas: verdadera, {epsilon, a, ab, ac}.

Testigo: {(e0,l0), (eb,l1), (ec,l1), (eb',lb), (ec',lc)}.
En la direccion inversa, (l1,eb) no responde a c y (l1,ec) no responde a b.
No se pueden fusionar ambos estados defensores despues del unico movimiento a.
La afirmacion tecnica atribuida al revisor no se confirma bajo la Definicion 4.
Se aclaro la exposicion, sin introducir una correccion matematica falsa.

Coinciden la implementacion principal, el juego previo, un nuevo juego con
cierres debiles construidos independientemente, el verificador de relaciones
explicitas y mCRL2 en los casos sin tau. La igualdad de trazas se comprobo
sin limitarla a profundidad k.

## B. Proposicion 2

- Debil no implica fuerte: a.0 frente a a.tau.0.
- Simulacion mutua no implica bisimilitud: a.(b+c)+a.b frente a a.(b+c).
- Igualdad de trazas no implica simulacion mutua: late frente a early.

Se preservo la jerarquia y se agrego una tabla que distingue los tres testigos.

## C. Otros cambios formales

No se encontro otro error matematico ni una inversion direccional.
Se retuvo el teorema de punto fijo y su prueba para eliminacion en sitio.
Se agregaron certificados, campos explicitos izquierda/derecha, inventario de
afirmaciones y pruebas de regresion. La auditoria de 32 pares concretos y tres
testigos coincide en todos los predicados.
El universo de 67.600 pares no tiene discrepancias ni violaciones de jerarquia;
41.080 pares son debilmente bisimilares y 4.848 tienen simulacion mutua sin
bisimilitud. No se extrapola esta comprobacion finita a una prueba general.

## D. Reorientacion para JBCB

Titulo anterior:
A formal and reproducible framework for auditing observable behavior in
qualitative biological network models.

Titulo nuevo:
Locating resolution-dependent behavioral correspondence in qualitative
DNA-damage response models.

El resumen, de 170 palabras, y la introduccion se reescribieron desde cero.
Antes destacaban controles, herramientas y cifras de verificacion; ahora
destacan la pregunta DDR, los modelos animal/Arabidopsis, la resolucion del
readout y el resultado GIM. Se retiraron del resumen 6/6, 42, 67.600 y p=0.25.

Orden: pregunta biologica; modelos/interfaces; metodo; GIM; casos secundarios;
HPN exploratorio; verificacion breve; discusion; conclusion; apendices.
La discusion responde que aporta la estructura, que agrega comparar conducta
ejecutable y que significa refinar la observacion.

## E. GIM

PN-GDDA reproducido: 0.9975845917160132, constante.
A y B: bisimilitud debil, ambas simulaciones, d6=0.
C: ninguna simulacion, d6=0.3529411764705882.
Los modelos, estados iniciales y estructuras no fueron cambiados.

El limite se localiza entre B y C dentro de las tres interfaces declaradas.
No se afirma haber encontrado una resolucion minima global, una diferencia
biologica desconocida o una frontera experimentalmente validada.
La diferenciacion/endoreduplicacion vegetal sigue siendo una transicion
combinada, no dos alternativas independientes.

## F. Material de validacion

El texto principal conserva definiciones, algoritmo, resultado GIM y pruebas
matematicas en el apendice. Las dos redes de Petri completas siguen presentes.
Controles sinteticos, comparadores, mCRL2, modelos publicos, escalabilidad y
auditorias detalladas pasan a Supplementary Validation. No se borraron analisis.

## G. HPN

Se conserva como contraste exploratorio secundario, sin escala ordinal de
clases ni busqueda de una estadistica mas favorable. Se mantienen los nueve
pares-condicion, direcciones y resultados inconclusos. El p=0.25 esta fuera
del resumen pero sigue visible en el texto y suplemento.
Se regeneraron las relaciones y permutaciones; no se volvio a ejecutar el
optimizador CASPOTS, cuyos resultados previos se conservaron sin modificacion.

## H. Verificaciones ejecutadas

Entorno cientifico: /opt/anaconda3/bin/python (Python 3.11).
mCRL2: lanzamiento oficial 202607.0, DMG comprobado por SHA-256.

- make test PY=/opt/anaconda3/bin/python: 63 pruebas, 63 aprobadas, sin omisiones
  tras incorporar las comprobaciones de carta autocontenida y tabla de seccion 7.
- make figures PY=/opt/anaconda3/bin/python: tablas y figuras regeneradas.
- make verify PY=/opt/anaconda3/bin/python: aprobado; incluye ahora la auditoria R2.
  Los resultados deterministas se regeneran identicos; tiempos excluidos.
- make notebook PY=/opt/anaconda3/bin/python: 50 celdas; 26 de codigo ejecutadas,
  cero errores.
- python -m src.formal_revision_audit: todos los pares y propiedades pasan.
- python scripts/run_R2_external_audit.py: mCRL2 coincide en los tres testigos.
- make jbcb-r2-package PY=/opt/anaconda3/bin/python: compila y verifica los ZIP.
- git diff --check: sin errores de espacios.

Pandas emitio un aviso no fatal por una version antigua de numexpr; no hubo
fallos de calculo ni diferencias en resultados. No se modifico el entorno
global para silenciarlo.

## I. Compilacion y presentacion

Articulo: 22 paginas, 4 figuras, 5 tablas, 29 referencias.
Suplemento: 7 paginas, 2 figuras, bibliografia interna.
Respuesta: 7 paginas, 13 puntos de respuesta.

La respuesta se amplio posteriormente a peticion del autor para ser autocontenida:
se retiraron las referencias a documentos locales y archivos de resultados o codigo,
y se incorporaron las transiciones, tablas y argumentos pertinentes en la carta.
Se recompilo sin advertencias y se revisaron visualmente sus siete paginas.
Las seis pruebas de integridad documental pasan, incluida una nueva prueba que
impide reintroducir referencias a archivos locales. No se cambiaron los resultados
cientificos, el articulo, el suplemento ni los ZIP durante aquella correccion
exclusiva de la carta.

En el refuerzo posterior solicitado para la seccion 7, se incorporo la nueva
Tabla 4 con cinco comprobaciones, procedimientos independientes y resultados.
La tabla de testigos del apendice pasa a ser la Tabla 5. Se actualizaron las
referencias en la carta, la matriz y la auditoria, y se recompilaron los ZIP
completo y manuscript-only desde carpetas limpias. El suplemento conserva
el mismo contenido y el mismo ZIP. La revision visual detecto y resolvio un
desbordamiento de columnas que no aparecia en el registro de LaTeX: la tabla
final usa anchos fijos y se presenta completa en la pagina 11.

Se revisaron visualmente las paginas, figuras, tablas y ejemplos matematicos.
Se elimino una pagina casi vacia sin retirar contenido cientifico.
Las columnas del esquema GIM representan categorias funcionales, no una
secuencia causal obligatoria entre reparacion y apoptosis.
No hay referencias sin resolver, desbordamientos ni advertencias en los
registros finales de compilacion.

Los ZIP son planos. Cada maestro se compilo desde una carpeta vacia con tres
pasadas de pdflatex, sin BibTeX ni auxiliares previos. Ambos documentos incluyen
thebibliography. La clase oficial no fue modificada.

## J. Entregables

Accesos directos:
- [Articulo: fuente LaTeX](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/main_jbcb_R2.tex).
- [Articulo: PDF](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/main_jbcb_R2.pdf).
- [Respuesta: fuente LaTeX](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/response_to_reviewer_R2.tex).
- [Respuesta: PDF](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/response_to_reviewer_R2.pdf).
- [Auditoria formal](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/formal_audit_report.md).
- [Matriz de comentarios](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/reviewer_comment_matrix.md).
- [Diferencias R1-R2](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/main_jbcb_R1_to_R2.diff).
- [Suplemento: fuente LaTeX](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/Supplementary_Validation_R2.tex).
- [Suplemento: PDF](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/Supplementary_Validation_R2.pdf).
- [ZIP completo](/Users/cero/Downloads/Articulos/CompAlgMolCancer/JBCB-1505-R2.zip).
- [ZIP recomendado para Manuscript](/Users/cero/Downloads/Articulos/CompAlgMolCancer/JBCB-1505-R2-manuscript-only.zip).
- [Instrucciones de carga](/Users/cero/Downloads/Articulos/CompAlgMolCancer/revision_R2/UPLOAD_R2.md).

Dentro de revision_R2/:
- main_jbcb_R2.tex y main_jbcb_R2.pdf.
- response_to_reviewer_R2.tex, .md y .pdf.
- Supplementary_Validation_R2.tex y .pdf.
- formal_audit_report.md y formal_direction_audit.md.
- reviewer_comment_matrix.md.
- manuscript_changes_R2.md y main_jbcb_R1_to_R2.diff.
- direction_statement_inventory.csv y main_text_space_audit.json.
- baseline_sha256.json, package_validation_R2.json y UPLOAD_R2.md.

En la raiz del proyecto:
- JBCB-1505-R2.zip: fuentes completas, 9 archivos planos, dos maestros.
- JBCB-1505-R2-manuscript-only.zip: recomendado para Manuscript, 6 archivos.
- JBCB-1505-R2-supplement.zip: fuentes suplementarias, si las solicita el portal.

Para cargar: ZIP manuscript-only como Manuscript, suplemento PDF como
Supplemental Material y respuesta PDF como Reply to Referee's Comments.
No cargar simultaneamente los ZIP completo y manuscript-only.

Se preservaron los nueve archivos R1 byte por byte. Se actualizaron localmente
el README y la guia de reproducibilidad. No se hizo commit, push ni reenvio
editorial. Antes de citar los nuevos archivos R2 como disponibles en GitHub,
los cambios deben publicarse en el repositorio remoto.

## Lista final de integridad

- [x] Definicion, ejemplo, jerarquia, teorema y orientaciones auditados.
- [x] Lenguajes exactos separados de diagnosticos truncados.
- [x] Resultados sinteticos, GIM, RCD y HPN comprobados.
- [x] Oraculos independientes y pruebas de regresion satisfactorios.
- [x] Narrativa centrada en GIM; controles como evidencia de soporte.
- [x] Conocimiento previo, resultado del modelo e hipotesis experimental separados.
- [x] Redes completas, pruebas y resultados negativos conservados.
- [x] Respuesta, matriz, diferencias y documentos compilados.
- [x] ZIP planos comprobados en directorios limpios.
- [x] Sin cambios en archivos ajenos a esta revision ni envio editorial.
