%%
%% This is file `ISRP.cls',
%% 
%%
%% 
%% Provided by  Alireza Yeganehparast
%%
%% 
%% 
%% 
%% 
%% -------------------------------------------
%% 
%% It may be distributed under the conditions of the LaTeX Project Public
%% License, either version 1.2 of this license or (at your option) any
%% later version.  The latest version of this license is in
%%    http://www.latex-project.org/lppl.txt
%% and version 1.2 or later is part of all distributions of LaTeX
%% version 1999/12/01 or later.
%% 
%% 
%%
%% generated base on  the 'elsarticle.cls' .
%%
%%

 \def\RCSversion{1}%
 \def\RCSdate{2024/08/01}%
 \def\@shortpid{ISRP}
 
 
 
 \newif\ifJMCS   \JMCStrue
 \newif\ifMNS    \MNSfalse
 \newif\ifJNSA   \JNSAfalse

 \DeclareOption{JMCS}{
 	\gdef\@journal{Journal of Mathematics and Computer Science}
 	\gdef\@journalabbr{J. Math. Computer Sci.}
 	\gdef\@shortjid{jmcs}
 	\gdef\@issn{2008-949X}
 	\JMCStrue \MNSfalse \JNSAfalse
 }
 
  
 \DeclareOption{JNSA}{
 	\gdef\@journal{Journal of Nonlinear Sciences and Applications}
 	\gdef\@journalabbr{J. Nonlinear Sci. Appl.}
 	\gdef\@shortjid{jnsa}
 	\gdef\@issn{2008-1898}
 	\JMCSfalse \MNSfalse \JNSAtrue
 }
 
 
  
 \DeclareOption{MNS}{
 	\gdef\@journal{Mathematics in Natural Science}
 	\gdef\@journalabbr{Math. Nat. Sci.}
 	\gdef\@shortjid{mns}
 	\gdef\@issn{2600-7665}
 	\JMCSfalse \MNStrue \JNSAfalse
 }
\ExecuteOptions{JMCS}% Sets JMCS as the default
\ProcessOptions\relax


\newif\ifsubmit \submitfalse
\newif\ifaccept \acceptfalse

\DeclareOption{submit}{
	\submittrue
	\acceptfalse
}

\DeclareOption{accept}{
	\accepttrue
	\submitfalse
}
\ExecuteOptions{submit}
\ProcessOptions\relax






\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resources/\@shortpid}[\RCSdate, \RCSversion: ]
\newif\ifpreprint \preprintfalse
\newif\iflongmktitle \longmktitlefalse

\def\@blstr{1}
\newdimen\@bls
\@bls=\baselineskip



\DeclareOption{preprint}{\global\preprinttrue
  \gdef\@blstr{1}\xdef\jtype{0}%
   \AtBeginDocument{\@twosidefalse\@mparswitchfalse}}
\DeclareOption{final}{\gdef\@blstr{1}\global\preprintfalse}
\DeclareOption{review}{\global\preprinttrue\gdef\@blstr{1.5}}
\DeclareOption{authoryear}{\xdef\@biboptions{round,authoryear}}
\DeclareOption{number}{\xdef\@biboptions{numbers}}
\DeclareOption{numbers}{\xdef\@biboptions{numbers}}
\DeclareOption{longtitle}{\global\longmktitletrue}
\DeclareOption{5p}{\xdef\jtype{5}\global\preprintfalse
  \ExecuteOptions{twocolumn}}
  \def\jtype{0}
\DeclareOption{3p}{\xdef\jtype{3}\global\preprintfalse}
\DeclareOption{1p}{\xdef\jtype{1}\global\preprintfalse
  \AtBeginDocument{\@twocolumnfalse}}
\DeclareOption{times}{\IfFileExists{txfonts.sty}%
  {\AtEndOfClass{\RequirePackage{txfonts}%
  \gdef\ttdefault{cmtt}%
   \let\iint\relax
  \let\iiint\relax
  \let\iiiint\relax
  \let\idotsint\relax
  \let\openbox\relax}}{\RequirePackage{times}}}
\ExecuteOptions{a4paper,10pt,oneside,onecolumn,number,preprint}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions
\LoadClass[11pt]{article}
\RequirePackage{graphicx}
\RequirePackage{color}
\RequirePackage{amscd, amsfonts, amssymb}
\RequirePackage[utf8]{inputenc}   % Handles UTF-8 input
\RequirePackage[T1]{fontenc}      % Ensures proper font encoding
\definecolor{mycol}{RGB}{8, 57, 113}
\RequirePackage{pifont}
\RequirePackage{lineno}
%\RequirePackage[\@biboptions]{natbib}
\RequirePackage[backref,colorlinks=true]{hyperref}
\RequirePackage{lmodern} 
\RequirePackage[sc]{mathpazo} 
\RequirePackage[scaled]{helvet} 
\RequirePackage{eulervm}
\RequirePackage[hang,flushmargin]{footmisc}


\RequirePackage{caption} 
\captionsetup[figure]{position=bottom, margin=0.75cm, labelfont={bf, small, stretch=1.17}, labelsep=period, textfont={small, stretch=1.17}, aboveskip=6pt, belowskip=-6pt, justification=justified}

\captionsetup[table]{position=top, margin=0.75cm, labelfont={bf, small, stretch=1.17}, labelsep=period, textfont={small, stretch=1.17}, aboveskip=6pt, justification=justified}








\let\comma\@empty
\let\tnotesep\@empty
\def\title#1{\gdef\@title{#1}}
\let\@title\@empty

\def\elsLabel#1{\@bsphack\protected@write\@auxout{}%
         {\string\Newlabel{#1}{\@currentlabel}}\@esphack}
\def\Newlabel#1#2{\expandafter\xdef\csname X@#1\endcsname{#2}}

\def\elsRef#1{\@ifundefined{X@#1}{0}{\csname X@#1\endcsname}%
}

\def\tnotemark[#1]{\textsuperscript{\@for\@@tmark:=#1\do{%
      \edef\tnotenum{\@ifundefined{X@\@@tmark}{1}{\elsRef{\@@tmark}}}%
      \ifcase\tnotenum\or\ding{73}\or,\ding{73}\ding{73}\fi}}%
}
\let\@tnotemark\@empty

\let\@tnotes\@empty

\newcounter{tnote}
\def\tnotetext[#1]#2{\g@addto@macro\@tnotes{%
  \refstepcounter{tnote}\elsLabel{#1}%
   \def\thefootnote{\ifcase\c@tnote\or\ding{73}\or\ding{73}\ding{73}\fi}%
    \footnotetext{#2}}}

\let\@nonumnotes\@empty
\def\nonumnote#1{\g@addto@macro\@nonumnotes{%
     \let\thefootnote\relax\footnotetext{#1}}}

\newcounter{fnote}
\def\fnmark[#1]{\let\comma\@empty
    \def\@fnmark{\@for\@@fnmark:=#1\do{%
    \edef\fnotenum{\@ifundefined{X@\@@fnmark}{1}{\elsRef{\@@fnmark}}}%
  \unskip\comma\fnotenum\let\comma,}}%
}

\let\@fnotes\@empty\let\@fnmark\@empty
\def\fntext[#1]#2{\g@addto@macro\@fnotes{%
     \refstepcounter{fnote}\elsLabel{#1}%
   \def\thefootnote{\thefnote}%
   \global\setcounter{footnote}{\thefnote}%
   \footnotetext{#2}}}


\def\cormark[#1]{\edef\cnotenum{\elsRef{#1}}%
	\unskip\textsuperscript{\sep\ifcase\cnotenum\or
		$\ast$\or$\ast\ast$\fi\hspace{-1pt}}\let\sep=,}

\let\@cormark\@empty
\let\@cornotes\@empty
\newcounter{cnote}
\def\cortext[#1]#2{\g@addto@macro\@cornotes{%
		\refstepcounter{cnote}\elsLabel{#1}%
		\def\thefootnote{\ifcase\thecnote\or$\ast$\or
			$\ast\ast$\fi}%
		\footnotetext{#2}}}
\let\@corref\@empty
\def\corref#1{\edef\cnotenum{\elsRef{#1}}%
	\edef\@corref{\ifcase\cnotenum\or
		$\ast$\or$\ast\ast$\fi\hskip-1pt}}


\def\fnref#1{\fnmark[#1]}
\def\tnoteref#1{\tnotemark[#1]}

\def\resetTitleCounters{\c@cnote=0
	\c@fnote=0 \c@tnote=0 \c@footnote=0}

\let\eadsep\@empty
\let\@elseads\@empty
\let\@elsuads\@empty
\let\@cormark\@empty
\def\hashchar{\expandafter\@gobble\string\~}
\def\underscorechar{\expandafter\@gobble\string\_}
\def\lbracechar{\expandafter\@gobble\string\{}
\def\rbracechar{\expandafter\@gobble\string\}}

\def\ead{\@ifnextchar[{\@uad}{\@ead}}
\gdef\@ead#1{\bgroup\def\_{\string\underscorechar\space}%
	\def\{{\string\lbracechar\space}%
	\def~{\hashchar\space}%
	\def\}{\string\rbracechar\space}%
	\edef\tmp{\the\@eadauthor}
	\immediate\write\@auxout{\string\emailauthor
		{#1}{\expandafter\strip@prefix\meaning\tmp}}%
	\egroup
}
\newcounter{ead}
\gdef\emailauthor#1#2{\stepcounter{ead}%
	\g@addto@macro\@elseads{\raggedright%
		\let\corref\@gobble
		\eadsep\texttt{#1} (#2)\def\eadsep{\unskip,\space}}%
}
\gdef\@uad[#1]#2{\bgroup
	\def~{\string\hashchar\space}%
	\def\_{\string\underscorechar\space}%
	\edef\tmp{\the\@eadauthor}
	\immediate\write\@auxout{\string\urlauthor
		{#2}{\expandafter\strip@prefix\meaning\tmp}}%
	\egroup
}
\def\urlauthor#1#2{\g@addto@macro\@elsuads{\let\corref\@gobble%
		\raggedright\eadsep\texttt{#1}\space(#2)%
		\def\eadsep{\unskip,\space}}%
}

\def\elsauthors{}
\let\authorsep\@empty
\let\sep\@empty
\newcounter{author}
\def\author{\@ifnextchar[{\@@author}{\@author}}

\newtoks\@eadauthor
\def\@@author[#1]#2{\g@addto@macro\elsauthors{%
		\def\baselinestretch{1}%
		\authorsep#2\unskip\textsuperscript{%#1%
			\@for\@@affmark:=#1\do{%
				\edef\affnum{\@ifundefined{X@\@@affmark}{1}{\elsRef{\@@affmark}}}%
				\unskip\sep\affnum\let\sep=,}%
			\ifx\@fnmark\@empty\else\unskip\sep\@fnmark\let\sep=,\fi
			\ifx\@corref\@empty\else\unskip\sep\@corref\let\sep=,\fi
		}%
		\def\authorsep{\unskip,\space}%
		\global\let\sep\@empty\global\let\@corref\@empty
		\global\let\@fnmark\@empty}%
	\@eadauthor={#2}
}

\def\@author#1{\g@addto@macro\elsauthors{\normalsize%
		\def\baselinestretch{1}%
		\upshape\authorsep#1\unskip\textsuperscript{%
			\ifx\@fnmark\@empty\else\unskip\sep\@fnmark\let\sep=,\fi
			\ifx\@corref\@empty\else\unskip\sep\@corref\let\sep=,\fi
		}%
		\def\authorsep{\unskip,\space}%
		\global\let\@fnmark\@empty
		\global\let\@corref\@empty
		\global\let\sep\@empty}%
	\@eadauthor={#1}
}






\def\elsaddress{}
\def\addsep{\par\vskip6pt}
\def\address{\@ifnextchar[{\@@address}{\@address}}

\def\@alph#1{%
  \ifcase#1\or a\or b\or c\or d\or e\or f\or g\or h\or i\or j\or k\or
  l\or m\or n\or o\or p\or q\or r\or s\or t\or u\or v\or w\or x\or
  y\or z%
  \or aa\or ab\or ac\or ad\or ae\or af\or ag\or ah\or ai\or aj\or
  ak\or al\or am\or an\or ao\or ap\or aq\or ar\or as\or at\or au\or
  av\or aw\or ax\or ay\or az%
  \or ba\or bb\or bc\or bd\or be\or bf\or bg\or bh\or bi\or bj\or
  bk\or bl\or bm\or bn\or bo\or bp\or bq\or br\or bs\or bt\or bu\or
  bv\or bw\or bx\or by\or bz%
  \or ca\or cb\or cc\or cd\or ce\or cf\or cg\or ch\or ci\or cj\or
  ck\or cl\or cm\or cn\or co\or cp\or cq\or cr\or cs\or ct\or cu\or
  cv\or cw\or cx\or cy\or cz%
  \or da\or db\or dc\or dd\or de\or df\or dg\or dh\or di\or dj\or
  dk\or dl\or dm\or dn\or do\or dp\or dq\or dr\or ds\or dt\or du\or
  dv\or dw\or dx\or dy\or dz%
  \or ea\or eb\or ec\or ed\or ee\or ef\or eg\or eh\or ei\or ej\or
  ek\or el\or em\or en\or eo\or ep\or eq\or er\or es\or et\or eu\or
  ev\or ew\or ex\or ey\or ez%
  \or fa\or fb\or fc\or fd\or fe\or ff\or fg\or fh\or fi\or fj\or
  fk\or fl\or fm\or fn\or fo\or fp\or fq\or fr\or fs\or ft\or fu\or
  fv\or fw\or fx\or fy\or fz%
  \or ga\or gb\or gc\or gd\or ge\or gf\or gg\or gh\or gi\or gj\or
  gk\or gl\or gm\or gn\or go\or gp\or gq\or gr\or gs\or gt\or gu\or
  gv\or gw\or gx\or gy\or gz%
  \else\@ctrerr\fi}

\newcounter{affn}
\renewcommand\theaffn{\alph{affn}}

\long\def\@@address[#1]#2{\g@addto@macro\elsaddress{%
    \def\baselinestretch{1}%
     \refstepcounter{affn}
     \xdef\@currentlabel{\theaffn}
     \elsLabel{#1}%
    \textsuperscript{\theaffn}#2\par}}

\long\def\@address#1{\g@addto@macro\elsauthors{%
    \def\baselinestretch{1}%
    \addsep\footnotesize\itshape#1\def\addsep{\par\vskip6pt}%
    \def\authorsep{\par\vskip8pt}}}

\ifsubmit
\newbox\absbox
\renewenvironment{abstract}{
	\global\setbox\absbox=\vbox\bgroup
	\hsize=\textwidth
	\normalsize\normalfont\def\baselinestretch{1}
	\parskip\z@
	\noindent\textbf{Abstract}\par\medskip
	\footnotesize
	\linenumbers  % Attempt to start line numbering within the box
}{
	\par \egroup
}

\else
\newbox\absbox
\renewenvironment{abstract}{\global\setbox\absbox=\vbox\bgroup
	\hsize=\textwidth\def\baselinestretch{1}%
	\noindent\unskip\textbf{Abstract}
	\par\medskip\indent\unskip\ignorespaces\footnotesize}
{\egroup}
\fi

\newbox\keybox
\def\keyword{%
	\def\sep{\unskip, }%
	\def\MSC{\@ifnextchar[{\@MSC}{\@MSC[2020]}}
	\def\@MSC[##1]{\vskip5pt\par\leavevmode\hbox {\bf ##1~MSC:}\space}%
	\def\PACS{\par\leavevmode\hbox {\it PACS:\space}}%
	\def\JEL{\par\leavevmode\hbox {\it JEL:\space}}%
	\global\setbox\keybox=\vbox\bgroup\hsize=\textwidth
	\normalsize\normalfont\def\baselinestretch{1}
	\parskip\z@
	\noindent\textit\footnotesize{\bf\footnotesize Keywords:}
	\raggedright                         % Keywords are not justified.
	\ignorespaces\footnotesize}
\def\endkeyword{\par \egroup}

\newdimen\Columnwidth
\Columnwidth=\columnwidth

\def\printFirstPageNotes{%
	\iflongmktitle
	\let\columnwidth=\textwidth\fi
	\ifx\@tnotes\@empty\else\@tnotes\fi
	\ifx\@nonumnotes\@empty\else\@nonumnotes\fi
	\ifx\@cornotes\@empty\else\@cornotes\fi
	\ifx\@elseads\@empty\relax\else
	\let\thefootnote\relax
	\footnotetext{
		\ifsubmit
		\ifnum\theead=1\relax
		{Email address:\space}\else
		{Email addresses:\space}\fi
		\@elseads\\[.5em]
		doi: \href{http://dx.doi.org/\@doi}{\@doi}\\[.5em]
		{\footnotesize\itshape
			Received: \ifx\@recivedat \@empty \today
			\else\@recivedat \fi \ \ \ 
			{\footnotesize\itshape
				Revised: \ifx\@revisedat \@empty \today
				\else\@revisedat \fi \ \ \  }
			{\footnotesize\itshape
				Accepted: \ifx\@\acceptedat \@empty \today
				\else\@\acceptedat \fi \hfill }
		}
		\else
		\ifnum\theead=1\relax
		{Email address:\space}\else
		{Email addresses:\space}\fi
		\@elseads\\[.5em]
		doi: \href{http://dx.doi.org/\@doi}{\@doi}\\[.5em]
		{\footnotesize\itshape
			Received: \ifx\@recivedat \@empty \today
			\else\@recivedat \fi \ \ \ 
			{\footnotesize\itshape
				Revised: \ifx\@revisedat \@empty \today
				\else\@revisedat \fi \ \ \  }
			{\footnotesize\itshape
				Accepted: \ifx\@\acceptedat \@empty \today
				\else\@\acceptedat \fi \hfill }
		}\fi 
	}\fi
	\ifx\@elsuads\@empty\relax\else
	\let\thefootnote\relax
	\footnotetext{\textit{URL:\space}%
		\@elsuads}\fi
	\ifx\@fnotes\@empty\else\@fnotes\fi
	\iflongmktitle\if@twocolumn
	\let\columnwidth=\Columnwidth\fi\fi
}


\def\doi#1{\gdef\@doi{#1}}
\let\@doi\@empty

\def\copyrightyear#1{\gdef\@copyrightyear{#1}}
\let\@copyrightyear\@empty

\def\vol#1{\gdef\@vol{#1}}
\let\@vol\@empty


\def\pages#1{\gdef\@pages{#1}}
\let\@pages\@empty

\def\authors#1{\gdef\@authors{#1}}
\let\@authors\@empty

\def\recivedat#1{\gdef\@recivedat{#1}}
\let\@recivedat\@empty


\def\revisedat#1{\gdef\@revisedat{#1}}
\let\@revisedat\@empty

\def\acceptedat#1{\gdef\@\acceptedat{#1}}
\let\@\acceptedat\@empty


\def\ps@printTitle{%
	\let\@oddhead\@empty
	\let\@evenhead\@empty
	\let\@oddfoot\@empty%
	\let\@evenfoot\@oddfoot}
\def\@seccntDot{.}
\def\@seccntformat#1{\csname the#1\endcsname\@seccntDot\hskip 0.5em}






\ifsubmit
% Hide author names and addresses
\def\@author{}
\def\@address{}

% Enable line numbering

\linenumbers

\fi

% Conditional formatting for accept option
\ifaccept

\fi


\long\def\pprintMaketitle{\clearpage
  \iflongmktitle\if@twocolumn\let\columnwidth=\textwidth\fi\fi
  \resetTitleCounters
  \def\baselinestretch{1}%
  \printFirstPageNotes
 \begin{center}%
 \thispagestyle{printTitle}%
   \def\baselinestretch{1}%
   \ifsubmit
   \nolinenumbers{\vspace*{-3.8em}\small\href{http://dx.doi.org/\@doi}{\@journalabbr,
 \ifx\@vol\@empty\else\@vol\fi, \ifx\@pages\@empty\else\@pages\fi}}
\else
{\vspace*{-3.8em}\small\href{http://dx.doi.org/\@doi}{\@journalabbr,
		\ifx\@vol\@empty\else\@vol\fi, \ifx\@pages\@empty\else\@pages\fi}}
\fi
\vskip  45pt
\begin{picture}(100,100)
\put(-215,57){\includegraphics[width=\textwidth]{resources/\@shortjid.jpg}}
\ifJMCS
\put(6,133){\scriptsize	 \textcolor{mycol}{Online:} ISSN \@issn}
\fi
\ifMNS
% No ISSN needed, 
\fi
\ifJNSA
\put(21,133){\scriptsize \textcolor{mycol}{ISSN:} 2008-1898}
\fi
\put(-45,68){\scriptsize	 \textcolor{mycol}{Journal Homepage: www.isr-publications.com/\@shortjid}}
\end{picture}
\end{center}
\vspace{-2cm}
     \begin{flushleft}%
	\begin{minipage}{14cm}
		\Large{\bf{\@title}}
	\end{minipage}
	\par\vskip18pt\sf
	\normalsize\elsauthors\par\vskip10pt
	\footnotesize\itshape\elsaddress\par\vskip20pt
	\rule{18cm}{.1pt}\vskip12pt
	\ifvoid\absbox\else\unvbox\absbox\par\vskip10pt\fi
	\ifvoid\keybox\else\unvbox\keybox\par\vskip10pt\fi
\end{flushleft}\vspace{-20pt}
\begin{flushright}%
\ifsubmit	
\nolinenumbers	\footnotesize \copyright \@copyrightyear\ All rights reserved.
\else
	\footnotesize \copyright \@copyrightyear\ All rights reserved.
\fi
\end{flushright}\vskip-1.6em
\ifsubmit	
{\nolinenumbers{\rule{18cm}{.1pt}\vskip12pt}}
\else
{\rule{18cm}{.1pt}\vskip12pt}
\fi
\gdef\thefootnote{\arabic{footnote}}%
}

\def\printWarning{%
     \mbox{}\par\vfill\par\bgroup
     \fboxsep12pt\fboxrule1pt
     \hspace*{.18\textwidth}
     \fcolorbox{gray50}{gray10}{\box\warnbox}
     \egroup\par\vfill\thispagestyle{empty}
     \setcounter{page}{0}
     \clearpage}

\long\def\finalMaketitle{%
  \resetTitleCounters
  \def\baselinestretch{1}%
   \MaketitleBox
   \thispagestyle{pprintTitle}%
  \gdef\thefootnote{\arabic{footnote}}%
  }

\long\def\MaketitleBox{%
  \resetTitleCounters
  \def\baselinestretch{1}%
  \begin{center}%
   \def\baselinestretch{1}%
    \Large\@title\par\vskip18pt
    \normalsize\elsauthors\par\vskip10pt
    \footnotesize\itshape\elsaddress\par\vskip36pt
    \hrule\vskip12pt
    \ifvoid\absbox\else\unvbox\absbox\par\vskip10pt\fi
    \ifvoid\keybox\else\unvbox\keybox\par\vskip10pt\fi
    \hrule\vskip12pt
    \end{center}%
  }

\def\FNtext#1{\par\bgroup\footnotesize#1\egroup}
\newdimen\space@left
\def\alarm#1{\typeout{******************************}%
             \typeout{#1}%
             \typeout{******************************}%
}
\long\def\getSpaceLeft{%\global\@twocolumnfalse%
   \global\setbox0=\vbox{\hsize=\textwidth\MaketitleBox}%
   \global\setbox1=\vbox{\hsize=\textwidth
    \let\footnotetext\FNtext
    \printFirstPageNotes}%
    \xdef\noteheight{\the\ht1}%
    \xdef\titleheight{\the\ht0}%
    \@tempdima=\vsize
    \advance\@tempdima-\noteheight
    \advance\@tempdima-1\baselineskip
}

  \skip\footins=24pt

\newbox\els@boxa
\newbox\els@boxb

\ifpreprint
  \def\maketitle{\pprintMaketitle}
  \else
   \ifnum\jtype=1
    \def\maketitle{%
      \iflongmktitle\getSpaceLeft
       \global\setbox\els@boxa=\vsplit0 to \@tempdima
       \box\els@boxa\par\resetTitleCounters
       \thispagestyle{pprintTitle}%
       \printFirstPageNotes
       \box0%
      \else
       \finalMaketitle\printFirstPageNotes
      \fi
    \gdef\thefootnote{\arabic{footnote}}}%
  \else
 \ifnum\jtype=5
    \def\maketitle{%
      \iflongmktitle\getSpaceLeft
       \global\setbox\els@boxa=\vsplit0 to \@tempdima
       \box\els@boxa\par\resetTitleCounters
       \thispagestyle{pprintTitle}%
       \printFirstPageNotes
       \twocolumn[\box0]%\printFirstPageNotes
      \else
       \twocolumn[\finalMaketitle]\printFirstPageNotes
     \fi
     \gdef\thefootnote{\arabic{footnote}}}
  \else
  \if@twocolumn
    \def\maketitle{%
      \iflongmktitle\getSpaceLeft
       \global\setbox\els@boxa=\vsplit0 to \@tempdima
       \box\els@boxa\par\resetTitleCounters
       \thispagestyle{pprintTitle}%
       \printFirstPageNotes
       \twocolumn[\box0]%
      \else
       \twocolumn[\finalMaketitle]\printFirstPageNotes
      \fi
     \gdef\thefootnote{\arabic{footnote}}}%
   \else
    \def\maketitle{%
      \iflongmktitle\getSpaceLeft
       \global\setbox\els@boxa=\vsplit0 to \@tempdima
       \box\els@boxa\par\resetTitleCounters
       \thispagestyle{pprintTitle}%
       \printFirstPageNotes
       \box0%
     \else
       \finalMaketitle\printFirstPageNotes
      \fi
    \gdef\thefootnote{\arabic{footnote}}}%
   \fi
  \fi
 \fi
\fi
\def\ps@pprintTitle{%
     \let\@oddhead\@empty
     \let\@evenhead\@empty
     \def\@oddfoot{\footnotesize\itshape
       Preprint submitted to \ifx\@journal\@empty Elsevier
       \else\@journal\fi\hfill\today}%
     \let\@evenfoot\@oddfoot}
\def\@seccntDot{.}
\def\@seccntformat#1{\csname the#1\endcsname\@seccntDot\hskip 0.5em}

\renewcommand\section{\@startsection {section}{1}{\z@}%
           {18\p@ \@plus 6\p@ \@minus 3\p@}%
           {9\p@ \@plus 6\p@ \@minus 3\p@}%
           {\normalsize\bfseries\boldmath}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
           {12\p@ \@plus 6\p@ \@minus 3\p@}%
           {3\p@ \@plus 6\p@ \@minus 3\p@}%
           {\normalfont\normalsize\itshape}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
           {12\p@ \@plus 6\p@ \@minus 3\p@}%
           {\p@}%
           {\normalfont\normalsize\itshape}}

\def\paragraph{\secdef{\els@aparagraph}{\els@bparagraph}}
\def\els@aparagraph[#1]#2{\elsparagraph[#1]{#2.}}
\def\els@bparagraph#1{\elsparagraph*{#1.}}

\newcommand\elsparagraph{\@startsection{paragraph}{4}{0\z@}%
           {10\p@ \@plus 6\p@ \@minus 3\p@}%
           {-6\p@}%
           {\normalfont\itshape}}
\newdimen\leftMargin
\leftMargin=2em
\newtoks\@enLab  %\newtoks\@enfont
\def\@enQmark{?}
\def\@enLabel#1#2{%
  \edef\@enThe{\noexpand#1{\@enumctr}}%
  \@enLab\expandafter{\the\@enLab\csname the\@enumctr\endcsname}%
  \@enloop}
\def\@enSpace{\afterassignment\@enSp@ce\let\@tempa= }
\def\@enSp@ce{\@enLab\expandafter{\the\@enLab\space}\@enloop}
\def\@enGroup#1{\@enLab\expandafter{\the\@enLab{#1}}\@enloop}
\def\@enOther#1{\@enLab\expandafter{\the\@enLab#1}\@enloop}
\def\@enloop{\futurelet\@entemp\@enloop@}
\def\@enloop@{%
  \ifx A\@entemp         \def\@tempa{\@enLabel\Alph  }\else
  \ifx a\@entemp         \def\@tempa{\@enLabel\alph  }\else
  \ifx i\@entemp         \def\@tempa{\@enLabel\roman }\else
  \ifx I\@entemp         \def\@tempa{\@enLabel\Roman }\else
  \ifx 1\@entemp         \def\@tempa{\@enLabel\arabic}\else
  \ifx \@sptoken\@entemp \let\@tempa\@enSpace         \else
  \ifx \bgroup\@entemp   \let\@tempa\@enGroup         \else
  \ifx \@enum@\@entemp   \let\@tempa\@gobble          \else
                         \let\@tempa\@enOther
             \fi\fi\fi\fi\fi\fi\fi\fi
  \@tempa}
\newlength{\@sep} \newlength{\@@sep}
\setlength{\@sep}{.5\baselineskip plus.2\baselineskip
            minus.2\baselineskip}
\setlength{\@@sep}{.1\baselineskip plus.01\baselineskip
            minus.05\baselineskip}
\providecommand{\sfbc}{\rmfamily\upshape}
\providecommand{\sfn}{\rmfamily\upshape}
\def\@enfont{\ifnum \@enumdepth >1\let\@nxt\sfn \else\let\@nxt\sfbc \fi\@nxt}
\def\enumerate{%
   \ifnum \@enumdepth >3 \@toodeep\else
      \advance\@enumdepth \@ne
      \edef\@enumctr{enum\romannumeral\the\@enumdepth}\fi
   \@ifnextchar[{\@@enum@}{\@enum@}}
\def\@@enum@[#1]{%
  \@enLab{}\let\@enThe\@enQmark
  \@enloop#1\@enum@
  \ifx\@enThe\@enQmark\@warning{The counter will not be printed.%
   ^^J\space\@spaces\@spaces\@spaces The label is: \the\@enLab}\fi
  \expandafter\edef\csname label\@enumctr\endcsname{\the\@enLab}%
  \expandafter\let\csname the\@enumctr\endcsname\@enThe
  \csname c@\@enumctr\endcsname7
  \expandafter\settowidth
            \csname leftmargin\romannumeral\@enumdepth\endcsname
            {\the\@enLab\hskip\labelsep}%
  \@enum@}
\def\@enum@{\list{{\@enfont\csname label\@enumctr\endcsname}}%
           {\usecounter{\@enumctr}\def\makelabel##1{\hss\llap{##1}}%
     \ifnum \@enumdepth>1\setlength{\topsep}{\@@sep}\else
           \setlength{\topsep}{\@sep}\fi
     \ifnum \@enumdepth>1\setlength{\itemsep}{0pt plus1pt minus1pt}%
      \else \setlength{\itemsep}{\@@sep}\fi
     %\setlength\leftmargin{\leftMargin}%%%{1.8em}
     \setlength{\parsep}{0pt plus1pt minus1pt}%
     \setlength{\parskip}{0pt plus1pt minus1pt}
                   }}

\def\endenumerate{\par\ifnum \@enumdepth >1\addvspace{\@@sep}\else
           \addvspace{\@sep}\fi \endlist}

\def\sitem{\@noitemargtrue\@item[\@itemlabel *]}

\def\itemize{\@ifnextchar[{\@Itemize}{\@Itemize[]}}

\def\@Itemize[#1]{\def\next{#1}%
  \ifnum \@itemdepth >\thr@@\@toodeep\else
   \advance\@itemdepth\@ne
  \ifx\next\@empty\else\expandafter\def\csname
   labelitem\romannumeral\the\@itemdepth\endcsname{#1}\fi%
  \edef\@itemitem{labelitem\romannumeral\the\@itemdepth}%
  \expandafter\list\csname\@itemitem\endcsname
  {\def\makelabel##1{\hss\llap{##1}}}%
 \fi}
\def\newdefinition#1{%
  \@ifnextchar[{\@odfn{#1}}{\@ndfn{#1}}}%]
\def\@ndfn#1#2{%
  \@ifnextchar[{\@xndfn{#1}{#2}}{\@yndfn{#1}{#2}}}
\def\@xndfn#1#2[#3]{%
  \expandafter\@ifdefinable\csname #1\endcsname
    {\@definecounter{#1}\@newctr{#1}[#3]%
     \expandafter\xdef\csname the#1\endcsname{%
       \expandafter\noexpand\csname the#3\endcsname \@dfncountersep
          \@dfncounter{#1}}%
     \global\@namedef{#1}{\@dfn{#1}{#2}}%
     \global\@namedef{end#1}{\@enddefinition}}}
\def\@yndfn#1#2{%
  \expandafter\@ifdefinable\csname #1\endcsname
    {\@definecounter{#1}%
     \expandafter\xdef\csname the#1\endcsname{\@dfncounter{#1}}%
     \global\@namedef{#1}{\@dfn{#1}{#2}}%
     \global\@namedef{end#1}{\@enddefinition}}}
\def\@odfn#1[#2]#3{%
  \@ifundefined{c@#2}{\@nocounterr{#2}}%
    {\expandafter\@ifdefinable\csname #1\endcsname
    {\global\@namedef{the#1}{\@nameuse{the#2}}
  \global\@namedef{#1}{\@dfn{#2}{#3}}%
  \global\@namedef{end#1}{\@enddefinition}}}}
\def\@dfn#1#2{%
  \refstepcounter{#1}%
  \@ifnextchar[{\@ydfn{#1}{#2}}{\@xdfn{#1}{#2}}}
\def\@xdfn#1#2{%
  \@begindefinition{#2}{\csname the#1\endcsname}\ignorespaces}
\def\@ydfn#1#2[#3]{%
  \@opargbegindefinition{#2}{\csname the#1\endcsname}{#3}\ignorespaces}
\def\@dfncounter#1{\noexpand\arabic{#1}}
\def\@dfncountersep{.}
\def\@begindefinition#1#2{\trivlist
   \item[\hskip\labelsep{\bfseries #1\ #2.}]\upshape}
\def\@opargbegindefinition#1#2#3{\trivlist
      \item[\hskip\labelsep{\bfseries #1\ #2\ (#3).}]\upshape}
\def\@enddefinition{\endtrivlist}

\def\@begintheorem#1#2{\trivlist
  \let\baselinestretch\@blstr
   \item[\hskip \labelsep{\bfseries #1\ #2.}]\itshape}
\def\@opargbegintheorem#1#2#3{\trivlist
  \let\baselinestretch\@blstr
      \item[\hskip \labelsep{\bfseries #1\ #2\ (#3).}]\itshape}

\def\newproof#1{%
  \@ifnextchar[{\@oprf{#1}}{\@nprf{#1}}}
\def\@nprf#1#2{%
  \@ifnextchar[{\@xnprf{#1}{#2}}{\@ynprf{#1}{#2}}}
\def\@xnprf#1#2[#3]{%
  \expandafter\@ifdefinable\csname #1\endcsname
    {\@definecounter{#1}\@newctr{#1}[#3]%
     \expandafter\xdef\csname the#1\endcsname{%
       \expandafter\noexpand\csname the#3\endcsname \@prfcountersep
          \@prfcounter{#1}}%
     \global\@namedef{#1}{\@prf{#1}{#2}}%
     \global\@namedef{end#1}{\@endproof}}}
\def\@ynprf#1#2{%
  \expandafter\@ifdefinable\csname #1\endcsname
    {\@definecounter{#1}%
     \expandafter\xdef\csname the#1\endcsname{\@prfcounter{#1}}%
     \global\@namedef{#1}{\@prf{#1}{#2}}%
     \global\@namedef{end#1}{\@endproof}}}
\def\@oprf#1[#2]#3{%
  \@ifundefined{c@#2}{\@nocounterr{#2}}%
    {\expandafter\@ifdefinable\csname #1\endcsname
    {\global\@namedef{the#1}{\@nameuse{the#2}}%
  \global\@namedef{#1}{\@prf{#2}{#3}}%
  \global\@namedef{end#1}{\@endproof}}}}
\def\@prf#1#2{%
  \refstepcounter{#1}%
  \@ifnextchar[{\@yprf{#1}{#2}}{\@xprf{#1}{#2}}}
\def\@xprf#1#2{%
  \@beginproof{#2}{\csname the#1\endcsname}\ignorespaces}
\def\@yprf#1#2[#3]{%
  \@opargbeginproof{#2}{\csname the#1\endcsname}{#3}\ignorespaces}
\def\@prfcounter#1{\noexpand\arabic{#1}}
\def\@prfcountersep{.}
\def\@beginproof#1#2{\trivlist\let\baselinestretch\@blstr
   \item[\hskip \labelsep{\scshape #1.}]\rmfamily}
\def\@opargbeginproof#1#2#3{\trivlist\let\baselinestretch\@blstr
      \item[\hskip \labelsep{\scshape #1\ (#3).}]\rmfamily}
\def\@endproof{\endtrivlist}
\newcommand*{\qed}{\hbox{}\hfill$\Box$}

\@ifundefined{@biboptions}{\xdef\@biboptions{numbers}}{}
\InputIfFileExists{\jobname.spl}{}{}
\RequirePackage[\@biboptions]{natbib}

\newwrite\splwrite
\immediate\openout\splwrite=\jobname.spl
\def\biboptions#1{\def\next{#1}\immediate\write\splwrite{%
   \string\g@addto@macro\string\@biboptions{%
    ,\expandafter\strip@prefix\meaning\next}}}

\let\baselinestretch=\@blstr
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\def\lhead{\@ifnextchar[{\@xlhead}{\@ylhead}}
\def\@xlhead[#1]#2{\gdef\@elhead{#1}\gdef\@olhead{#2}}
\def\@ylhead#1{\gdef\@elhead{#1}\gdef\@olhead{#1}}

\def\chead{\@ifnextchar[{\@xchead}{\@ychead}}
\def\@xchead[#1]#2{\gdef\@echead{#1}\gdef\@ochead{#2}}
\def\@ychead#1{\gdef\@echead{#1}\gdef\@ochead{#1}}

\def\rhead{\@ifnextchar[{\@xrhead}{\@yrhead}}
\def\@xrhead[#1]#2{\gdef\@erhead{#1}\gdef\@orhead{#2}}
\def\@yrhead#1{\gdef\@erhead{#1}\gdef\@orhead{#1}}

\def\lfoot{\@ifnextchar[{\@xlfoot}{\@ylfoot}}
\def\@xlfoot[#1]#2{\gdef\@elfoot{#1}\gdef\@olfoot{#2}}
\def\@ylfoot#1{\gdef\@elfoot{#1}\gdef\@olfoot{#1}}

\def\cfoot{\@ifnextchar[{\@xcfoot}{\@ycfoot}}
\def\@xcfoot[#1]#2{\gdef\@ecfoot{#1}\gdef\@ocfoot{#2}}
\def\@ycfoot#1{\gdef\@ecfoot{#1}\gdef\@ocfoot{#1}}

\def\rfoot{\@ifnextchar[{\@xrfoot}{\@yrfoot}}
\def\@xrfoot[#1]#2{\gdef\@erfoot{#1}\gdef\@orfoot{#2}}
\def\@yrfoot#1{\gdef\@erfoot{#1}\gdef\@orfoot{#1}}

\newdimen\headrulewidth
\newdimen\footrulewidth
\newdimen\plainheadrulewidth
\newdimen\plainfootrulewidth
\newdimen\headwidth

\newif\if@fancyplain \@fancyplainfalse
\def\fancyplain#1#2{\if@fancyplain#1\else#2\fi}

% Initialization of the head and foot text.

\headrulewidth  1pt
\footrulewidth\z@
\plainheadrulewidth\z@
\plainfootrulewidth\z@


\lhead[\fancyplain{}{\sl\rightmark}]{\fancyplain{}{\sl\leftmark}}
%  i.e. empty on ``plain'' pages \rightmark on even, \leftmark on odd pages
\chead{}
\rhead[\fancyplain{}{\sl\leftmark}]{\fancyplain{}{\sl\rightmark}}
%  i.e. empty on ``plain'' pages \leftmark on even, \rightmark on odd pages
\lfoot{}
\cfoot{}
\rfoot{}

% Put together a header or footer given the left, center and
% right text, fillers at left and right and a rule.
% The \lap commands put the text into an hbox of zero size,
% so overlapping text does not generate an errormessage.

\def\@fancyhead#1#2#3#4#5{#1\hbox to \headwidth{\vbox{\hbox
{\rlap{\parbox[b]{\headwidth}{\raggedright#2\strut}}\hfill
\parbox[b]{\headwidth}{\centering#3\strut}\hfill
\llap{\parbox[b]{\headwidth}{\raggedleft#4\strut}}}\headrule}}#5}


\def\@fancyfoot#1#2#3#4#5{#1\hbox to\headwidth{\vbox{\footrule
\hbox{\rlap{\parbox[t]{\headwidth}{\raggedright#2\strut}}\hfill
\parbox[t]{\headwidth}{\centering#3\strut}\hfill
\llap{\parbox[t]{\headwidth}{\raggedleft#4\strut}}}}}#5}

\def\headrule{{\color{blue}\if@fancyplain\headrulewidth\plainheadrulewidth\fi
\hrule\@height\headrulewidth\@width\headwidth \vskip-\headrulewidth}}

\def\footrule{{\if@fancyplain\footrulewidth\plainfootrulewidth\fi
\vskip-0.3\normalbaselineskip\vskip-\footrulewidth
\hrule\@width\headwidth\@height\footrulewidth\vskip0.3\normalbaselineskip}}

\def\ps@fancy{
\let\@mkboth\markboth
\@ifundefined{chapter}{\def\sectionmark##1{\markboth
{\uppercase{\ifnum \c@secnumdepth>\z@
 \thesection\hskip 1em\relax \fi ##1}}{}}
\def\subsectionmark##1{\markright {\ifnum \c@secnumdepth >\@ne
 \thesubsection\hskip 1em\relax \fi ##1}}}
{\def\chaptermark##1{\markboth {\uppercase{\ifnum \c@secnumdepth>\m@ne
 \@chapapp\ \thechapter \ \fi ##1}}{}}
\def\sectionmark##1{\markright{\uppercase{\ifnum \c@secnumdepth >\z@
 \thesection \ \fi ##1}}}}
\def\@oddhead{\@fancyhead\relax\@olhead\@ochead\@orhead\hss}
\def\@oddfoot{\@fancyfoot\relax\@olfoot\@ocfoot\@orfoot\hss}
\def\@evenhead{\@fancyhead\hss\@elhead\@echead\@erhead\relax}
\def\@evenfoot{\@fancyfoot\hss\@elfoot\@ecfoot\@erfoot\relax}
\headwidth\textwidth}
\def\ps@fancyplain{\ps@fancy \let\ps@plain\ps@plain@fancy}
\def\ps@plain@fancy{\@fancyplaintrue\ps@fancy}


\pagestyle{fancy}
\headwidth 180mm
\rhead{\rm \thepage}
\lhead{\ifx\@authors\@empty\else\@authors\fi,
             \@journalabbr, \ifx\@vol\@empty\else\@vol\fi,
             \ifx\@pages\@empty\else\@pages\fi}
%---------------------------------------------------------------------------------------------------------



\RequirePackage{geometry}
\geometry{
	paperwidth=210mm,
	paperheight=297mm,
	textheight=240mm,
	textwidth=180mm,
	centering,
	headheight=40mm,
	headsep=5mm,
	footskip=18pt,
	footnotesep=24pt plus 2pt minus 12pt,
}%
\global\let\bibfont=\footnotesize
\global\bibsep=0pt
\input{fleqn.clo}







%%%%%%%%%%%%%%%%%%%%%




\def\journal#1{\gdef\@journal{#1}}
 \let\@journal\@empty
\newenvironment{frontmatter}{}{\maketitle}

\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip\footnotesize
  \sbox\@tempboxa{#1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    #1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}

\AtBeginDocument{\@ifpackageloaded{hyperref}
  {\def\@linkcolor{blue}
   \def\@anchorcolor{blue}
   \def\@citecolor{blue}
   \def\@filecolor{blue}
   \def\@urlcolor{blue}
   \def\@menucolor{blue}
   \def\@pagecolor{blue}
\begingroup
  \@makeother\`%
  \@makeother\=%
  \edef\x{%
    \edef\noexpand\x{%
      \endgroup
      \noexpand\toks@{%
        \catcode 96=\noexpand\the\catcode`\noexpand\`\relax
        \catcode 61=\noexpand\the\catcode`\noexpand\=\relax
      }%
    }%
    \noexpand\x
  }%
\x
\@makeother\`
\@makeother\=
}{}}
%%
\renewcommand\appendix{\par
  \setcounter{section}{0}%
  \setcounter{subsection}{0}%
  \setcounter{equation}{0}
  \gdef\thefigure{\@Alph\c@section.\arabic{figure}}%
  \gdef\thetable{\@Alph\c@section.\arabic{table}}%
  \gdef\thesection{\appendixname\@Alph\c@section}%
  \@addtoreset{equation}{section}%
  \gdef\theequation{\@Alph\c@section.\arabic{equation}}%
}
\def\appendixname{Appendix}

%% Added for work with amsrefs.sty

\@ifpackageloaded{amsrefs}%
  {}
  {%\let\bibsection\relax%
  \AtBeginDocument{\def\cites@b#1#2,#3{%
    \begingroup[%
        \toks@{\InnerCite{#2}#1}%
        \ifx\@empty#3\@xp\@gobble\fi
        \cites@c#3%
}}}
%%


\endinput
%%
%% End of file `ISRP.cls'.
