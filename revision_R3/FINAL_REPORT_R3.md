# Informe final R3: JBCB-1505

## Conclusion cientifica

La revision incorpora una comparacion biologica con interfaz fija y una
intervencion explicita. El resultado corresponde al **patron B**, acuerdo
exacto de destinos basales con diferencias en futuros tras retirar TNF.
**No demuestra el patron A**, igualdad global de trazas con diferencia
exclusivamente ramificada. Esta limitacion aparece en resumen, resultados,
discusion y respuesta al revisor, no solamente en este informe.

La ejecucion del plan aprobado esta completada; no equivale a asegurar que
el revisor acepte esta version mas debil de su ejemplo ideal. La igualdad de
todas las trazas basales esta ahora refutada; solo la inclusion inversa sigue
sin decidirse. No hay nueva validacion experimental. No se debe presentar una probabilidad de aceptacion calculada
a partir de estas pruebas de software.

## Candidato 1: receptor de muerte

- Importacion: modelo original de Calzone et al. (2010), 28 nodos Booleanos,
  archivo oficial GINsim, DOI `10.1371/journal.pcbi.1000702`.
- FB+: reglas originales; FB-: solo se elimina la lectura CASP3 en CASP8,
  sin hacer knockout de CASP3. La publicacion ya analiza esa interaccion.
- Inicializacion: TNF=FADD=ATP=cIAP=1; todos los otros nodos=0, incluido FASL.
- Semantica: actualizacion asincrona unitaria; retirada irreversible de TNF
  como accion adicional que cambia solo esa entrada.
- Interfaz fija: activacion/desactivacion de NFkB, CASP3 y MPT, mas withdraw_TNF.
  ATP se conserva para clasificar destinos, sin convertirse en etiqueta visible.
- Configuracion prospectiva local, no registro externo: SHA-256
  `408936bf397586897e72b73004084c7210a81084b9b74826ce7d7e6d637075c6`.
- Tres enmiendas computacionales conservadas: eliminacion exacta de tres
  salidas ocultas sin regulaciones salientes y representacion compacta de
  estados/aristas y ampliacion del presupuesto de busqueda basal.
  No se cambiaron interfaz ni reglas retenidas.

| Protocolo | Modelo | Estados retenidos | Aristas |
|---|---|---:|---:|
| TNF sostenido | FB+ | 1,044,457 | 10,296,917 |
| TNF sostenido | FB- | 547,021 | 5,062,632 |
| Retirada permitida | FB+ | 3,133,393 | 32,980,090 |
| Retirada permitida | FB- | 2,140,569 | 21,544,296 |

Ambos modelos sostenidos tienen exactamente los destinos terminales
supervivencia, apoptosis y necrosis. La busqueda basal ampliada alcanzo 6,158
pares y 1,999,975,480 bytes antes del limite de memoria, despues de encontrar
una palabra de 12 acciones posible solo en FB+:

`MPT_up, CASP3_up, CASP3_down, NFkB_up, NFkB_down, MPT_down,
CASP3_up, CASP3_down, CASP3_up, CASP3_down, CASP3_up, CASP3_down`.

La propagacion exacta, una comprobacion independiente con SciPy y mCRL2
confirman el contraejemplo. Su trayectoria positiva de 53 actualizaciones
satisface las reglas originales de los 28 nodos. Por tanto, la igualdad basal
global es falsa y FB- no simula debilmente a FB+; tampoco son debilmente
bisimilares. La inclusion inversa no esta decidida. La exploracion incompleta
no es la prueba de desigualdad: lo es la palabra verificada. El producto
directo de reglas completas para esta palabra agoto su limite de 100,000
estados y no se presenta como una comprobacion exitosa.

### Hallazgo principal y testigo

Un estado compartido se alcanza tras ocho actualizaciones:
TNFR, DISC_TNF, CASP8, BAX, MOMP, Cyt_c, apoptosome y CASP3, todas activaciones.
Su proyeccion visible es `CASP3_up`. La busqueda selecciona automaticamente
el primer estado por profundidad que satisface el criterio de compromiso;
no se afirma una observacion biologica globalmente mas corta.

Desde ese estado, con TNF sostenido, ambos sistemas tienen 3 estados, 2 aristas
silenciosas y lenguaje exacto `{epsilon}`: bisimulacion fuerte y debil.
Si se permite la retirada, K+ tiene 12 estados/17 aristas y K- tiene
34 estados/54 aristas:

`K+ <=_w K-`, pero `K- not<=_w K+` y `K+ not~_w K-`.

K- permite `withdraw_TNF, CASP3_down`; K+ no. El certificado de eliminacion
incluye todas las respuestas defensoras. Tras la retirada inmediata, K+
mantiene CASP3 y solo tiene destino terminal apoptotico; K- solo tiene la
firma terminal naive. Son continuaciones aciclicas. **Naive no significa
recuperacion de una celula que ya ejecuto apoptosis.**

La historia visible admite 78 estados ocultos en cada variante. Sus futuros
terminales agregados tras retirar TNF son `{apoptosis, naive, necrosis}` en
FB+ y `{naive, necrosis}` en FB-. La observacion no identifica unicamente el
estado testigo ni implica compromiso en todos los estados compatibles.

El escaneo de profundidades 0--40 es exhaustivo para cada profundidad, sin
truncar los futuros posteriores. Apoptosis aparece como posibilidad tras una
actualizacion; compromiso con CASP3 persistente aparece por primera vez a
profundidad 8, en uno de 73 estados FB+. No aparece en FB- en ese escaneo.
Son conteos de estados, no probabilidades celulares ni minutos.

### Diferencias globales con intervencion

Los lenguajes globales con retirada son diferentes en ambas inclusiones:

