#import libraries needed 
from flask import Flask, render_template, url_for, redirect, request, flash, session, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, DataRequired
from flaskext.mysql import MySQL
#import GEOparse 
import numpy as np
import pandas as pd
import re
import io
import base64
#import seaborn as sns
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#import matplotlib.pyplot as plt
#from matplotlib.figure import Figure


# create a flask application object
app = Flask(__name__)



# we need to set a secret key attribute for secure forms
app.config['SECRET_KEY'] = 'catherine'

#Connecting to the MySQL database where all the tf details are stored
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Catherine2021'
app.config['MYSQL_DATABASE_DB'] = 'transfacts'


#Creating an instance which will provide access 
mysql = MySQL(app)
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


#HOME PAGE

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f))

    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('family', family_name = transcr_f))
    return render_template('index_page.html')




#PROTEINS PAGE


@app.route('/proteins', methods=['GET', 'POST'])
def proteins():
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f))
    cursor.execute("SELECT gene_name, protein_name, uniprot_ID, location, family \
                            from Transcr_f")                                
    conn.commit()
    data = cursor.fetchall()
    return render_template('proteins.html', data=data)


@app.route('/protein/<protein_name>', methods=['GET', 'POST'])
def protein(protein_name):   
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f))
    transcr_f = protein_name
    # search by uniprotID or name
    cursor.execute("SELECT uniprot_ID, gene_name, protein_name, family, location, link\
                        from Transcr_f \
                        WHERE protein_name LIKE %s OR gene_name LIKE %s OR uniprot_ID LIKE %s", (transcr_f, transcr_f, transcr_f))
    conn.commit()
    data_tf = cursor.fetchall()
    cursor.execute("SELECT Target.target_name, Target.interaction, Target.tf_uniprot_ID \
                        from Transcr_f \
                        LEFT JOIN Target ON Target.tf_name = Transcr_f.gene_name \
                         WHERE Transcr_f.protein_name LIKE %s OR Transcr_f.uniprot_ID LIKE %s OR Transcr_f.gene_name LIKE %s", (transcr_f, transcr_f, transcr_f))
    conn.commit()
    data_target = cursor.fetchall()

    cursor.execute("SELECT Interaction.drug_ID, Drugs.drug_name \
                        from Transcr_f \
                        LEFT JOIN Interaction ON Interaction.uniprot_ID = Transcr_f.uniprot_ID \
                        LEFT JOIN Drugs ON Drugs.drug_ID = Interaction.drug_ID \
                        WHERE Transcr_f.protein_name LIKE %s OR Transcr_f.uniprot_ID LIKE %s", (transcr_f, transcr_f))
    conn.commit()
    data_dr = cursor.fetchall()
    return render_template('protein_view.html', data_tf=data_tf, data_dr=data_dr, protein_name=protein_name, data_target= data_target)






#FAMILY PAGES

@app.route('/families', methods=['GET', 'POST'])
def protein_families():
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f)) 

    cursor.execute("SELECT DISTINCT Family, COUNT(family) AS TFcount  \
                        from Transcr_f \
                        GROUP BY family" )                 
    conn.commit()
    fam = cursor.fetchall()
    

    return render_template('families.html', fam=fam)



@app.route('/families/<family_name>', methods=['GET', 'POST'])
def family(family_name):
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f)) 
    transcr_f = family_name
    # search by uniprotID or name
    cursor.execute("SELECT  family, uniprot_ID, gene_name, protein_name \
                        from Transcr_f \
                        WHERE family LIKE %s ", (transcr_f))
    conn.commit()
    data_fam = cursor.fetchall()
    return render_template('family_view.html', data_fam=data_fam, family_name=family_name)





#DRUG PAGES
@app.route('/drugs', methods=['GET', 'POST'])
def drugs():
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f))
    cursor.execute("SELECT drug_name, drug_ID \
                    from Drugs" )                 
    conn.commit()
    drug = cursor.fetchall()
    return render_template('drugs.html', drug=drug)


#DRUG PAGES
@app.route('/drugs/<drug_name>', methods=['GET', 'POST'])
def drug1(drug_name):
    if request.method == "POST":
        transcr_f = request.form['transcr_f']
        return redirect(url_for('protein', protein_name = transcr_f))
    transcr_f = drug_name
    cursor.execute("SELECT drug_ID, drug_name, description \
                    FROM Drugs \
                    WHERE drug_ID LIKE %s OR drug_name LIKE %s", (transcr_f, transcr_f))
    conn.commit()
    drug_details = cursor.fetchall()
    # search by uniprotID or name
    cursor.execute("SELECT Transcr_f.uniprot_ID, Transcr_f.gene_name, Transcr_f.protein_name, Transcr_f.family \
                    FROM Drugs \
                    LEFT JOIN Interaction ON Interaction.drug_ID = Drugs.drug_ID \
                    LEFT JOIN Transcr_f ON Transcr_f.uniprot_ID = Interaction.uniprot_ID \
                    WHERE Drugs.drug_name LIKE %s OR Drugs.drug_ID LIKE %s", (transcr_f, transcr_f))
    conn.commit()
    data_drug = cursor.fetchall()
    return render_template('drug_view.html', drug_details=drug_details, data_drug=data_drug, drug_name=drug_name)



        




