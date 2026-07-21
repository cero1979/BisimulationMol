# NetMAHIB upload package

Run `make package` from the repository root. Upload
`netmahib_latex_flat.zip` as the LaTeX manuscript/source item.

The archive is intentionally flat and self-contained. `main.tex` is the root
document and already includes the title, author, affiliation, corresponding
author email, abstract, keywords and declarations. A separate title-page file
is therefore not required for compilation.

Do not upload `main.tex` alone: it depends on the included Springer Nature
class, bibliography style, bibliography database and 12 vector artwork files
that compose eight figures. The PDF files inside the ZIP are figure assets, not
a manuscript PDF; they are accepted by LaTeX through `\includegraphics`. The
ZIP contains all dependencies and can be tested with:

```bash
unzip netmahib_latex_flat.zip -d /tmp/netmahib-check
cd /tmp/netmahib-check
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

In the submission interface, repeat the author-contribution and competing-
interest statements in their dedicated fields. Add the author's ORCID there if
one is available. The main source already includes the required data- and
code-availability statements and documents the use of OpenAI Codex during
revision.
