# SHIBAINU @ UC HACKFEST 2026

## Quick Commands

0. Concurrent Running

    ```bash
    (cd frontend && bun dev) & (cd backend && fastapi dev)
    ```

1. Frontend

    ```bash
    bun dev
    ```

2. Backend

- Dependencies Update:

    ```bash
    pip freeze > requirements.txt
    ```

- Runnning the project:

```bash
fastapi dev
```

## CROSSCHECK LAGII

1. cleaner.py nanti polish lagi biar lebih akurat
2. embedder predict category kurang detail, predict urgency worse masih if-else clause, cek generateEmbedding juga
3. recomputeCluster()
4. generateBrief harus connect ke AI-side nunggu athilluy
5. tambahin di reference service data provinsi dan regency di Indonesia.
6. Lengkapin category di reference service
