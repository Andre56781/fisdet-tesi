from flaskr import create_app

# Crea l'app Flask
app = create_app()

if __name__ == "__main__":
    # Avvia l'app Flask in modalità debug
    app.run(debug=True)
