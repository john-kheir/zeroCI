import os 
os.chdir(os.path.join(os.path.abspath("."), "backend"))

from zero_ci import app

if __name__ == "__main__":
    app.run()
