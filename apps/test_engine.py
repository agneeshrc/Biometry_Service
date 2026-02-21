from engine.embedder import get_embedding
from engine.recognizer import recognize

emb = get_embedding("test_images/test1.jpg")
result = recognize(emb)

print(result)
