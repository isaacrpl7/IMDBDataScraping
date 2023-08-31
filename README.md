# About the project
This is a project that scrapes data from TV Series (not movies) on IMDB. The main goal is to provide an API to my other project that is the Front-End, showing
a comparison between ratings of each episode from each season of a tv serie. It uses Flask to provide the API and a multithread approach is used in order
to speed the scraper by fetching pages concurrently.

## Set virtual env
If you choose to work on this project, it is recommended that you configure a virtual environment on your pc. With python installed (preferably version 3.8), follow the next steps:

To create virtual env in linux:
```
python -m venv env
```

To create virtual env in Windows:
```
python -m venv c:\path\to\env
```

To access virtual env in linux:
```
source env/bin/activate
```

To access virtual env in Windows:
```
wenv\Scripts\Activate.ps1
```

If you're using windows powershell on vscode, and get UnauthorizedAccess error, please run:
```
Set-ExecutionPolicy Unrestricted -Scope Process
```
before entering the virtual env. After that, you can run:
```
Set-ExecutionPolicy Default -Scope Process
```
to avoid any potential issues.