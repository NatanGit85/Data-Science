#!/bin/bash
# Tente ativar o ambiente virtual (se aplicável)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Execute o Gunicorn
gunicorn scriptdash:server --workers 1


