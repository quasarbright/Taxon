from appJar import gui
import subprocess, re, sys, os, shutil, retrain, label_image, webbrowser
THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))
defaultSize = '378x265'

#============================== general purpose functions ======================
def relPath(f):
    '''returns absolute path of relative path f (can contain '/' but not '\\')'''
    f = f.split('/')
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(os.path.abspath('__file__'))
    return os.path.join(datadir, *f)
if not os.path.isdir(relPath('profiles')):
    os.mkdir(relPath('profiles'))
def runpy(f,*options):
    '''like runpy('retrain.py','-h')'''
    # if '' in f:
    #     tempf = re.sub('','',f)
    #     tempf = re.sub('\.py','\.exe',tempf)
    #     if os.path.isfile(relPath(tempf)):# if frozen
    #         return subprocess.check_output([relPath(tempf),*options]).decode('utf-8')
    if getattr(sys, 'frozen', False):
        # The application is frozen
        # f = re.sub('.py','.exe',f)
        return subprocess.check_output([sys.executable, relPath(f),*options]).decode('utf-8')
    return subprocess.check_output([sys.executable, relPath(f),*options]).decode('utf-8')
def profiles():
    return os.listdir(relPath('profiles'))
def isTrained(p):
    return os.path.isfile(relPath('profiles/{p}/output_graph.pb'.format(p=p)))
def trainedProfiles():
    ans = []
    for p in profiles():
        if isTrained(p):
            ans.append(p)
    return ans
def labeledProfiles():
    ans = []
    for p in profiles():
        if isTrained(p):
            ans.append(p + ' (trained)')
        else:
            ans.append(p)
    return ans
def train(profile,image_dir,shouldPrint=False):
    profile = relPath('profiles/'+profile)
    try:
        shutil.rmtree(relPath('profiles/'+profile+'/summaries'))
    except FileNotFoundError:
        pass
    myargs = """'--image_dir', '{image_dir}', '--output_graph', '{profile}\\output_graph.pb', '--intermediate_output_graphs_dir', '{profile}\\intermediate_out', '--output_labels', '{profile}\\output_labels.txt', '--summaries_dir', '{profile}\\summaries', '--bottleneck_dir', '{profile}\\bottleneck_dir', '--how_many_training_steps', '1000', '--model_dir', '{profile}\\model_dir'""".format(image_dir=image_dir,profile=profile)
    myargs.split(', ')
    myargs = re.sub("'",'',myargs)
    myargs = myargs.split(', ')
    retrain.myFunc(myargs)
def label(profile,image_path,shouldPrint=False,shouldParse=True):
    profile = relPath('profiles/'+profile)
    myargs = '''--graph, {profile}\\output_graph.pb, --labels={profile}\\output_labels.txt, --input_layer=Mul, --output_layer=final_result, --input_mean=128, --input_std=128, --image={image_path}'''.format(profile=profile,image_path=image_path)
    myargs = myargs.split(', ')
    ans = label_image.myFunc(myargs)
    if not shouldParse:
        return ans
    ans = re.split(r'[\n\r]+',ans)
    ans = [e.split(' ') for e in ans][:-1]
    ans = [[' '.join(e[:-1]), e[-1]] for e in ans]
    ans = [[e[0],float(e[1])] for e in ans]
    ans = ans[0]
    ans[1] = ans[1] * 100
    ans = "{ans[0]}  ({ans[1]}% confident)".format(ans=ans)
    return ans

# =============================== app-specific stuff ===========================

def createProfile(name):
    if name == '':
        print('warning: tried to create profile with empty string name')
        return None
    name = re.sub(' ','_',name)
    match = re.sub(r'\w','',name)
    if match != '':
        app.errorBox('profile name error','profile names can only contain letters, numbers, and underscores',parent=None)
        return None
    name = relPath('profiles/'+name)
    # print(name)
    try:
        os.mkdir(name)
        def mk(x):
            os.mkdir(os.path.join(name,x))
        mk('bottleneck_dir')
        mk('intermediate_out')
        mk('summaries')
        updateOptionBoxes()
    except FileExistsError:
        app.errorBox('profile already exists error','It appears a profile with that name already exists',parent=None)
def removeProfile(profile):
    if profile == '':
        print('warning: tried to remove profile with name empty string.')
        return None
    shutil.rmtree(relPath('profiles/'+profile),ignore_errors=True)
def updateOptionBoxes():
    '''updates all option boxes and list boxes after the profiles have been edited'''
    updateViewListBox()
    updateUseOptionBox()
    updateTrainOptionBox()
    updateRemoveOptionBox()

#=================================== press =====================================

