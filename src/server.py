from app import create_app

app = create_app()
server = app.server

if __name__ == "__main__":
    #app.run_server(host='0.0.0.0', debug=True, port=8050)
    app.run(host='0.0.0.0', debug=True, port=8050)