# PythonAnywhere WSGI Configuration
# ==================================
# INSTRUÇÕES DE DEPLOY:
#
# 1. Crie uma conta em pythonanywhere.com
# 2. Vá em "Consoles" → "Bash" e execute:
#      cd ~
#      git clone https://github.com/rcastrogi/ponto.git
#      cd ponto
#      mkvirtualenv --python=/usr/bin/python3.10 ponto
#      pip install -r requirements.txt
#
# 3. Vá em "Web" → "Add a new web app"
#      - Choose: Manual configuration
#      - Python version: 3.10
#
# 4. Na seção "Code":
#      - Source code: /home/SEU_USUARIO/ponto
#      - Working directory: /home/SEU_USUARIO/ponto
#
# 5. Na seção "Virtualenv":
#      - Path: /home/SEU_USUARIO/.virtualenvs/ponto
#
# 6. Clique em "WSGI configuration file" e substitua TODO o conteúdo por:
#
#      import sys
#      import os
#
#      path = '/home/SEU_USUARIO/ponto'
#      if path not in sys.path:
#          sys.path.append(path)
#
#      os.environ['DATA_DIR'] = path
#      os.environ['SECRET_KEY'] = 'coloque-uma-chave-secreta-aqui'
#
#      from app import app as application
#
# 7. Na seção "Static files" adicione:
#      URL: /static/    Directory: /home/SEU_USUARIO/ponto/static
#
# 8. Clique em "Reload" (botão verde)
#
# 9. Acesse: https://SEU_USUARIO.pythonanywhere.com
#    Login: admin@empresa.com / admin123
#
# ==================================
# Para ATUALIZAR o código depois:
#   1. Abra um console Bash no PythonAnywhere
#   2. cd ~/ponto && git pull
#   3. Vá em "Web" → clique "Reload"
# ==================================
