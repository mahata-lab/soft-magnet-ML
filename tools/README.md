# tools

`build_manuscript_v3.py` assembles the Word manuscript from the v2 source document
plus the v3 results, preserving the Zotero citation fields byte-identically.

It has a hard-coded input path near the top:

```python
SRC_DOC = Path('/mnt/user-data/uploads/soft-magnets/paper/Summer Paper.docx')
```

Point `SRC_DOC` at your own copy of the source document before running it. The
script is included for provenance — it documents exactly how the manuscript was
produced — not because it runs unmodified.

Note: the manuscript's nine equation blocks are native Word OMML. LibreOffice does
not import OMML, so they appear blank in a LibreOffice-generated PDF. They render
correctly in Word.