def press(button):
    image_dir = ''
    image_dir_selected = False
    if button == 'add a profile':
        profile = app.stringBox('create a profile','type profile name (only letters, numbers, and "_")')
        if profile:
            createProfile(profile)
    elif button == 'view profiles':
        if len(profiles()) > 0:
            app.showSubWindow('view profiles window')
        else:
            try:
                app.errorBox('no profiles to view error',"To view your profiles, you need to have profiles. Try adding one")
            except AttributeError:
                pass
    elif button == 'remove a profile':
        if len(profiles()) > 0:
            app.showSubWindow('remove profiles window')
        else:
            try:
                app.errorBox('no profiles to remove error','There are no profiles to remove. Try adding one')
            except AttributeError:
                pass
    elif button == 'train a profile':
        if len(profiles()) > 0:
            app.showSubWindow('train profile window')
        else:
            try:
                app.errorBox('no profiles to train error','To train, you need a profile. Try adding one')
            except AttributeError:
                pass
    elif button == 'use a profile':
        if len(trainedProfiles()) > 0:
            app.showSubWindow('use profile window')
        else:
            try:
                app.errorBox('no profiles to use error',"To use a profile, you need a trained profile. Try training one. If you don't have any, try adding one")
            except AttributeError:
                pass
    elif button == 'choose image directory':
        image_dir = app.directoryBox(title='select a directory', dirName=None, parent=None)
        image_dir_selected = True
        app.openSubWindow('train profile window')
        app.setLabel('image_dir',image_dir)
        app.addButton('train',press)
    elif button == 'select an image to be labeled':
        image_path = ''
        try:
            image_path = app.openBox(title='select an image to be labeled', fileTypes=[('images', '*.png'), ('images', '*.jpg'), ('images','*.bmp'), ('images','*.gif')], parent='use profile window')
        except AttributeError:
            pass
        if image_path:
            app.setLabel('image_path',image_path)#TODO implement label.py
            profile = app.getOptionBox('use profiles option box')
            app.disableButton('select an image to be labeled')
            def whenDone(out):
                try:
                    app.infoBox('label result',out,parent="train profile window")
                except AttributeError:
                    pass
                app.enableButton('select an image to be labeled')
            app.threadCallback(label,whenDone,profile,image_path,shouldPrint=True)#TODO change to false when done
    elif button == 'train':
        profile = app.getOptionBox('train profiles option box')
        if profile == '':
            return None
        profile = re.sub(' (.*)','',profile)
        image_dir = app.getLabel('image_dir')

        if image_dir:
            app.openSubWindow('train profile window')
            app.addMessage('training msg','The neural network is training. please do not close any of the applcation windows or shut down your computer. If it is the first time training this profile, it could take over 30 minutes. Otherwise, it should take about 1-5 minutes')
            app.disableButton('train')
            def whenDone(*args):
                app.setMessage('training msg','')
                try:
                    app.infoBox('training done','training complete',parent="train profile window")
                except AttributeError:
                    pass
                app.enableButton('train')
                app.hideSubWindow('train profile window')
                updateOptionBoxes()
            app.threadCallback(train,whenDone,profile,image_dir,shouldPrint=True)
    elif button == 'remove':
        profile = app.getOptionBox('remove profiles option box')
        if profile == '':
            return None
        if profile:
            profile = re.sub(' (.*)','',profile)
            removeProfile(profile)
        updateOptionBoxes()#TODO thread callback for deleting trained profiles
    elif button == 'help':
        webbrowser.open('https://quasarbright.github.io/Taxon')

#============================== main window ====================================

app = gui('Taxon',defaultSize)
app.setIcon(relPath('MISTER-BRAINWASH.ico'))
buttons = [
    ['add a profile','view profiles'],
    ['train a profile','use a profile'],
    ['remove a profile'],
    ['help']
]
for row in buttons:
    app.addButtons(row,press)


#============================= train a profile =================================

app.startSubWindow('train profile window',title="train",modal=True)
app.setSticky('ew')
app.startLabelFrame('select profile to train')
app.setSticky('ew')
def updateTrainOptionBox():
    arr = profiles()
    if not arr:
        arr = ['']
    app.changeOptionBox('train profiles option box',arr)
app.addOptionBox('train profiles option box',profiles())
app.stopLabelFrame()
app.setSticky('')
app.setSize(defaultSize)
app.addButton('choose image directory',press)
app.addLabel('image_dir','')
app.stopSubWindow()

#============================= use a profile ===================================

app.startSubWindow('use profile window',title='use',modal=True)
app.setSticky('ew')
app.startLabelFrame('select profile to use')
app.setSticky('ew')
def updateUseOptionBox():
    arr = trainedProfiles()
    if not arr:
        arr = ['']
    app.changeOptionBox('use profiles option box',arr)
app.addOptionBox('use profiles option box',trainedProfiles())
app.stopLabelFrame()
app.setSticky('')
app.addButton('select an image to be labeled',press)
app.addLabel('image_path','')
app.setSize(defaultSize)
app.stopSubWindow()

#============================= view profiles ===================================

app.startSubWindow('view profiles window',title='view',modal=False)
app.setSize(defaultSize)
app.setPadding([20,20])
app.startScrollPane('view profiles scroll pane')
def updateViewListBox():
    arr = labeledProfiles()
    if not arr:
        arr = ['']
    app.updateListBox('view profiles list box',arr)
app.addListBox('view profiles list box',labeledProfiles())
app.stopScrollPane()
app.stopSubWindow()

#============================= remove profiles ===================================

app.startSubWindow('remove profiles window',title='remove',modal=True)
app.setSize(defaultSize)
app.setSticky('ew')
app.startLabelFrame('select profile to remove')
app.setSticky('ew')
def updateRemoveOptionBox():
    arr = profiles()
    if not arr:
        arr = ['']
    app.changeOptionBox('remove profiles option box',arr)
arr = profiles()
if not arr:
    arr = ['']
app.addOptionBox('remove profiles option box',arr)
app.stopLabelFrame()
app.setSticky('')
app.addButton('remove',press)
app.stopSubWindow()


app.go()
