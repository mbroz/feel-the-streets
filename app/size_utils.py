from PySide2.QtCore import QLocale

def format_size(num_bytes):
    return QLocale().formattedDataSize(num_bytes)