- Solo FB+: `withdraw_TNF, CASP3_up, CASP3_down, CASP3_up`.
- Solo FB-: `CASP3_up, withdraw_TNF, CASP3_down`.

Por tanto, fallan ambas simulaciones debiles globales y ambas bisimilitudes.
Una segunda implementacion, usando directamente las reglas de los 28 nodos,
confirma aceptacion/rechazo para ambas palabras sin usar la reduccion ni
el ejecutor compacto. Esto tambien deja claro que, al incluir la retirada,
la comparacion de trazas puede detectar la diferencia: no es una separacion
observable exclusivamente mediante bisimulacion.

La utilidad biologica es una reconstruccion relacional verificable de un
fenomeno publicado, con estado/historia, futuros y observacion discriminante
explicitos. No es un descubrimiento del feedback ni del experimento de retirada.

## Candidato 2: punto de restriccion

No se ejecuto en el plan inicial, pero una exploracion posterior autorizada
comparo los modelos publicos de 2006 y 2016 con dos interfaces y dos protocolos.
En las cuatro comparaciones hubo desigualdad de trazas. No se incorpora al
articulo como solucion al ejemplo de separacion exclusivamente ramificada.

## Cambios del manuscrito

- Titulo de produccion, actualizado el 2026-10-02: *Locating resolution-dependent
  behavioral correspondence in qualitative DNA-damage response models*.
- Resumen centrado en compromiso y limites exactos, incluida la refutacion basal.
- Introduccion y modelos: pregunta biologica, procedencia y semantica explicitas.
- Seccion 4 y nueva Figura 1: acuerdo basal, testigo, futuros e intervencion.
- Tabla de estatus evidencial: supuestos, resultados, implicacion y ausencia de
  evidencia experimental separados.
- GIM pasa a la Seccion 5 como ilustracion secundaria. La perdida de
  correspondencia se restringe a las tres interfaces probadas, no a una
  frontera biologica unica o globalmente minima. Se conservan las redes de Petri.
- Seccion 7: comprobaciones locales/globales, oraculos, reduccion y limites.
- Discusion: dos preguntas separadas, compromiso con interfaz fija y
  sensibilidad a la interfaz; conclusion ajustada al patron realmente obtenido.
- Las 19 definiciones/proposiciones/teoremas/pruebas/ejemplos/algoritmos
  comparados permanecen identicos al R2 proporcionado.
- Carta al revisor autocontenida: sin referencias a `.md`, codigo ni JSON.

## Reproducibilidad y verificacion

`results/death_receptor_*.json` contiene comparaciones, trazas, certificado,
oraculos e interpretacion por alcance; el CSV de compromiso tiene 82 filas.
La fuente original, configuracion y enmiendas tienen hashes preservados.
`reproducibility_check_R3.json` registra igualdad byte a byte en 12 archivos
de resultados, interfaz y auditorias conservadas, comprobados antes/despues
de la ejecucion completa del cuaderno.

El cuaderno completo se ejecuto sin errores: 53 celdas totales, 28 celdas de
codigo y 28 ejecutadas. Incluye ahora la figura central y la comprobacion
independiente de palabras con 28 nodos. Las comprobaciones mCRL2 locales
coinciden en seis decisiones (fuerte/debil/trazas para dos protocolos).
Los cuatro intentos globales weak-bisim/weak-trace originales agotaron 180
segundos por comando: son inconclusos, no validaciones exitosas. Las palabras
con retirada y el nuevo contraejemplo sostenido resuelven la desigualdad en
ambos protocolos. La nueva comprobacion mCRL2 del lenguaje finito de la palabra
sostenida se reproduce desde los modelos originales, sin caches pickle.

La suite de la correccion incluye las nuevas regresiones de desigualdad basal,
inclusion inversa desconocida y trayectoria positiva en reglas originales,
con **90/90 pruebas aprobadas**, ademas de las regresiones
matematicas R2, reglas e inicializacion, ejecutores y ciclos, limites de
recursos, certificados con todas las respuestas defensoras, auditoria de
palabras con 28 nodos y dependencias del paquete. La revision independiente
detecto una debilidad de enlace entre certificado y direccion declarada;
se corrigio mediante una prueba que fallo antes y paso despues. Los resultados
biologicos no cambiaron.

Las fuentes se compilan con tres pasadas de pdfLaTeX desde directorios vacios,
sin BibTeX, auxiliares heredados o archivos de bibliografia externos. Se revisan
referencias, desbordamientos, paginas renderizadas y contenido exacto del ZIP.
Los informes ejecutables de verificacion se conservan junto a las fuentes.
El manuscrito tiene 27 paginas, el suplemento 10 y la respuesta 3.
Los hashes y comprobaciones de esta correccion se
registran en los informes de verificacion actualizados junto a las fuentes.

## Entregables

- `revision_R3/main_jbcb_R3.tex` y PDF.
- `revision_R3/response_to_reviewer_R3.tex` y PDF.
- `revision_R3/Supplementary_Validation_R3.tex` y PDF.
- `JBCB-1505-R3-manuscript-only.zip`: recomendado para Manuscript.
- `JBCB-1505-R3-supplement.zip`: fuentes suplementarias si son solicitadas.
- `JBCB-1505-R3.zip`: alternativa combinada plana; no cargar junto al anterior.
- `JBCB-1505-R3-reproducibility.zip`: codigo/datos/cuaderno, suplemento separado.
- `revision_R3/UPLOAD_R3.md`: clasificacion y prevencion de duplicados.

R2 y los cambios ajenos se conservaron. No se hizo commit, push ni envio
editorial. El paquete de reproducibilidad permite compartir R3 sin fingir
que la version remota ya contiene estos cambios.
