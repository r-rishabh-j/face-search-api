import face_recognition
import numpy as np

class FaceProcessing:
    """
    Used for performing basic operation of face images
    """
    def getFaceEncoding(self, image):
        """
        Get face encoding
        """
        img = face_recognition.load_image_file(image)
        return face_recognition.face_encodings(img)

    def getByteEncoding(self, image):
        """
        Get byte encoding of the face
        """
        img = face_recognition.load_image_file(image)
        encoding = np.array(face_recognition.face_encodings(img),)
        num_faces = encoding.shape[0]
        enc_bytes = encoding.tobytes()
        return enc_bytes, num_faces
    
    def compare(self, known_encodings, unkown_encodings, tolerance):
        """
        Compare faces with tolerance
        """
        _known_encodings = [known for known in known_encodings]
        for unknown_face in unkown_encodings:
            comparision = face_recognition.compare_faces(_known_encodings, unknown_face, tolerance=tolerance)
            distance = face_recognition.face_distance(_known_encodings, unknown_face)
            for face, res in enumerate(comparision):
                if res:
                    return True, distance[face]
        return False, 1 
                    
        