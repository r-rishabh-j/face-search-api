import os
from PIL import Image
import zipfile


class FileManager():
    """
    Used to save images and extract zip file
    """
    def __init__(self, static_path, temp = './__tmp'):
        self.__root = static_path
        self.__temp = temp

    def __getNextDirPath(self):
        i = 1
        while os.path.exists(self.__root+'/'+str(i)):
            i += 1
        return f'{self.__root}/{i}/'

    def saveImage(self, image):
        '''
        Save images
        '''
        img = Image.open(image)
        img.verify()
        img = Image.open(image)
        dir_name = self.__getNextDirPath()
        os.mkdir(dir_name)
        file_path = dir_name+str(os.path.basename(image.filename))
        img.save(file_path)
        img.close()
        return os.path.abspath(file_path)

    def saveImagesFromZip(self, zip_file):
        """
        Save images from zip
        """
        path = self.__getNextDirPath()
        assert zipfile.is_zipfile(zip_file)
        zip_file = zipfile.ZipFile(zip_file)
        zip_file.extractall(path)
        image_paths = []
        total_images = 0
        for root_dir in os.scandir(path):
            if root_dir.is_dir():
                for f1 in os.scandir(root_dir):
                    if f1.is_file():
                        total_images+=1
                        image_paths.append((root_dir.name, os.path.abspath(f1)))
                    elif f1.is_dir():
                        for f2 in os.scandir(f1):
                            total_images+=1
                            image_paths.append((f1.name, os.path.abspath(f2)))
        return image_paths, total_images, path