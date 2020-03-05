from rank import generate_summary
from feature import testText
from feature import extract_text_from_pdf
generate_summary("storytor.pdf")
texta = extract_text_from_pdf('storytor.pdf')
textt = "the invisible man"
summ = testText(textt,texta)
print("\n[Summarized text from Feature Based:]\n")
print(summ)
