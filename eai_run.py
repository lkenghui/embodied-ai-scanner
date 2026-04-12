import uvicorn
import os
from backend.database import init_db

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.api:app", host="0.0.0.0", port=port, reload=False)
