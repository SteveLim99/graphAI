import os


def deleteTemporaryFiles(upload, download, fileName):
    upload_path = upload + fileName
    download_path = download + fileName

    if os.path.exists(upload_path + "_input.png"):
        os.remove(upload_path + "_input.png")

    if os.path.exists(download_path + "_arr.png"):
        os.remove(download_path + "_arr.png")
        
    if os.path.exists(download_path + "_ent.png"):
        os.remove(download_path + "_ent.png")
    
    if os.path.exists(download_path + "_nx.png"):
        os.remove(download_path + "_nx.png")

    if os.path.exists(download_path + "_nx.gml"):
        os.remove(download_path + "_nx.gml")

    if os.path.exists(download_path + ".csv"):
        os.remove(download_path + ".csv")
