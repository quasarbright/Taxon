from appJar import gui
import subprocess
import re, sys, os, shutil
THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))
defaultSize = '378x265'
#now cx freeze
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
    '''like runpy('tensorflow/retrain.py','-h')'''
    # if 'tensorflow/' in f:
    #     tempf = re.sub('tensorflow/','',f)
    #     tempf = re.sub('\.py','\.exe',tempf)
    #     if os.path.isfile(relPath(tempf)):# if frozen
    #         return subprocess.check_output([relPath(tempf),*options]).decode('utf-8')
    return subprocess.check_output([sys.executable, relPath(f),*options]).decode('utf-8')
def profiles():
    return os.listdir(relPath('profiles'))
def trainedProfiles():
    ans = []
    for p in profiles():
        output_graph = os.path.isfile(relPath('profiles/{p}/output_graph.pb'.format(p=p)))
        if output_graph:
            ans.append(p)
    return ans
def train(profile,image_dir,shouldPrint=False):
    profile = relPath('profiles/'+profile)
    shutil.rmtree(relPath('profiles/'+profile+'/summaries'))
    myargs = """'--image_dir', '{image_dir}', '--output_graph', '{profile}\\output_graph.pb', '--intermediate_output_graphs_dir', '{profile}\\intermediate_out', '--output_labels', '{profile}\\output_labels.txt', '--summaries_dir', '{profile}\\summaries', '--bottleneck_dir', '{profile}\\bottleneck_dir', '--how_many_training_steps', '1000', '--model_dir', '{profile}\\model_dir'""".format(image_dir=image_dir,profile=profile)
    myargs.split(', ')
    myargs = re.sub("'",'',myargs)
    myargs = myargs.split(', ')
    # print(myargs)
    # sys.exit()
    if shouldPrint:
        print(runpy('tensorflow/retrain.py',*myargs))
    else:
        runpy('tensorflow/retrain.py',*myargs)
    return None
def label(profile,image_path,shouldPrint=False,shouldParse=True):
    profile = relPath('profiles/'+profile)
    myargs = '''--graph, {profile}\\output_graph.pb, --labels={profile}\\output_labels.txt, --input_layer=Mul, --output_layer=final_result, --input_mean=128, --input_std=128, --image={image_path}'''.format(profile=profile,image_path=image_path)
    myargs = myargs.split(', ')
    ans = runpy('tensorflow/label_image.py',*myargs)
    if not shouldParse:
        if shouldPrint:
            print(ans)
        return ans
    ans = re.split(r'[\n\r]+',ans)
    ans = [e.split(' ') for e in ans][:-1]
    ans = [[' '.join(e[:-1]), e[-1]] for e in ans]
    ans = [[e[0],float(e[1])] for e in ans]
    ans = ans[0]
    ans[1] = ans[1] * 100
    ans = "{ans[0]}  ({ans[1]}% confident)".format(ans=ans)

    if shouldPrint:
        print(ans)
    return ans
# print(train('flowers','D:\\code\\flower_neural_network\\flower_photos'))
# sys.exit()
# =============================== app-specific stuff ===========================

def createProfile(name):
    name = re.sub(' ','_',name)
    match = re.sub(r'\w','',name)
    if match != '':
        try:
            app.errorBox('profile name error','profile names can only contain letters, numbers, and underscores',parent='add profile window')
        except AttributeError:
            pass
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
        app.hideSubWindow('add profile window')
    except FileExistsError:
        try:
            app.errorBox('profile already exists error','It appears a profile with that name already exists',parent='add profile window')
        except AttributeError:
            pass
        app.openSubWindow('add profile window')
        return False

#=================================== main gui ==================================

def press(button):
    image_dir = ''
    image_dir_selected = False
    if button == 'create':
        createProfile(app.getEntry('profile name'))
    elif button == 'add a profile':
        app.showSubWindow('add profile window')
        app.setFocus('profile name')
    elif button == 'view profiles':
        app.showSubWindow('view profiles window')
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
                app.errorBox('no profiles to use error','To use a profile, you need a profile. Try adding one')
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
            app.threadCallback(train,whenDone,profile,image_dir,shouldPrint=True)

#============================== main window ====================================

app = gui('Taxon',defaultSize)
app.setIcon(relPath('MISTER-BRAINWASH.ico'))
app.addButton('add a profile',press)
app.addButton('view profiles',press)
app.addButton('train a profile',press)
app.addButton('use a profile',press)
# def checkStop():
#     sys.exit()
#     return True
# app.setStopFunction(checkStop)

#=========================== create a new profile ==============================

app.startSubWindow('add profile window',title='add',modal=True)
app.setSize(defaultSize)
app.addLabelEntry("profile name")
app.addButton('create',press)
app.stopSubWindow()

#============================= train a profile =================================

app.startSubWindow('train profile window',title="train",modal=True)
app.startLabelFrame('select profile to train')
app.addOptionBox('train profiles option box',profiles())
app.stopLabelFrame()
app.setSize(defaultSize)
app.addButton('choose image directory',press)
app.addLabel('image_dir','')
app.stopSubWindow()

#============================= use a profile ===================================

app.startSubWindow('use profile window',title='use',modal=True)
app.startLabelFrame('select profile to use')
app.addOptionBox('use profiles option box',trainedProfiles())
app.stopLabelFrame()
app.addButton('select an image to be labeled',press)
app.addLabel('image_path','')
app.setSize(defaultSize)
#TODO handle profile not being trained and no profiles existing
app.stopSubWindow()

#============================= view profiles ===================================

app.startSubWindow('view profiles window',title='view',modal=True)
app.setSize(defaultSize)
app.setPadding([20,20])
app.startScrollPane('view profiles scroll pane')
app.addListBox('view profiles list box',profiles())
app.stopScrollPane()
app.stopSubWindow()
app.go()