#UPLOAD GEO
@app.route('/upload', methods =('GET', 'POST'))
def upload():
    '''Function to take GDS ID and output GDS object'''
    if request.method == "POST": 
        if request.form.get('gds') != None:
            GDS_name = request.form['gds']
            gds = GEOparse.get_GEO(geo = str(GDS_name), destdir="./")
            title = gds.metadata['title']
            description = gds.metadata['description']
            session['gdsname'] = GDS_name
            return render_template('GDS_datasets.html' , title = title, description = description)
        else:        
            transcr_f = request.form['transcr_f']
            return redirect(url_for('protein', protein_name = transcr_f)) 
    return render_template('upload.html')


@app.route('/plot_tfdist')
def plot_tfdist():
    """produces distribution graph for TFs and prints table shape"""
    GDS_name = session['gdsname']
    gds = GEOparse.get_GEO(geo = str(GDS_name), destdir="./")
    gdstable = gds.table
    gdstable = gdstable.set_index('IDENTIFIER')
    gdstable = gdstable.groupby(['IDENTIFIER']).mean()
    allidentifiers = gdstable.index.tolist()
    #butactualallidentifiers = identifiers in gds table

    cursor.execute("SELECT GROUP_CONCAT(gene_name) \
                        from Transcr_f")
    conn.commit()
    tfs = str(cursor.fetchall())
    tfs = tfs.split(',')

    cursor.execute("SELECT DISTINCT GROUP_CONCAT(target_name) \
                        from Target")
    conn.commit()
    targs = str(cursor.fetchall())
    targs = targs.split(',')

    #list_ofactualgenes = TF genes in gdstable after cross referenced 
    #list_ofactualtargs = target genes in gdstable after cross referenced 
    
    gdstable['Mean'] = gdstable.mean(axis = 1)
    gdstable['S.D.'] = gdstable.std(axis = 1)
    gdstable_targ = gdstable.copy()
    gdstable = gdstable[gdstable.index.isin(tfs)]
    gdstable_targ = gdstable_targ[gdstable_targ.index.isin(targs)]
    
    meandf=gdstable['Mean'].dropna()


    #gdstable, gdstable_targ = prep(gds)
    #meandf=gdstable['Mean'].dropna()
    fig,ax=plt.subplots(figsize=(6,6))
    ax=sns.set_style(style="darkgrid")
    sns.distplot(meandf)
    canvas=FigureCanvas(fig)
    img=io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='img/png')

@app.route('/plot_corr')
def plot_corr():
    """produces distribution graph for TFs and prints table shape"""
    GDS_name = session['gdsname']
    gds = GEOparse.get_GEO(geo = str(GDS_name), destdir="./")
    gdstable = gds.table
    gdstable = gdstable.set_index('IDENTIFIER')
    gdstable = gdstable.groupby(['IDENTIFIER']).mean()
    fig,ax=plt.subplots(figsize=(6,6))
    ax=sns.set_style(style="darkgrid")
    sns.heatmap(gdstable.corr(), cmap="YlGnBu", annot=True) 
    canvas=FigureCanvas(fig)
    img=io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='img/png')


@app.route('/plot_hist')
def plot_hist():
    """produces distribution graph for TFs and prints table shape"""
    GDS_name = session['gdsname']
    gds = GEOparse.get_GEO(geo = str(GDS_name), destdir="./")
    gdstable = gds.table
    gdstable = gdstable.set_index('IDENTIFIER')
    gdstable = gdstable.groupby(['IDENTIFIER']).mean()
    gse_name = gds.metadata['reference_series']
    gse = GEOparse.get_GEO(geo=gse_name[0], destdir = '../')
    pDat = unique(gse)
    df = gdstable.merge(pDat, how = 'left', left_index=True, right_index = True)
    fig,ax=plt.subplots(figsize=(6,6))
    plt.bar()
    canvas=FigureCanvas(fig)
    img=io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='img/png')

def unique(gse):
    pDat = gse.phenotype_data
    title = pDat['title'].tolist()
    d_status = []
    for x in range(0, len(title)):
        i = title[x].split(' ')
        i.pop()
        i = '_'.join(i)
        d_status.append(i)
    pDat['title']=d_status
    pDat = pd.DataFrame(pDat['title'])
    return pDat

# start the web server
if __name__ == '__main__':
    app.run(debug=True)