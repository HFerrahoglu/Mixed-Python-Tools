import os
import shutil
import ctypes
from tkinter import Tk
from tkinter.filedialog import askdirectory


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def delete_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"'{folder_path}' bulunamadı.")
        return
    try:
        shutil.rmtree(folder_path)
        print(f"'{folder_path}' başarıyla silindi.")
    except PermissionError:
        print(f"'{folder_path}' silinirken yetki hatası oluştu.")
    except Exception as e:
        print(f"'{folder_path}' silinirken bir hata oluştu: {e}")


if __name__ == "__main__":
    if not is_admin():
        print("Bu scripti yönetici olarak çalıştırmalısınız!")
    else:
        Tk().withdraw()

        print("Silmek istediğiniz klasörü seçmek için File Explorer açılacak.")
        selected_folder = askdirectory(title="Silinecek Klasörü Seçin")

        if selected_folder:
            print(f"Seçilen klasör: {selected_folder}")
            delete_folder(selected_folder)
        else:
            print("Hiçbir klasör seçilmedi.")
