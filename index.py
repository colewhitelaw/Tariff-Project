from app import app

# Create a server variable for Vercel
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True) 