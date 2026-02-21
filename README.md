# Biometry — Local Biometric Identity Service

Biometry is a modular real-time face recognition system designed as a **background authentication service**, not just a GUI application.

Instead of embedding recognition logic inside an interface, the system runs continuously and exposes identity information through an API so multiple applications can use it simultaneously.

---

## Key Idea

The camera observes reality once.
The service decides identity once.
Any application can ask *who is present*.

---

## Features

* Real-time face recognition (DeepFace embeddings + cosine similarity)
* Identity stabilization tracker (prevents flicker)
* Automatic camera detection & reconnection
* Local REST API using FastAPI
* Persistent embedding database
* Enroll / remove users dynamically
* Service health monitoring (`/status` endpoint)

---

## Architecture

The system is layered to separate perception from interface:

Camera Worker
→ continuously captures frames

Recognition Worker
→ generates embeddings and compares identities

Tracker
→ stabilizes recognition across time

State
→ stores current identity

FastAPI Service
→ exposes identity to external applications

```
Camera → Recognition → Tracker → State → API → Clients
```

No recognition occurs inside API routes.

---

## API Endpoints

| Endpoint    | Purpose                  |
| ----------- | ------------------------ |
| `/identity` | Current detected person  |
| `/users`    | List enrolled identities |
| `/status`   | Service health & uptime  |
| `/enroll`   | Add new identity         |
| `/delete`   | Remove identity          |

---

## Running the Service

### 1) Create environment

```bash
conda create -n face_bio python=3.10
conda activate face_bio
pip install -r requirements.txt
```

### 2) Start server

```bash
python -m uvicorn service.main:app --reload
```

Open in browser:

```
http://127.0.0.1:8000/docs
```

---

## Project Goal

This project is not just face recognition —
it aims to act as a **local identity layer** that other software can rely on.

Future applications may include:

* desktop login
* attendance logging
* automation triggers
* smart environment control

---

## Privacy

All biometric data stays local.
No images are uploaded or stored remotely.

---

## License

MIT License
