del /f /q dist\*
C:\Users\ricoi\PycharmProjects\Discord_tools\.venv\Scripts\python.exe -m pip install -r requirements.txt
C:\Users\ricoi\PycharmProjects\Discord_tools\.venv\Scripts\python.exe -m build
C:\Users\ricoi\PycharmProjects\Discord_tools\.venv\Scripts\python.exe -m twine upload .\dist\*