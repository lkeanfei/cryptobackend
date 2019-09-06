import os, shutil
import gzip

currentDir = os.path.dirname(os.path.abspath(__file__))

# Remove all files in current css and js folders

currentCSSFiles = os.listdir(currentDir + "/static/css")
currentJSFiles = os.listdir(currentDir + "/static/js")

for css in currentCSSFiles:
    os.remove(currentDir + "/static/css/" + css)

for js in currentJSFiles:
    os.remove(currentDir + "/static/js/" + js)

# Remove html file from templates folder
if os.path.exists(currentDir + "/templates/index.html"):
    os.remove(currentDir + "/templates/index.html")

# Copy from react

laptopMachinePath = 'D:/crypto-react/build/'
homeMachinePath = 'C:/crypto-react/build/'
reactBuildPath = ''

if os.path.exists(laptopMachinePath):
    reactBuildPath = laptopMachinePath
elif os.path.exists(homeMachinePath):
    reactBuildPath = homeMachinePath

# Copy index.html from react build
shutil.copy(reactBuildPath + "/index.html" , currentDir + "/analysis/templates/")

sourceJSFiles = os.listdir(reactBuildPath + "/static/js")
for sourceJSScript in sourceJSFiles:

    if ".js.map" not in sourceJSScript:
        with open(reactBuildPath + "/static/js/" + sourceJSScript, 'rb') as f_in:
            with gzip.open(currentDir + "/static/js/" + sourceJSScript + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        shutil.copy(reactBuildPath + "/static/js/" + sourceJSScript , currentDir + "/static/js/")

sourceCSSFiles = os.listdir(reactBuildPath + "/static/css")

for sourceCSSFile in sourceCSSFiles:
    if ".css.map" not in sourceCSSFile:
        shutil.copy(reactBuildPath + "/static/css/" + sourceCSSFile , currentDir + "/static/css/")
    print(sourceCSSFile)




print(reactBuildPath)