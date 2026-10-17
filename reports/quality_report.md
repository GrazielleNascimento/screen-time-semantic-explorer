# Quality Report

- Generated at: 2026-10-16 17:27:20
- Collection: `screen_time_children`
- Embedding model: all-MiniLM-L6-v2 (ONNX, ChromaDB default)
- Isolation Forest: contamination=0.03, n_estimators=200, random_state=42

## Before cleaning

- Total chunks: 6069
- Anomalous chunks: 183 (3.02%)
- Scores (min / median / max): -0.4941 / -0.4372 / -0.4022

## Most anomalous chunks (top 15)

Lower score = more anomalous.

| id | PDF | chunk_idx | score | text |
| --- | --- | --- | --- | --- |
| PMC13540691_41 | PMC13540691.pdf | 41 | -0.4941 | a, Chuuk, Yap, Kosrae, Pohnpei, Ponape, Fiji, French Polynesia, Guam, Kiribati, Nauru, New Caledonia, Niue, Commonwealth of the Northern Mariana Islan |
| PMC13587508_106 | PMC13587508.pdf | 106 | -0.4893 | epackage{wasysym} \usepackage{amsfonts} \usepackage{amssymb} \usepackage{amsbsy} \usepackage{mathrsfs} \usepackage{upgreek} \setlength{\oddsidemargin} |
| PMC13584371_162 | PMC13584371.pdf | 162 | -0.4870 | s Thomas the Tank Engine SpongeBob SquarePants Dora the Explorer 2 Hi-5 Bob the Builder The Wiggles Little Einsteins 3 Mickey Mouse Clubhouse Blue’s C |
| PMC13590006_198 | PMC13590006.pdf | 198 | -0.4856 | 12. A Spearman correlation heatmap with labeled rows and columns and numeric coefficients in cells. Figure 4 visually synthesizes our final model, dis |
| PMC13532691_130 | PMC13532691.pdf | 130 | -0.4854 | uration of time; for example, “any desktop ” (8784/12,628, 69.6%) had fair agreement (PABAK: 0.391), and “any handheld gaming console” (6314/11,705, 5 |
| PMC13587429_77 | PMC13587429.pdf | 77 | -0.4800 | , and by verifying that imputed values fell within realistic ranges. In addition, convergence of the imputation algorithm was assessed by inspecting t |
| PMC13561401_87 | PMC13561401.pdf | 87 | -0.4790 | cleaning. For participants with more than 7 consecutive complete days available, we selected the first 7 days from the first qualifying consecutive se |
| PMC13571863_114 | PMC13571863.pdf | 114 | -0.4787 | s typically lacked explicit operational definitions and predated the DSM-5 reorganization, limiting direct comparability. Given that DICCD in this sam |
| PMC13532691_84 | PMC13532691.pdf | 84 | -0.4785 | logical order. To gain an understanding of the context, coders were encouraged to watch several video frames prior to coding. The coder would first de |
| PMC13570809_103 | PMC13570809.pdf | 103 | -0.4784 | bstitute■versus■support distinction outlined above defines the boundary conditions under which the model's general trade■off is more or less likely to |
| PMC13540691_219 | PMC13540691.pdf | 219 | -0.4781 | eening and reviewing, contributed to writing the manuscript, and reviewed and approved the final manuscript. Fiorenzo Toncan screened studies and comp |
| PMC13559115_34 | PMC13559115.pdf | 34 | -0.4778 | getables, legumes and nuts and is considered a central component of a healthy diet due to positive effects on metabolic and cardiovascular health para |
| PMC13540691_28 | PMC13540691.pdf | 28 | -0.4777 | a, Niue, Pitcairn Islands, Samoa, Tokelau, Tonga, Tuvalu, Wallis and Futuna), Micronesia (Commonwealth of the Northern Mariana Islands (CNMI), Federat |
| PMC13540691_44 | PMC13540691.pdf | 44 | -0.4777 | H, Scopus, SPORTDiscus. Backward and forward citation chasing on included articles from the initial English search was executed in September 2024 usin |
| PMC13567359_95 | PMC13567359.pdf | 95 | -0.4775 | rticipate, and duplicate project registrations were removed using the email address as the reference identifier. However, repeated email addresses in |

## Anomalies per PDF

| PDF | anomalous chunks |
| --- | --- |
| PMC13540691.pdf | 18 |
| PMC13590006.pdf | 15 |
| PMC13591200.pdf | 15 |
| PMC13532691.pdf | 14 |
| PMC13540923.pdf | 11 |
| PMC13599830.pdf | 11 |
| PMC13576209.pdf | 9 |
| PMC13587429.pdf | 9 |
| PMC13561401.pdf | 8 |
| PMC13570809.pdf | 8 |
| PMC13551982.pdf | 6 |
| PMC13560222.pdf | 6 |
| PMC13569844.pdf | 6 |
| PMC13571863.pdf | 6 |
| PMC13584371.pdf | 6 |
| PMC13587508.pdf | 6 |
| PMC13544660.pdf | 5 |
| PMC13559115.pdf | 5 |
| PMC13567359.pdf | 5 |
| PMC13573580.pdf | 4 |
| PMC13555211.pdf | 3 |
| PMC13571864.pdf | 2 |
| PMC13574985.pdf | 2 |
| PMC13589181.pdf | 2 |
| PMC13585841.pdf | 1 |

## After cleaning

- Chunks remaining: 5886
- Chunks removed: 183
- Scores (min / median / max): -0.4630 / -0.4368 / -0.4022 (original scores of the remaining chunks, not recomputed)
- Database updated: yes (anomalous chunks deleted from the collection).

## Curation note

Not every flagged chunk is garbage: a short but legitimate passage can be flagged, and some noise can slip through. Review the table above before trusting the removal.
