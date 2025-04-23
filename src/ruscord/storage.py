from django.core.files.storage import FileSystemStorage
import time


class OverwriteStorage(FileSystemStorage):
    """
    Возвращает то же имя для существующего файла и удаляет существующий файл при сохранении.
    """

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super()._save(name, content)

    def get_available_name(self, name, max_length=None):
        """
        Возвращает имя файла без изменений, учитывая max_length.
        """
        if max_length and len(name) > max_length:
            name = name[:max_length]
        return name
