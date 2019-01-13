#!/usr/bin/python

#import
import os #global
from StringIO import StringIO #some kind of temp file storage
from flask import (  #web framework
    Flask,
    render_template,
    send_from_directory,
    send_file,
    request,
    redirect,
    url_for,
    request,
    session,
    Response,
)
from flask_sessionstore import Session #server side storage
from escpos.printer import Usb #printer driver
from cairosvg import svg2png    #svg to bitmap
#from re import re #regex

#config 
print_width = 384           # image = 384 x 175  -- print area =  384 x 154 
print_height = 154
print_spacing = 175-154

# create flask app
#SESSION_TYPE = 'redis'

app = Flask(__name__)
app.config.from_object(__name__)

#app.secret_key = '4334fdsergsFGSDfsdfgSgfdsgsdsresgdsSERE'.encode('utf8')
app.secret_key = os.urandom(24)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app) #server side storage config 


# return css static files
@app.route('/Semantic-UI-CSS/<path:path>')
def send_js(path):
    return send_from_directory('Semantic-UI-CSS', path)

# return a label svg template from collection 
@app.route('/svgtemplate/<path:path>')
def send_label(path):
    return send_from_directory('templates/labels', path)


# index page
@app.route('/')
def do_index():
   return redirect(url_for('do_choose')) #redirect to choose


# choose page
@app.route('/choose')
def do_choose():
    labels = os.listdir('templates/labels') #read all files
    return render_template('choose.html', labels = labels)

# select page
@app.route('/edit', methods=['GET'])
def do_edit():
   
    print(request.args['labelsvg'] ) 
    try:
        if  request.args['labelsvg'] != "":
            session['labelsvg'] = request.args['labelsvg']
            return render_template('edit.html')
        else:
            return redirect(url_for('do_choose')) #redirect to choose

    except Exception as e:
        print(str(e))
        return redirect(url_for('do_choose')) #redirect to choose
    

# preview page
@app.route('/preview', methods=['POST'])
def do_preview():

    session['txt1'] = request.form['txt1']
    session['txt2'] = request.form['txt2']
    session['txt3'] = request.form['txt3']
    session['txt4'] = request.form['txt4']

    return render_template('edit.html')

# resize svg according to printer label size
def svg_resize (srcsvg):
    destsvg=srcsvg
    return destsvg



# return svg image
@app.route('/prev_img_svg')
def send_preview_img():
	#label template engine
    try:
        session['svg'] = render_template("labels/"+session['labelsvg'],txt1 =session['txt1'], txt2 =session['txt2'],txt3 =session['txt3'],txt4 =session['txt4'],) #template
        session['svg'] = svg_resize(session['svg']) #resize svg image
    except Exception as e:
        print(str(e))
    return Response(session['svg'],mimetype='image/svg+xml')

# paper forward
@app.route('/forward', methods=['GET'])
def do_forward():
    try:
        nrpx = int(request.args['nrpx'])                        # read get param and convert to integer
        svg='<svg width="300" height="'+str(nrpx)+'"></svg>'    # create blank svg according to param
        svg_to_printer(svg) #sent to printer                    # print that svg
        return 'ok'
    except Exception as e:
        return 'error'

# print image
@app.route('/print')
def do_print():
    svg_to_printer(session['svg'])
    return render_template('edit.html')

def svg_to_printer(svg):
     #config printer
    p = Usb(0x4b43, 0x3538,0 ,0xB2, 0x02  )
    #   lsus
    #   lsusb -vvv -d 4b43:3538"b
    #   sudo usermod -a -G dialout user
    #   sudo usermod -a -G tty user
    #   sudo usermod -a -G lp user
    #   ls -la /dev/usb/
    
    # escape svg
    tofile("svg_to_print1.svg",svg)
    svg = svg.decode('utf-8').encode('ascii') # todo: problem with special char are used, find othern way to do that.
    tofile("svg_to_print2.svg",svg)

    # image = 384 x 175  -- print area =  384 x 154 
    pngfile = StringIO() #temp file
    pngbuffer = svg2png(bytestring=svg, dpi=171, write_to=pngfile) #SVG to PNG
    pngbuffer = svg2png(bytestring=svg, dpi=171, write_to="label.png") #SVG to PNG
    p.image(pngfile) #PNG to printer

    return render_template('edit.html')



def tofile(filename,content):
    text_file = open(filename, "w")
    text_file.write(content)
    text_file.close()
