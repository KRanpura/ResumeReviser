<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Crimson+Pro&family=Literata" rel="stylesheet">

<div align=center>


<div style="text-align: center; background: ; width:300px;">
    <img src="imgs/magic_resume_dark.png" alt="Logo"  width="300" height="300">
<h1 style="color:black;font-family:'Crimson Pro'">ResumeReviser</h1>
</div>

</div>

**An automated tool that helps revise and review resumes while offering tips based on job descriptions!**

<p align="center">
<i>Built for HackPrinceton Fall 2023</i>
<p>

![hackprinceton banner](imgs/hackprinceton_banner.png)

<div align="center">

## How to install

</div>

Follow these steps to set up the environment and run the application.
1. If you are *not* an author, fork the repository [here](https://github.com/KRanpura/ResumeReviser/fork).
2. Clone the repository.
```bash
    git clone https://github.com/KRanpura/ResumeReviser
```
3. Create the python virtual environment.
- Either use vscode or using [virtualenv](https://learnpython.com/blog/how-to-use-virtualenv-python/):
```bash
virtual env 
```
- **OR**
```bash
python -m venv env
```
4. Activate the Virtual Environment (Not necessary for vscode).

- On Windows.

```bash
env\Scripts\activate
```

- On macOS and Linux.

```bash
source env/bin/activate
```

5. Install Dependencies
```bash
pip install -r requirements.txt
```
- Make sure your pip version is up-to-date:

```bash
pip install --upgrade pip
```

6. Run the app
```bash
cd flask
python -m flask run
```

### Technologies
- Flask
- Python
- Sqlite3
- SQL
- Bootstrap
