from flask import Flask,render_template,request
from bs4 import BeautifulSoup as bs  #Beautiful Soup uses a pluggable XML or HTML parser to parse a (possibly invalid) document into a tree representation. Beautiful Soup provides methods and Pythonic idioms that make it easy to navigate, search, and modify the parse tree.
import requests   #Requests is an HTTP library, written in Python, for human beings. Basic GET usage:
from urllib.request import urlopen  #Open the URL url, which can be either a string or a Request object.

#  About urllib.request -> The simplest way to use this module is to call the urlopen function, which accepts a string containing a URL or a Request object (described below). It opens the URL and returns the results as file-like object; the returned object has some extra methods described below.
import json
app=Flask(__name__) # initializing a flask app

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/result")
def result():
    return render_template("result.html")

@app.route("/review",methods=['POST','GET'])   # route to show the review comments in a web UI
def index():
    if request.method =='POST':
        try:
            searchString=request.form['content'].replace(" ","")
            flipkart_url="https://www.flipkart.com/search?q="+searchString
            uClient=urlopen(flipkart_url)
            flipkartPage=uClient.read() # it read all the html for that page
            uClient.close()
            flipkart_html=bs(flipkartPage, "html.parser") # make easy navigation and search
            bigBoxes=flipkart_html.findAll('div',{"class" : "_1AtVbE col-12-12"})
            # now we target the those div which come inside the div having class==_1AtVbE col-12-12 
            del bigBoxes[0:3] # we delete first 3 element beacause they dont have 
            box=bigBoxes[0]
            productLink="https://www.flipkart.com"+ box.div.div.div.a['href']
            prodRes=requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes=prod_html.find_all("div",{"class":"_16PBlm"})

            filename=searchString +".json"
            fw=open(filename,"w")
            reviews=[]
            for commentbox in commentboxes:
                try:
                    name=commentbox.div.div.find_all('p',{"class":"_2sc7ZR _2V5EHH"})[0].text                    
                except:
                    name='No Name'
                try:
                    rating=commentbox.div.div.div.div.text 
                except:
                    rating="No Rating"
                try:
                    commentHead=commentbox.div.div.div.p.text
                except:
                    commentHead="No Comment Heading"
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e) 
                
                mydict={
                    "Product":searchString,
                    "Name":name,
                    "Rating":rating,
                    "CommentHead":commentHead,
                    "Comment":custComment
                }
                reviews.append(mydict)
            json.dump(reviews,fw, indent=4)
            # The json.dump() function is used to write the list into the file in JSON format. If the file doesn’t exist, it will be created. If it does exist, this will overwrite the existing file.
            # Please note that the data will be written in a single line in the file without the indent parameter
            return render_template("result.html",reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
                                                            
    else:
        return render_template("index.html")


if __name__=="__main__":
    app.run(debug=True)