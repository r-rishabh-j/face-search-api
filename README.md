# face-search

## Description
The program is an image search API implemented using flask and face_recognition python API. Users
can upload ZIP files or images into the database, and later give a sample image and find its
matches in the database.
## Usage
First, using the face_recognition API, an image encoding is saved into the database to optimize
storage space and search. The user can then query an image. An encoding for this image will
be generated, which will then be compared with the database encodings with a given
confidence value. The top-K matches will be returned to the user.

## Directory structure:
```
├── api/
│   ├── __init__.py
│   ├── face_processing.py
│   ├── file_manager.py
│   ├── heap.py
│   └── models.py
├── main.py
├── requirements.txt
├── static/
├── templates/
│   ├── get_face_info.html
│   ├── home.html
│   ├── search_faces.html
│   ├── set_face_info.html
│   ├── show_results.html
│   ├── upload_image.html
│   └── upload_zip.html
├── testing_articles/
├── testzip.zip
└── unit_test.py
```

## API endpoints

Description of routes:
1. ```'/'```:   
This is the route to access html template to use the API interactively.

2. ```‘/add_face’```:   
Route to upload an image. User needs to upload an image and a
name of the person through a POST request. If the face-recognition library does not detect a face, the image is simply ignored.   

    Input JSON format:
    ```
    {  
        ‘file’: <FileObject>,   
        ‘name’: <PersonNameAsText>  
    }
    ```
 

3. ```‘/add_faces_in_bulk’```:  
User needs to upload a ZIP file through a post request.
The zip file must be atmost 2 levels deep, and every image must be
inside a subfolder with a name of the person whose images are inside the folder.
This zip file is unzipped, stored in a unique folder in /static folder, and then the files loaded onto the database.
    
    Input JSON format:
    ```
    {  
        ‘file’: <ZipFile>,    
    }
    ```

4. ```‘/search_faces’```:   
Route to send a POST request to search the database using an
image.

    Input JSON format:
    ```
    {
        ‘image’: <ImageObject>,
        ‘k’: <K parameter as int’,
        ‘confidence’: < A number between 0 and 1>
    }
    ```  
    Returns results in a JSON object.
Note that if less than K images are found in the database for the given
confidence level, then only those many images are returned. The user should
thus lower the confidence level to get more images.

5. ```‘/get_face_info’```:   
Route to get metadata of the image with a id ‘id’
Send a POST request as a form.
    Input JSON Format:
    ```
    {
        ‘id’:<image ID in database>
    }
    ```     
    Returns image metadata(if added) and the image path. If metadata other than name is not set, null is returned corresponding to that field.

6. ```‘/set_face_info’```:   
Route to set metadata of the image. Note that name can only be
set while uploading the image to the database. Other metadata, which are date,
location, and version of the image can only be added separately here through
this route.
Metadata can only be set once.
    Input JSON format:
    ```
    {
        ‘id’: <ID of image>,
        ‘date’: <Date as String>
        ‘version’: <Version as String>,
        ‘location’: <Location as String>
    }
    ```

## Run the program
This program was developed using python 3.9.1

- First, install requirements by: ```pip install -r requirements.txt```
- Create a database called ‘face_api’ in your postgresql database.
- In main.py, set postgresql URI(change password and username to your configuration in
the provided URI)
- Run the server by ```flask run``` command. Server will be hosted at http://localhost:5000.

Interactively testing the program:
- To try out the program, html templates have been given in /templates for easy hands-on
usage of the program.
- Go to http://localhost:5000
- The page will show links to the various endpoints.
- Click the links and interact with the application.

Note: This project was a part of the course CS305 @IIT Ropar
