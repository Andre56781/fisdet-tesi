import os

def create_folder_structure():
    """Crea la struttura delle cartelle necessarie"""
    paths = [
        'instance',
        'flaskr/assets/css',
        'flaskr/assets/images',
        'flaskr/dash_application/pages'
    ]
    
    for path in paths:
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, '.gitkeep'), 'w') as f:
            pass  # Crea file vuoti per mantenere le cartelle in git

if __name__ == '__main__':
    create_folder_structure()
    print("Project structure initialized!")