"""
Run backend with HTTPS using Office dev certificates
"""
import os
import uvicorn
from pathlib import Path

if __name__ == "__main__":
    # Use Office dev certs
    cert_dir = Path.home() / '.office-addin-dev-certs'

    ssl_config = {
        'certfile': str(cert_dir / 'localhost.crt'),
        'keyfile': str(cert_dir / 'localhost.key')
    }

    port = int(os.getenv("PORT", 3001))
    print(f"🚀 Backend server starting on https://localhost:{port}")
    print(f"📊 Ready to process DCF models")
    print(f"🔒 Using SSL certificates from {cert_dir}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        ssl_certfile=ssl_config['certfile'],
        ssl_keyfile=ssl_config['keyfile']
    )
