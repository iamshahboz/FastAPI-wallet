#### Megafon wallet

#### Installation

1) clone the repository 
```bash
git clone https://github.com/iamshahboz/FastAPI-wallet.git
```

2) create virtual environment and activate it. This is for Windows.
The given approach is different for Linux, MacOS
```bash
python -m venv env
```

```bash
env\Scripts\activate
```

3) install the required packages 
```bash
python -m pip install -r requirements.txt
```

4) You should have PostgreSQL and MySQL installed and running locally

#### Run the project

1) Change the directory
```bash
cd Megafon_wallet
```

2)
```bash
uvicorn main:app --reload
```

3) in your browser go to 
```bash
http://127.0.0.1/docs
```

##### Copyright Megafon Tajikistan