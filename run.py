import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print("  SISTEMA DE GESTÃO PECUÁRIA - FAZENDA MODELO")
    print("  Iniciando servidor web em http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)

