import importlib.util
import shutil
import sys


# 列出 PDF 工作流會用到的命令列工具與 Python 套件，並對缺少項目給出替代方式。
# 僅使用標準函式庫，所以在沒有任何第三方套件的 python3 下也能執行。

COMMANDS = {
    "pdftotext": "文字提取（brew install poppler）",
    "pdftoppm": "頁面轉圖片（brew install poppler）",
    "pdfimages": "抽取內嵌圖片（brew install poppler）",
    "qpdf": "合併、分割、修復（brew install qpdf）；缺少時改用 pypdf",
    "tesseract": "OCR 引擎（brew install tesseract）",
    "ocrmypdf": "掃描件轉可搜尋 PDF（brew install ocrmypdf）；缺少時改用 pdftoppm 加 tesseract",
}

MODULES = {
    "pypdf": "pypdf",
    "pdfplumber": "pdfplumber",
    "pypdfium2": "pypdfium2",
    "pdf2image": "pdf2image",
    "PIL": "pillow",
    "reportlab": "reportlab",
    "pytesseract": "pytesseract",
}


def main():
    print(f"python: {sys.executable} ({sys.version.split()[0]})")
    print()
    print("命令列工具")
    for name, note in COMMANDS.items():
        path = shutil.which(name)
        print(f"  {'OK     ' if path else 'MISSING'} {name:<10} {path or note}")

    print()
    print("Python 套件")
    missing = []
    for module, package in MODULES.items():
        found = importlib.util.find_spec(module) is not None
        print(f"  {'OK     ' if found else 'MISSING'} {package}")
        if not found:
            missing.append(package)

    if missing:
        withs = " ".join(f"--with {p}" for p in missing)
        print()
        print("缺少的套件可用 uv 臨時帶入，例如：")
        print(f"  uv run {withs} python3 scripts/<script>.py <args>")


if __name__ == "__main__":
    main()
